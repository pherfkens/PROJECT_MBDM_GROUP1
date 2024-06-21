"""
Created on Wed Mar 21 17:34:11 2018

@author: ciullo

Edited by group 1 on 20 Jun 2024 for course EPA141A

@editors: 1. Leshem, 2. Rositsa, 3. Pepijn, 4. Wouter
"""
from ema_workbench import (
    Model,
    CategoricalParameter,
    ArrayOutcome,
    ScalarOutcome,
    IntegerParameter,
    RealParameter,
)
from dike_model_function import DikeNetwork  # @UnresolvedImport

import numpy as np


def sum_over(*args):
    numbers = []
    for entry in args:
        try:
            value = sum(entry)
        except TypeError:
            value = entry
        numbers.append(value)

    return sum(numbers)


def sum_over_time(*args):
    data = np.asarray(args)
    summed = data.sum(axis=0)
    return summed


def get_model_for_problem_formulation():
    """
    Returns the model and planning steps for the problem formulation.

    Returns:
        tuple: A tuple containing the dike model and the planning steps.

    """
    
    # Load the model:
    function = DikeNetwork()
    # workbench model:
    dike_model = Model("dikesnet", function=function)

    # Uncertainties and Levers:
    # Specify uncertainties range:
    Real_uncert = {"Bmax": [30, 350], "pfail": [0, 1]}  # m and [.]
    # breach growth rate [m/day]
    cat_uncert_loc = {"Brate": (1.0, 1.5, 10)}

    cat_uncert = {
        f"discount rate {n}": (1.5, 2.5, 3.5, 4.5) for n in function.planning_steps
    }

    Int_uncert = {"A.0_ID flood wave shape": [0, 132]}
    # Range of dike heightening:
    dike_lev = {"DikeIncrease": [0, 10]}  # dm

    # Series of five Room for the River projects:
    rfr_lev = [f"{project_id}_RfR" for project_id in range(0, 5)]

    # Time of warning: 0, 1, 2, 3, 4 days ahead from the flood
    EWS_lev = {"EWS_DaysToThreat": [0, 4]}  # days

    uncertainties = []
    levers = []

    for uncert_name in cat_uncert.keys():
        categories = cat_uncert[uncert_name]
        uncertainties.append(CategoricalParameter(uncert_name, categories))

    for uncert_name in Int_uncert.keys():
        uncertainties.append(
            IntegerParameter(
                uncert_name, Int_uncert[uncert_name][0], Int_uncert[uncert_name][1]
            )
        )

    # RfR levers can be either 0 (not implemented) or 1 (implemented)
    for lev_name in rfr_lev:
        for n in function.planning_steps:
            lev_name_ = f"{lev_name} {n}"
            levers.append(IntegerParameter(lev_name_, 0, 1))

    # Early Warning System lever
    for lev_name in EWS_lev.keys():
        levers.append(
            IntegerParameter(lev_name, EWS_lev[lev_name][0], EWS_lev[lev_name][1])
        )

    for dike in function.dikelist:
        # uncertainties in the form: locationName_uncertaintyName
        for uncert_name in Real_uncert.keys():
            name = f"{dike}_{uncert_name}"
            lower, upper = Real_uncert[uncert_name]
            uncertainties.append(RealParameter(name, lower, upper))

        for uncert_name in cat_uncert_loc.keys():
            name = f"{dike}_{uncert_name}"
            categories = cat_uncert_loc[uncert_name]
            uncertainties.append(CategoricalParameter(name, categories))

        # location-related levers in the form: locationName_leversName
        for lev_name in dike_lev.keys():
            for n in function.planning_steps:
                name = f"{dike}_{lev_name} {n}"
                levers.append(
                    IntegerParameter(name, dike_lev[lev_name][0], dike_lev[lev_name][1])
                )

    # load uncertainties and levers in dike_model:
    dike_model.uncertainties = uncertainties
    dike_model.levers = levers

    # Problem formulations:
    # Outcomes are all costs, thus they have to minimized:
    direction = ScalarOutcome.MINIMIZE

    outcomes = []

    for dike in function.dikelist:
        if dike in ['A.1', 'A.2']: # Changed the original problem formulation to exclude dike rings A.3, A.4, and A.5
            external_cost_variables = []
            for e in ["Expected Evacuation Costs", "Dike Investment Costs"]:
                external_cost_variables.append(f"{dike}_{e}")

            outcomes.append(
                ScalarOutcome(
                    f"{dike}_External Costs", # Made our own outcome 'External Costs' which is the sum of the Expected Evacuation Costs and Dike Investment Costs
                    variable_name=[var for var in external_cost_variables],
                    function=sum_over,
                    kind=direction,
                )
            )

            outcomes.append(
                ScalarOutcome(
                    f"{dike}_RfR Costs",                     # We wanted to measure the RfR Costs per dike ring. However, this was not possible due to the way the RfR Costs are 
                    variable_name=f"{dike}_RfR Total Costs", # measured, however we only found out later and couldn't rerun the results so this formulation was used for the 
                    function=sum_over,                       # base case generation. This will be explained more in depth at the relevant parts of the code and notebooks.
                    kind=direction,
                )   
            )

            outcomes.append(
                ScalarOutcome(
                    f"{dike}_Expected Number of Deaths",
                    variable_name=f"{dike}_Expected Number of Deaths",
                    function=sum_over,
                    kind=direction,
                )
            )

            outcomes.append(
                ScalarOutcome(
                    f"{dike}_Expected Annual Damage",
                    variable_name=f"{dike}_Expected Annual Damage",
                    function=sum_over,
                    kind=direction,
                )
            )

    dike_model.outcomes = outcomes

    return dike_model, function.planning_steps


if __name__ == "__main__":
    get_model_for_problem_formulation()
