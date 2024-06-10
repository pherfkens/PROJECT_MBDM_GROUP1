import pandas as pd
from ema_workbench import MultiprocessingEvaluator, Scenario
from ema_workbench.em_framework.optimization import (
    EpsilonProgress, ArchiveLogger, to_problem
)
from ema_workbench.util import ema_logging
from custom_problem_formulation import get_model_for_problem_formulation

def load_scenarios(filepath):
    df = pd.read_csv(filepath)
    df.rename(columns={df.columns[0]: 'scenario_id'}, inplace=True)
    scenarios = [
        Scenario(row['scenario_id'], **row.drop('scenario_id').to_dict())
        for _, row in df.iterrows()
    ]
    return scenarios

def optimize_scenarios(model, scenarios, nfe, epsilon, seeds=4):
    results = []
    convergences = []
    with MultiprocessingEvaluator(model) as evaluator:
        for scenario in scenarios:
            for seed in range(seeds):
                convergence_metrics = [
                    ArchiveLogger(
                        "./archive",
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

def save_results(result, convergence, scenario_name, seed):
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
