"""

Outline:
...
Calculate risk values using             risk_measures.py
...
Calculate optimized positions using     dyn_opt.py
... (if applicable)
Place orders using                      update_portfolio.py

"""

import pandas as pd
import numpy as np
import json
import requests
from enum import Enum
import typing
import importlib

import sys
import os

# Add the ib_utils directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ib-gateway/ib_utils')))

# Add the ib_utils/src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ib-gateway/ib_utils/src')))


update_portfolio = importlib.import_module('ib-gateway.ib_utils.update_portfolio') #!!! yes, yes ... i know, i will change the name later :(


#!!!! Config settings like port numbers, etc. !!!!#
class Config:
    RISK_MEASURES_PORT = 5001
    OPTIMIZED_POSITIONS_PORT = 5002


class SERVICE_TYPE(str, Enum):
    AGGREGATOR = 'aggregator'
    RISK_MEASURES = 'risk_measures'

class ContainerUtils:
    def client_request(data : typing.Any, port : int, service : SERVICE_TYPE) -> typing.Any:
        """Sends a request to the server and returns the response."""
        serialized_data = ContainerUtils.serialize(data)
        if serialized_data is not None:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f'http://localhost:{port}/{service.value}', data=serialized_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return result

            else:
                raise Exception(f"Error: {response.status_code}")

    def serialize(data : typing.Any) -> str:
        """Serializes data to a json string."""
        try:
            return json.dumps(data)
        except Exception as e:
            print("Error serializing data:", e)
            print("Data:", data)
            return None
        
    def dataframe_to_dict(df : pd.DataFrame) -> dict[str, dict]:
        """Converts a pandas DataFrame to a dictionary of dictionaries."""
        return {str(column): df[column].to_dict() for column in df}

    def convert_to_dataframes(json_dict : dict[str, str]):
        """Converts a dictionary of json strings to a dictionary of pandas DataFrames."""
        df_dict : dict[str, pd.DataFrame] = {}
        for key in json_dict.keys():
            df_dict[key] = pd.read_json(json_dict[key])
        return df_dict

    def sanitize_data(df : pd.DataFrame) -> pd.DataFrame:
        df = df.replace([np.inf, -np.inf], np.nan)
        df.index = df.index.astype(str)  # Convert index to string
        return df.where(pd.notnull(df), None)  # Convert NaN to None

