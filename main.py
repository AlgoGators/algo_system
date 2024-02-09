import pandas as pd
import configparser
from dotenv import load_dotenv
from pathlib import Path
from math import sqrt
import logging
import logging.config
from get_volatile_instruments import get_volatile_instruments
from get_trend_signals import get_trend_positions
from get_carry_signals import get_carry_positions
from get_optimized_positions import get_optimized_positions
from get_risk_adjusted_positions import get_risk_adjusted_positions
from get_buffered_positions import get_buffered_positions
from get_notional_exposures import get_notional_exposures
from get_held_positions import get_held_positions
from get_historical_data import Prices, SQLPull, get_most_recent_open_interest
from get_cost_estimates import get_contract_cost_estimates
from logging_handler import logging_config

# Starts logging configuration
logging.config.dictConfig(logging_config)


class GetFromCSV:
    def get_multipliers(path : str, instruments : list, symbol_column : str = 'Data Symbol', multiplier_column : str = 'Pointsize') -> dict:
        contents = pd.read_csv(path)

        multipliers = {}

        for index, row in contents.iterrows():
            symbol = row[symbol_column]
            multiplier = row[multiplier_column]

            # NaN check
            if (symbol == symbol) and (symbol in instruments):
                multipliers[symbol] = multiplier

        return multipliers

    def get_instruments(path : str, instrument_column : str= 'Data Symbol'):

        contents = pd.read_csv(path, index_col=0)

        instruments = contents[instrument_column].tolist()
        instruments.sort()

        return instruments


class ReturnMetrics:
    def get_percent_return(self, price : float, previous_price : float) -> float:
        """Returns the percentage return of the price compared to the previous price"""
        if previous_price == 0:
            return 0
        elif previous_price < 0:
            return (price - previous_price) / abs(previous_price)

        return (price - previous_price) / previous_price

    def get_instrument_returns(self, prices_df : pd.DataFrame) -> pd.DataFrame:
        """Returns the daily percentage returns of the prices DataFrame"""

        instrument_name = prices_df.columns[0]

        # requires the index to be the dates
        dates = prices_df.index.tolist()
        prices = prices_df[instrument_name].tolist()

        percent_returns = []

        for i in range(1, len(prices)):
            percent_returns.append(self.get_percent_return(prices[i], prices[i-1]))

        instrument_returns_df = pd.DataFrame(percent_returns, index=dates[1:], columns=[instrument_name])

        return instrument_returns_df

    def get_all_instruments_returns_df(self, all_prices_df : pd.DataFrame) -> pd.DataFrame:
        """Returns a DataFrame of the daily percentage returns of each instrument"""
        returns_df = pd.DataFrame()

        instruments = all_prices_df.columns.tolist()

        for instrument in instruments:
            instrument_returns = self.get_instrument_returns(all_prices_df.loc[:, [instrument]])
            
            if returns_df.empty:
                returns_df = instrument_returns
                continue

            returns_df = returns_df.join(instrument_returns, how='inner')

        return returns_df

def combine_dataframe_dicts(df_dict1 : dict, df_dict2 : dict) -> dict:
    keys = [key for key in df_dict1 if key in df_dict2.keys()]

    summed_df_dict = {}

    for key in keys:
        df1 : pd.DataFrame = df_dict1[key]
        df2 : pd.DataFrame = df_dict2[key]

        summed_df = df1.add(df2, fill_value=None)

        summed_df_dict[key] = summed_df

    return summed_df_dict

def get_most_recent_positions(positions : dict) -> dict:
    most_recent_positions = {}

    for instrument in positions.keys():
        most_recent_positions[instrument] = positions[instrument].iloc[-1]

    return most_recent_positions

#! TEMPORARY
def get_stddev_dct(df : pd.DataFrame, BUSINESS_DAYS_IN_YEAR : int) -> dict:
    instruments = df.columns.tolist()

    stddev_dct = {}

    for instrument in instruments:
        stddev_dct[instrument] = df[instrument].std() * sqrt(BUSINESS_DAYS_IN_YEAR)

    return stddev_dct

def parse_config(config_file : str):
    Config = configparser.ConfigParser()
    Config.read(config_file)

    sections = Config.sections()

    config_dict = {}

    for section in sections:
        options = Config.options(section)
        for option in options:
            # Try to eval if possible
            try:
                config_dict[option.upper()] = eval(Config.get(section, option))
            except:
                # String if not
                config_dict[option.upper()] = Config.get(section, option)

    return config_dict

def parse_environment(environment_file : str):
    load_dotenv(Path(environment_file))

