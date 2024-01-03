import pandas as pd
from dyn_opt import dyn_opt

def get_optimized_positions(
    held_positions : dict,
    ideal_positions : dict,
    notional_exposures_per_contract : dict,
    capital : float,
    costs_per_contract : dict,
    returns_df : pd.DataFrame,
    risk_target : float) -> dict:

    """
    Returns a dictionary of optimized positions given certain capital

    NOTE:
        All currency values must be in the same currency, i.e. convert all exposures/costs to $

    Parameters:
    ---
        held_positions : dict
            Dictionary of held positions for each instrument
        ideal_positions : dict
            Dictionary of optimal positions for each instrument assuming fractional positions can be held
        notional_exposures_per_contract : dict
            Dictionary of the notional exposure per contract for each instrument
        capital : float
            The capital available to be used
        costs_per_contract : dict
            Dictionary of the costs per contract for each instrument (estimate)
        returns_df : pd.DataFrame
            Historical returns for each instruments (daily)
        risk_target : float
            The risk target for the portfolio
    ---
    """

    return dyn_opt.get_optimized_positions(
        held_positions=held_positions, 
        ideal_positions=ideal_positions, 
        notional_exposures_per_contract=notional_exposures_per_contract, 
        capital=capital, 
        costs_per_contract=costs_per_contract, 
        returns_df=returns_df, 
        risk_target=risk_target)