def get_risk_measures(
        trend_tables : dict[str, pd.DataFrame],
        weights : tuple[float, float, float],
        warmup : int,
        unadj_column : str,
        expiration_column : str,
        date_column : str,
        fill : bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Calculates risk measures for a set of instruments. Returns daily returns, product returns, GARCH variances, and GARCH covariances.
    
    Parameters:
    trend_tables : dict[str, pd.DataFrame]
        A dictionary where each key is the instrument and the DataFrame is the instrument's prices, delivery months, etc.
    weights : tuple[float, float, float]
        Weights applied to GARCH calculations for each instrument, default is (0.01, 0.01, 0.98).
    warmup : int
        Number of days to warm up the GARCH model, default is 100.
    unadj_column : str
        Column name for unadjusted prices, default is "Unadj_Close".
    expiration_column : str
        Column name for delivery months, default is "Delivery Month".
    date_column : str
        Column name for dates, default is "Date".
    fill : bool
        Whether to fill missing dates, default is True.    
    """
    
    trend_tables_json = {contract: table.to_json() for contract, table in trend_tables.items()}

    data = {
        "trend_tables": trend_tables_json,
        "weights": weights,
        "warmup": warmup,
        "unadj_column": unadj_column,
        "expiration_column": expiration_column,
        "date_column": date_column,
        "fill": fill
    }

    result = ContainerUtils.client_request(data, Config.RISK_MEASURES_PORT, SERVICE_TYPE.RISK_MEASURES)

    if result is None:
        raise Exception("Error: No result returned")
    
    dfs = ContainerUtils.convert_to_dataframes(result)

    return dfs['daily_returns'], dfs['product_returns'], dfs['GARCH_variances'], dfs['GARCH_covariances']


def get_optimized_positions(
    unadj_prices : pd.DataFrame,
    multipliers : pd.DataFrame,
    ideal_positions : pd.DataFrame,
    covariances : pd.DataFrame,
    jump_covariances : pd.DataFrame,
    open_interest : pd.DataFrame,
    instrument_weight : pd.DataFrame,
    capital : float,
    fixed_cost_per_contract : float,
    IDM : float,
    tau : float,
    asymmetric_risk_buffer : float,
    maximum_forecast_ratio : float,
    max_acceptable_pct_of_open_interest : float,
    max_forecast_buffer : float,
    maximum_position_leverage : float,
    maximum_portfolio_leverage : float,
    maximum_correlation_risk : float,
    maximum_portfolio_risk : float,
    maximum_jump_risk : float,
    cost_penalty_scalar : float) -> pd.DataFrame:
    """
    Calculates optimized positions for a set of instruments. Returns the optimized positions.

    Parameters:
    unadj_prices : pd.DataFrame
        Unadjusted prices for each instrument (see risk_management/dyn_opt/unittesting/data/unadj_prices.parquet)
    multipliers : pd.DataFrame
        Multipliers for each instrument. (see risk_management/dyn_opt/unittesting/data/multipliers.parquet)
    ideal_positions : pd.DataFrame
        Ideal positions for each instrument. (see risk_management/dyn_opt/unittesting/data/ideal_positions.parquet)
    covariances : pd.DataFrame
        Covariances for each instrument. (see risk_management/dyn_opt/unittesting/data/covariances.parquet)
    jump_covariances : pd.DataFrame
        Jump covariances for each instrument. (see risk_management/dyn_opt/unittesting/data/jump_covariances.parquet)
    open_interest : pd.DataFrame
        Open interest for each instrument. (see risk_management/dyn_opt/unittesting/data/open_interest.parquet)
    instrument_weight : pd.DataFrame
        Weight for each instrument. 1/N works where N is the number of instruments.
    capital : float
        Capital available for trading.
    fixed_cost_per_contract : float
        Fixed cost per contract.
    IDM : float
        IDM, default is 2.5.
    tau : float
        Tau, default is 0.2.
    asymmetric_risk_buffer : float
        Asymmetric risk buffer, default is 0.05.
    maximum_forecast_ratio : float
        Maximum forecast ratio, default is 2.0.
    max_acceptable_pct_of_open_interest : float
        Maximum acceptable percentage of open interest, default is 0.01.
    max_forecast_buffer : float
        Maximum forecast buffer, default is 0.5.
    maximum_position_leverage : float
        Maximum position leverage, default is 2.0.
    maximum_portfolio_leverage : float
        Maximum portfolio leverage, default is 20.0.
    maximum_correlation_risk : float
        Maximum correlation risk, default is 0.65.
    maximum_portfolio_risk : float  
        Maximum portfolio risk, default is 0.3.
    maximum_jump_risk : float
        Maximum jump risk, default is 0.75.
    cost_penalty_scalar : float
        Cost penalty scalar, default is 10.
    """
    
    unadj_prices = ContainerUtils.sanitize_data(unadj_prices)
    multipliers = ContainerUtils.sanitize_data(multipliers)
    ideal_positions = ContainerUtils.sanitize_data(ideal_positions)
    covariances = ContainerUtils.sanitize_data(covariances)
    jump_covariances = ContainerUtils.sanitize_data(jump_covariances)
    open_interest = ContainerUtils.sanitize_data(open_interest)
    instrument_weight = ContainerUtils.sanitize_data(instrument_weight)

    data = {
        "capital": capital,
        "fixed_cost_per_contract": fixed_cost_per_contract,
        "tau": tau,
        "asymmetric_risk_buffer": asymmetric_risk_buffer,
        "unadj_prices": ContainerUtils.dataframe_to_dict(unadj_prices),
        "multipliers": ContainerUtils.dataframe_to_dict(multipliers),
        "ideal_positions": ContainerUtils.dataframe_to_dict(ideal_positions),
        "covariances": ContainerUtils.dataframe_to_dict(covariances),
        "jump_covariances": ContainerUtils.dataframe_to_dict(jump_covariances),
        "open_interest": ContainerUtils.dataframe_to_dict(open_interest),
        "instrument_weight": ContainerUtils.dataframe_to_dict(instrument_weight),
        "IDM": IDM,
        "maximum_forecast_ratio": maximum_forecast_ratio,
        "max_acceptable_pct_of_open_interest": max_acceptable_pct_of_open_interest,
        "max_forecast_buffer": max_forecast_buffer,
        "maximum_position_leverage": maximum_position_leverage,
        "maximum_portfolio_leverage": maximum_portfolio_leverage,
        "maximum_correlation_risk": maximum_correlation_risk,
        "maximum_portfolio_risk": maximum_portfolio_risk,
        "maximum_jump_risk": maximum_jump_risk,
        "cost_penalty_scalar": cost_penalty_scalar
    }

    result = ContainerUtils.client_request(data, Config.OPTIMIZED_POSITIONS_PORT, SERVICE_TYPE.AGGREGATOR)

    if result is None:
        raise Exception("Error: No result returned")
    
    dfs = ContainerUtils.convert_to_dataframes(result)

    return dfs['positions']

def place_orders(data_positions, instruments_df):
    """
    Places orders for a set of instruments.

    Parameters:
    data_positions : dict[str, float]
        A dictionary where each key is the instrument and the value is the position.
        --- Important to note!!! Use the data instruments names, this shouldn't be a problem 
            because we don't normally use the IBKR symbols but nevertheless
    instruments_df : pd.DataFrame
        A DataFrame containing the instrument names and their corresponding IBKR symbols (and other details).
        --- see ib-gateway/ib_utils/unittesting/instruments.csv
    """
    update_portfolio.update_portfolio(data_positions, instruments_df)

if __name__ == "__main__":
    place_orders(
        data_positions = {
            "ES": 1,
            "NQ": 0,
            "FDAX" : 0,
        },
        instruments_df = pd.read_csv("ib-gateway/ib_utils/unittesting/instruments.csv")
    )