def main(config_dict : dict):
    parse_environment(config_dict['ENVIRONMENT_PATH'])

    all_instruments : list = GetFromCSV.get_instruments(config_dict['INSTRUMENTS_PATH'])

    #!! removed because extreme covariances
    all_instruments.remove('ZL')

    logging.info('Getting Historical Prices')
    adj_historical_prices_df, unadj_historical_prices_df, open_interest_df = Prices.get_all_historical_prices(all_instruments)
    
    logging.info('Getting Carry Prices')
    carry_prices = SQLPull.get_carry_data(all_instruments)

    logging.info('Getting Returns')
    instrument_returns_df : pd.DataFrame = ReturnMetrics().get_all_instruments_returns_df(adj_historical_prices_df)

    instrument_weight = 1 / len(all_instruments)

    multipliers = GetFromCSV.get_multipliers(config_dict['MULTIPLIERS_PATH'], all_instruments) #? SQL pull for this

    held_positions = get_held_positions(all_instruments, 'N/A') #? SQL pull for this

    most_recent_prices = Prices.get_most_recent_prices(adj_historical_prices_df)

    notional_exposure_per_contract = get_notional_exposures(most_recent_prices, multipliers)

    costs_per_contract = get_contract_cost_estimates(all_instruments, config_dict['CONTRACT_COSTS'])

    open_interest_dct = get_most_recent_open_interest(open_interest_df=open_interest_df)

    #! NEED to figure out how we want to calculate this LT
    standard_deviation_dct = get_stddev_dct(instrument_returns_df, config_dict['BUSINESS_DAYS_IN_YEAR']) #? function for this

    instrument_weights_dct = {}
    for instrument in all_instruments:
        instrument_weights_dct[instrument] = instrument_weight

    logging.info('Getting Volatile Instruments')
    instruments = get_volatile_instruments(
        instruments=all_instruments,
        instrument_weight=instrument_weight,
        IDM=config_dict['IDM'],
        risk_target=config_dict['RISK_TARGET'],
        instrument_returns_df=instrument_returns_df,
        maximum_leverage=config_dict['MAX_LEVERAGE'])

    #? doesnt need past returns?
    logging.info('Getting trend positions')
    trend_positions = get_trend_positions(
        instruments=instruments,
        collective_adj_prices=adj_historical_prices_df,
        collective_unadj_prices=unadj_historical_prices_df,
        weights=instrument_weights_dct,
        capital=config_dict['CAPITAL'],
        #!! IDM=IDM,
        risk_target_tau=config_dict['RISK_TARGET'],
        multipliers=multipliers,
        fast_spans=config_dict['FAST_SPANS'])

    logging.info('Getting Carry Positions')
    carry_positions = get_carry_positions(
        instruments=instruments,
        weights=instrument_weights_dct,
        capital=config_dict['CAPITAL'],
        #!! IDM=IDM,
        risk_target_tau=config_dict['RISK_TARGET'],
        multipliers=multipliers,
        carry_spans=config_dict['CARRY_SPANS'],
        adjusted_prices_dict=adj_historical_prices_df,
        carry_prices_dict=carry_prices,
        unadjusted_prices_dict=unadj_historical_prices_df)

    total_positions : dict = combine_dataframe_dicts(trend_positions, carry_positions)

    total_positions = get_most_recent_positions(total_positions)

    logging.info('Optimizing Positions')
    optimized_positions = get_optimized_positions(
        held_positions=held_positions,
        ideal_positions=total_positions,
        notional_exposures_per_contract=notional_exposure_per_contract,
        capital=config_dict['CAPITAL'],
        costs_per_contract=costs_per_contract,
        returns_df=instrument_returns_df,
        risk_target=config_dict['RISK_TARGET'])
    
    quit()
    logging.info('Adjusting Positions for Risk')
    risk_adjusted_positions = get_risk_adjusted_positions(
        positions=optimized_positions,
        notional_exposure_per_contract=notional_exposure_per_contract,
        capital=config_dict['CAPITAL'],
        risk_target=config_dict['RISK_TARGET'],
        IDM=config_dict['IDM'],
        average_forecast=config_dict['AVERAGE_FORECAST'],
        open_interest_dct=open_interest_dct,
        standard_deviation_dct=standard_deviation_dct,
        instrument_weights_dct=instrument_weights_dct,
        max_forecast=config_dict['MAX_FORECAST'],
        max_position_leverage_ratio=config_dict['MAX_POSITION_LEVERAGE'],
        max_forecast_margin=config_dict['MAX_FORECAST_MARGIN'],
        max_pct_of_open_interest=config_dict['MAX_PERCENT_OF_OPEN_INTEREST'],
        instrument_returns_df=instrument_returns_df,
        max_portfolio_leverage=config_dict['MAX_PORTFOLIO_LEVERAGE'])

    logging.info('Buffering Positions')
    buffered_positions = get_buffered_positions(
        positions=risk_adjusted_positions,
        held_positions=held_positions,
        buffer_fraction=config_dict['BUFFER'])

    print(buffered_positions)
    #? what to do with buffered positions?
    


if __name__ == '__main__':
    config_dict = parse_config('config.ini')
    main(config_dict=config_dict)

