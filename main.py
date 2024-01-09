import pandas as pd
from config import *
from get_instruments import get_instruments
from get_trend_signals import get_trend_positions
from get_optimized_positions import get_optimized_positions
from get_risk_adjusted_positions import get_risk_adjusted_positions
from get_buffered_positions import get_buffered_positions

def main():
    #!! NEED to source this
    all_instruments = []

    instrument_returns_df = pd.DataFrame()

    instrument_weight = 1 / len(all_instruments)

    #!! NEED to calculate the following:
    multipliers = {}

    held_positions = {}

    notional_exposure_per_contract = {}
    
    costs_per_contract = {}

    open_interest_dct = {}

    standard_deviation_dct = {}

    instrument_weights_dct = {}

    instruments = get_instruments(
        instruments=all_instruments,
        instrument_weight=instrument_weight,
        IDM=IDM,
        risk_target=RISK_TARGET,
        instrument_returns_df=instrument_returns_df,
        maximum_leverage=MAXIMUM_LEVERAGE)
    
    #? doesnt need past returns?
    trend_positions = get_trend_positions(
        instruments=instruments,
        weights={},#? reason not to make it equal (1/len(instruments))?
        capital=CAPITAL,
        #!! IDM=IDM
        risk_target_tau=RISK_TARGET,
        multipliers=multipliers,
        fast_spans=FAST_SPANS)#? values?

    #!! NEED to calculate carry_positions: 
    carry_positions = {}

    total_positions = {}

    for instrument in instruments:
        total_positions[instrument] = trend_positions[instrument] + carry_positions[instrument]

    optimized_positions = get_optimized_positions(
        held_positions=held_positions,
        ideal_positions=total_positions,
        notional_exposures_per_contract=notional_exposure_per_contract,
        capital=CAPITAL,
        costs_per_contract=costs_per_contract,
        returns_df=instrument_returns_df,
        risk_target=RISK_TARGET)
    
    risk_adjusted_positions = get_risk_adjusted_positions(
        positions=optimized_positions,
        notional_exposure_per_contract=notional_exposure_per_contract,
        capital=CAPITAL,
        risk_target=RISK_TARGET,
        IDM=IDM,
        average_forecast=AVERAGE_FORECAST,
        open_interest_dct=open_interest_dct,
        standard_deviation_dct=standard_deviation_dct,
        instrument_weights_dct=instrument_weights_dct,
        max_forecast=MAX_FORECAST,
        max_position_leverage_ratio=MAX_POSITION_LEVERAGE_RATIO,
        max_forecast_margin=MAX_FORECAST_MARGIN,
        max_pct_of_open_interest=MAX_PCT_OF_OPEN_INTEREST,
        instrument_returns_df=instrument_returns_df,
        max_portfolio_leverage=MAXIMUM_PORTFOLIO_LEVERAGE)
    
    buffered_positions = get_buffered_positions(
        positions=risk_adjusted_positions,
        held_positions=held_positions,
        buffer_fraction=BUFFER_FRACTION)
    
    #? what to do with buffered positions?
    


if __name__ == '__main__':
    main()

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
