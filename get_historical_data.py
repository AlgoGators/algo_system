import pandas as pd
from sqlalchemy import create_engine
import urllib
import os
import logging

def SQL_pull(instrument_list: list, unadj_column: str = 'Unadj_Close', adj_column: str = 'Close', interest_column : str = 'Open Interest'):
     # get all tables from database
    driver = "ODBC Driver 18 for SQL Server"
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")

    import time
    start = time.time()
    # Connection string for SQL Server Authentication - do not change
    params = urllib.parse.quote_plus(fr'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    # Retrieve a list of all table names in the database - do not change
    try:
        table_names_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog='" + database + "'"
        table_names = pd.read_sql(table_names_query, engine)['table_name'].tolist()
    except:
        # Raise the error if the table isn't found; considering it returned from the function anyway.
        raise KeyError("Unable to retrieve table names from database.")

    # Convert instrument list to name in database (e.g. 'ES' -> 'ES_Data')

    # Dictionary of dataframes
    instrument_dataframes = {}
    for instrument in instrument_list:
        table_name = instrument + '_Data'

        if (table_name not in table_names):
            raise KeyError(f"Error: {instrument} is not in the database.")
        
        table_query = f"SELECT * FROM [{table_name}]"
        instrument_dataframes[instrument] = pd.read_sql(table_query, engine)

    # Convert date column to datetime
    for instrument in instrument_list:
        instrument_dataframes[instrument]['Date'] = pd.to_datetime(instrument_dataframes[instrument]['Date'])
    
    # Set date column to index
    for instrument in instrument_list:
        instrument_dataframes[instrument].set_index('Date', inplace=True)
        assert instrument_dataframes[instrument].index.name == 'Date'
    
    # Get all adjusted close prices in each dataframe
    adjusted_prices = {}
    for instrument in instrument_list:
        adjusted_price_df = instrument_dataframes[instrument][adj_column]
        
        # Converted series to frame
        adjusted_price_df = adjusted_price_df.to_frame()

        adjusted_prices[instrument] = adjusted_price_df
        
    # Get all unadjusted close prices in each dataframe
    current_prices = {}
    for instrument in instrument_list:
        current_price_df = instrument_dataframes[instrument][unadj_column]

        # Converted series to frame
        current_price_df = current_price_df.to_frame()

        current_prices[instrument] = current_price_df

    open_interest = {}
    for instrument in instrument_list:
        open_interest_df = instrument_dataframes[instrument][interest_column]

        open_interest_df = open_interest_df.to_frame()

        open_interest[instrument] = open_interest_df

    return adjusted_prices, current_prices, open_interest

class Prices:
    def get_all_historical_prices(self, instruments : list[str], price_column : str = 'Close', interest_column : str = 'Open Interest') -> pd.DataFrame:
        collective_price_df = pd.DataFrame()
        collective_open_interest_df = pd.DataFrame()

        # Grabs the adjusted prices (_ is the current_prices which we dont need)
        prices_dct, _, open_interest_dct = SQL_pull(instruments, adj_column=price_column, interest_column=interest_column)

        for instrument in instruments:
            # Grabs the price & open interest dataframes for each instrument
            price_df : pd.DataFrame = prices_dct[instrument]
            open_interest_df : pd.DataFrame = open_interest_dct[instrument]

            price_df.rename(columns={price_column : instrument}, inplace=True)
            open_interest_df.rename(columns={interest_column : instrument}, inplace=True)
            # print(price_df)

            # If nothing has been added yet
            if collective_price_df.empty:
                collective_price_df = price_df
                collective_open_interest_df = open_interest_df
                continue
            
            collective_price_df = collective_price_df.join(price_df, how='inner')
            collective_open_interest_df = collective_open_interest_df.join(open_interest_df, how='inner')

        return collective_price_df, collective_open_interest_df

    def get_most_recent_prices(prices_df : pd.DataFrame) -> dict:
        most_recent_prices = {}

        instruments = prices_df.columns.tolist()

        for instrument in instruments:
            most_recent_prices[instrument] = prices_df[instrument].iloc[-1]

        return most_recent_prices

def get_most_recent_open_interest(open_interest_df : pd.DataFrame) -> dict:
    most_recent_open_interest = {}

    instruments = open_interest_df.columns.tolist()

    for instrument in instruments:
        most_recent_open_interest[instrument] = open_interest_df[instrument].iloc[-1]

    return most_recent_open_interest

if __name__ == '__main__':
    df = Prices().get_all_historical_prices(['6A', 'ES', 'ZF'])