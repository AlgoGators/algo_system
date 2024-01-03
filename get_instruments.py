import pandas as pd
from risk_analysis import risk_functions

def get_instruments(
    instruments : list[str],
    instrument_weight : float,
    IDM : float,
    risk_target : float,
    instrument_returns_df : pd.DataFrame,
    maximum_leverage : float) -> list[str]:
    """
    Returns list of instruments that meet our volatility requirements

    Parameters:
    ---
    instruments : list[str]
        list of all possible instruments we may be interested in trading
    instrument_weight : float
        weight of any instrument within the portfolio (equal for all instruments, unless we decide otherwise)
    IDM : float
        determined from Carver's table
    risk_target : float
        0.20 unless that changes
    instrument_returns_df : pd.DataFrame
        e.g. 
        Date        ES      ZF
        2019-01-01  0.01    0.02
        2019-01-02  0.02    -0.01
    maximum_leverage : float
        maximum leverage ratio of the entire position (2? 4?)
    ---
    """

    acceptable_instruments = [instrument for instrument in instruments if risk_functions.Volatility().minimum_volatility(IDM, instrument_weight, risk_target, instrument_returns_df[instrument].tolist(), maximum_leverage)]

    return acceptable_instruments
