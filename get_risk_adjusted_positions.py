import pandas as pd
from risk_analysis import risk_functions

def get_portfolio_risk_multiplier(
    instruments : list,
    notional_exposure_per_contract : dict,
    capital : float,
    instrument_returns_df) -> float:

    position_weights = {}

    for instrument in instruments:
        position_weights[instrument] = [notional_exposure_per_contract[instrument] / capital]

    position_weights = pd.DataFrame.from_dict(position_weights)

    return risk_functions.RiskOverlay().final_risk_multiplier(
        position_weights=position_weights,
        position_percent_returns=instrument_returns_df)

def get_position_risk_multiplier(
    number_of_contracts : float,
    IDM : float,
    instrument_weight : float,
    risk_target : float,
    annualized_stddev : float,
    average_forecast : int,
    max_forecast : int,
    max_leverage_ratio : int,
    capital : float,
    notional_exposure_per_contract : float,
    open_interest : int,
    max_pct_of_open_interest : float,
    max_forecast_margin : float) -> float:
    """
    Parameters:
    ---
    number_of_contracts : float
        number of contracts requested for this instrument, should be unrounded
    IDM : float
        same IDM as used in every other step
    instrument_weight : float
        capital allocation to this instrument / total capital
    
    """

    return risk_functions.PositionLimits().maximum_position(
        number_of_contracts=number_of_contracts,
        IDM=IDM,
        instrument_weight=instrument_weight,
        risk_target=risk_target,
        annualized_stddev=annualized_stddev,
        average_forecast=average_forecast,
        max_forecast=max_forecast,
        max_leverage_ratio=max_leverage_ratio,
        capital=capital,
        notional_exposure_per_contract=notional_exposure_per_contract,
        open_interest=open_interest,
        max_pct_of_open_interest=max_pct_of_open_interest,
        max_forecast_margin=max_forecast_margin)

def get_risk_adjusted_positions(
    positions : dict,
    notional_exposure_per_contract : dict,
    capital : float) -> dict:

    instruments = list(positions.keys())

    final_risk_multiplier = get_portfolio_risk_multiplier(
        instruments=instruments,
        notional_exposure_per_contract=notional_exposure_per_contract,
        capital=capital,)

    risk_adjusted_positions = positions

    if final_risk_multiplier < 1:
        for instrument in instruments:
            risk_adjusted_positions[instrument] = positions[instrument] * final_risk_multiplier

    for instrument in instruments:
        position_risk_multiplier = get_position_risk_multiplier()
        
        if position_risk_multiplier >= 1:
            continue

        risk_adjusted_positions[instrument] = position_risk_multiplier * risk_adjusted_positions[instrument]

    

if __name__ == '__main__':
    get_portfolio_risk_multiplier({'ES' : 25000, 'ZF' : 100000}, 500000)