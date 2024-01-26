def get_contract_cost_estimates(instruments : list, cost_estimate : float = None) -> dict:
    """For now we will assume all costs are the same"""

    contract_costs = {}
    for instrument in instruments:
        contract_costs[instrument] = cost_estimate

    return contract_costs
