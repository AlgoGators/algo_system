def get_notional_exposure_per_contract(
    price : float,
    multiplier : float) -> float:

    return price * multiplier

def get_notional_exposures(
    prices : dict,
    multipliers : dict) -> dict:

    notional_exposures = {}

    for instrument in list(prices.keys()):
        notional_exposures[instrument] = get_notional_exposure_per_contract(
            price=prices[instrument],
            multiplier=multipliers[instrument])
    
    return notional_exposures
