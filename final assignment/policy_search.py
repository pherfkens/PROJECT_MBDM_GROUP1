import pandas as pd
from ema_workbench import MultiprocessingEvaluator, Scenario
from ema_workbench.em_framework.optimization import (
    EpsilonProgress, ArchiveLogger, to_problem
)
from ema_workbench.util import ema_logging
from custom_problem_formulation import get_model_for_problem_formulation

# Function to load the selected scenarios
def load_scenarios(filepath):
    """
    Loads scenarios from a CSV file. 

    Args:
        filepath (str): Path to the CSV file containing scenarios.

    Returns:
        list: List of Scenario objects.
    """
    df = pd.read_csv(filepath)
    df.rename(columns={df.columns[0]: 'scenario_id'}, inplace=True)
    scenarios = [
        Scenario(row['scenario_id'], **row.drop('scenario_id').to_dict())
        for _, row in df.iterrows()
    ]
    return scenarios

# Function to optimize the selected scenarios
def optimize_scenarios(model, scenarios, nfe, epsilon, seeds=4):
    """
    Optimizes scenarios using the EMA workbench.

    Args:
        model (object): The EMA model to use for optimization.
        scenarios (list): List of Scenario objects.
        nfe (int): Number of function evaluations (iterations).
        epsilon (list): Epsilon values for multi-objective optimization.
        seeds (int, optional): Number of random seeds for optimization runs. Defaults to 4.

    Returns:
        tuple: Tuple containing lists of optimization results and convergence metrics.
    """
    results = []
    convergences = []
    with MultiprocessingEvaluator(model) as evaluator:
        for scenario in scenarios:
            for seed in range(seeds):
                convergence_metrics = [
                    ArchiveLogger(
                        "./archive", # Save the optimisation logs in the archive folder
                        [lever.name for lever in model.levers],
                        [outcome.name for outcome in model.outcomes],
                        base_filename=f"Policy_search_arch_{scenario.name}_seed{seed}.tar.gz"
                    ),
                    EpsilonProgress()
                ]
                result, convergence = evaluator.optimize(
                    nfe=nfe,
                    searchover="levers",
                    epsilons=epsilon,
                    convergence=convergence_metrics,
                    reference=scenario
                )
                results.append(result)
                convergences.append(convergence)

                save_results(result, convergence, scenario.name, seed)
    return results, convergences

# Function to save the optimization results
def save_results(result, convergence, scenario_name, seed):
    """
    Saves optimization results and convergence data to CSV files.

    Args:
        result (object): Optimization result object.
        convergence (object): Convergence metrics object.
        scenario_name (str): Name of the scenario.
        seed (int): Random seed used for optimization.
    """
    filename = f'./results/Policy_search_scen{scenario_name}_seed{seed}'
    result.to_csv(filename + 'results.csv')
    convergence.to_csv(filename + 'convergence.csv')

if __name__ == "__main__":
    ema_logging.log_to_stderr(ema_logging.INFO)

    model, steps = get_model_for_problem_formulation()
    problem = to_problem(model, searchover='levers')

    scenarios = load_scenarios('results/selected_scenarios.csv')
    epsilon = [100, 100, 0.01, 100, 100, 100, 0.01, 100]
    nfe = 20000

    results, convergences = optimize_scenarios(model, scenarios, nfe, epsilon)
    print(f'Optimization complete. {len(results)} results obtained.')
