import pandas as pd
from Carry import FinalCarry


"""
2. Calculate positions as a result of Carry (Nᵀ)
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
            carry_spans : list[int] e.g. [20, 50]
                spans for each instrument

        Returns a tuple of two dictionaries, one for the buffered positions and one for the unbuffered positions
"""
def get_carry_positions(
    instruments : list,
    weights : dict,
    capital : int,
    risk_target_tau : float,
    multipliers : dict,
    carry_spans : list,
    ) -> dict:

    # Get positions from FinalCarry.py
    positions = FinalCarry.carry_forecast(
        instr_list=instruments,
        weights=weights,
        capital=capital,
        risk_target_tau=risk_target_tau,
        multipliers=multipliers,
        carry_spans=carry_spans,
        )

    return positions[1]