"""
Proposed folder repo structure

algo_system
┝ Carry
┝ dyn_opt
┝ risk_analysis
┝ trend_following
┝ unittesting
│   ┝ data
│   │   ┝ ES.csv
│   │   ┕ ..
│   ┕ unittesting.py
┝ main.py (steps 1-8)
┝ get_instruments.py (step 1)
┝ get_trend_positions.py (step 2)
┝ get_carry_positions.py (step 3)
┝ get_optimized_positions.py (step 5)
┕ get_risk_adjusted_positions.py (step 6, 7 & 8)

steps 6 & 7 should append to a CSV if any risk limits are hit and whether it was portfolio wide or position only and what type of limit was hit (forecast, leverage, open interest)

Outline

1. Calculate list of instruments volatile enough to be traded (I)
    Iterate over list of instruments and keep if risk_analysis/risk_functions.py Volatility().minimum_volatility() is returns True
        Arguments:
            IDM : float
                ? I'd assume since dyn_opt its fair to assume the highest IDM
            instrument_weight : float
                assume equal for all instruments (unless we decide otherwise)
            risk_target : float
                0.20 unless that changes
            instrument_returns : list[float] e.g. [0.01, 0.02, -0.003]
                daily percentage returns
            maximum_leverage : float
                whatever max leverage we find acceptable 
                ? 2.0? 4.0?

        Returns True/False if instrument is volatile enough to be traded or not, respectively

2. Calculate positions as a result of trend following (Nᵀ)
    Using the list of instruments from step 1, generate positions using multitrend.py and return a dictionary of positions using the function trend_forecast() from trend_following/multitrend.py
        Arguments:
            instr_list : list[str] e.g. ['ES', 'ZF']
                list of instruments to generate positions for
            weights : dict e.g. [ES=0.5, US=0.5]
                weights for each instrument
            capital : int
                trading capital
            risk_target_tau : float
                risk target e.g. 0.20
            multipliers : dict e.g. {'ES' : 1.0, 'ZF' : 1.0}
                multipliers for each instrument
            fast_spans : list[int] e.g. [20, 50]
                fast spans for each instrument

        Returns a tuple of two dictionaries, one for the buffered positions and one for the unbuffered positions


3. Calculate positions as a result of carry (Nꟲ)

4. Sum trend and carry positions into N (N = Nᵀ + Nꟲ)

5. Plug N into dyn_opt/dyn_opt.py get_optimized_positions() to get optimized positions (Nᴼ)
    Arguments:
        held_positions : dictionary e.g. {'ES' : 1, 'ZF' : 3}
            what we already hold (should be integer positions)
            maybe from a CSV file in the repo, database, trading platform
        ideal_positions : dictionary e.g. {'ES' : 0.94, 'ZF' : -0.1}
            the value of N from step 3 (should be unrounded float positions)
            calculated with trading capital not the 50MM 'jumbo portfolio'
        notional_exposure_per_contract : dictionary e.g. {'ES' : 50000, 'ZF' : 100000}
            the notional exposure per contract for instrument
            should be calculated with the most recent price and multipliers (maybe add a function for this)
        capital : float
            total trading capital we have access to (not the 50MM 'jumbo portfolio')
        costs_per_contract : dict {'ES' : 0.008, 'ZF' : 10.75}
            estimate of the costs per contract for each instrument
            this needs to be updated occasionally based on current conditions (monthly?)
                no clue if this has been done or if it needs to be done
        returns_df : pandas.DataFrame (% returns)
            e.g. 
            Date        ES      ZF
            2019-01-01  0.01    0.02
            2019-01-02  0.02    -0.01
            2019-01-03  0.01    0.01

            Likely that each instrument will have different dates so an inner merge of daily returns on date is needed
        risk_target : float
            simply just 0.20 unless we want to use a different risk target

    Returns a buffered and optimized set of integer positions (Nᴼ)

6. Plug positions into risk_analysis/risk_functions.py RiskOverlay().final_risk_multiplier() to get the portfolio multiplier (apply the multiplier to each position)
    Arguments:
        position_weights : pd.DataFrame 
            e.g.
                ES      ZF
            0   -2.1    1.68

            position weights are the notional exposure per contract * N (+ or - positions) / trading capital
        position_percent_returns : pd.DataFrame
            Date        ES      ZF
            2019-01-01  0.01    0.02
            2019-01-02  0.02    -0.01
            2019-01-03  0.01    0.01

    Returns the portfolio multiplier

7. Iterate through the risk_multiplier adjusted positions and plug into risk_analysis/risk_functions.py PositionsLimits().maximum_position()
    Arguments:
        number of contracts : float
            contracts for each instrument
        IDM : float
            determined from Carver's table
        instrument_weight : float
            assume equal for all instruments (unless we decide otherwise)
        risk_target : float
            0.20 unless that changes
        annualized_stddev : float
            annualized standard deviation of the instrument (can use weighted between 10 year and current)
        average_forecast : float
            normally 10 (average absolute forecast)
        max_leverage_ratio : float
            max leverage ratio of the entire portfolio (often 2)
        capital : float
            trading capital
        notional_exposure_per_contract : float
            notional exposure per contract for the instrument
        open_interest : int
            open interest for the contract
        max_open_interest : float
            max percent of open interest we would like to be

    Returns position multiplier in order to stay within max forecast, leverage, and open interest

8. Scale every position by position multiplier, round to nearest integer and buffer        
"""
