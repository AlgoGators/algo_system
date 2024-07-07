"""
The Algo System:
1. The Data Engine collects raw data from Databento 
2. The data engine processes the raw data into a cleaned and usable format
3. The data engine finds the signals for carry and trend strategies
4. The data engine sends the following pieces of data to the dynamic optimization:
    - The singals for carry and trend strategies
    - 
"""
import pandas as pd

from data_engine.pipeline import Pipeline
from risk_management.dyn_opt.dyn_opt import aggregator

if __name__ == "__main__":
    # Pipeline kicked off
    pipeline = Pipeline()
    pipeline.rebuild()
    pipeline.transform()
    pipeline.load()
    pipeline.signals()

    positions: pd.Dataframe = aggregator(capital= ,
                           fixed_cost_per_contract= ,
                           tau= ,
                           asymmetric_risk_buffer= ,
                           unadj_prices= ,
                           multipliers= ,
                           ideal_positions= ,
                           covariances= ,
                           jump_covariances= ,
                           open_interest= ,
                           instrument_weight= ,
                           IDM= ,
                           maximum_forecast_ratio= ,
                           max_acceptable_pct_of_open_interest= ,
                           max_forecast_buffer= ,
                           maximum_position_leverage= ,
                           maximum_portfolio_leverage= ,
                           maximum_correlation_risk= ,
                           maximum_portfolio_risk= ,
                           maximum_jump_risk= ,
                           cost_penalty_scalar)
