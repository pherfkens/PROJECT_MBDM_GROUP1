# import all modules, some might not be necessary (DIE NOG VERWIJDEREN)
from ema_workbench import (
    Model,
    MultiprocessingEvaluator,
    ScalarOutcome,
    IntegerParameter,
    optimize,
    Scenario,
    Constraint,
)
from ema_workbench.em_framework.optimization import EpsilonProgress, epsilon_nondominated
from ema_workbench.util import ema_logging

from ema_workbench import (
    HypervolumeMetric,
    GenerationalDistanceMetric,
    EpsilonIndicatorMetric,
    InvertedGenerationalDistanceMetric,
    SpacingMetric,
)
from ema_workbench.em_framework.optimization import to_problem, ArchiveLogger
from custom_problem_formulation_no_RfR import get_model_for_problem_formulation
import pandas as pd

# Set up logging
ema_logging.log_to_stderr(ema_logging.INFO)

# Get the model and problem formulation
model, steps = get_model_for_problem_formulation()
problem = to_problem(model, searchover="levers")

# Load the selected scenarios
scenarios_df = pd.read_csv('results/selected_scenarios.csv')
scenarios_df.rename(columns={'Unnamed: 0': 'scenario_id'}, inplace=True)
scenarios_df = scenarios_df.set_index('scenario_id')

scenario_ids = scenarios_df.index.to_list()
archive_dict = {}
results_dict = {}
convergence_dict = {}
amount_of_seeds = 4

# Process each scenario
for scenario in scenario_ids:
    archive_list = []
    results_list = []
    convergence_list = []
    for i in range(amount_of_seeds):
        archives = ArchiveLogger.load_archives(f"./archive/Policy_search_arch_{float(scenario)}_seed{i}.tar.gz")
        for key, df in archives.items():
            if 'Unnamed: 0' in df.columns:
                del df['Unnamed: 0']
            df.drop(['A.1_RfR Costs', 'A.2_RfR Costs'], axis=1, inplace=True)
        archive_list.append(archives)

        result = pd.read_csv(f"./results/Policy_search_scen{float(scenario)}_seed{i}results.csv", index_col=0)
        result.drop(['A.1_RfR Costs', 'A.2_RfR Costs'], axis=1, inplace=True)
        results_list.append(result)

        convergence = pd.read_csv(f"./results/Policy_search_scen{float(scenario)}_seed{i}convergence.csv", index_col=0)
        convergence_list.append(convergence)

    archive_dict[scenario] = archive_list
    results_dict[scenario] = results_list
    convergence_dict[scenario] = convergence_list

policy_dict = {}
epsilon = [100, 100, 0.01, 100, 100, 100, 0.01, 100]
for i in range(len(scenario_ids)):
    df = epsilon_nondominated(results_dict[scenario_ids[i]], epsilon, problem)
    policy_dict[scenario_ids[i]] = df
    n_policies = df.shape[0]
    print(f"Scenario {scenario_ids[i]} has {n_policies} non-dominated policies")

for scenario in scenario_ids:
    df_all_seeds = pd.concat(results_dict[scenario])
    df_unique_policies = df_all_seeds.drop_duplicates()
    print(f"Scenario {scenario} has {df_unique_policies.shape[0]} unique policies")

# Calculate and save convergence metrics
convergence_metrics = {}
# for scenario in scenario_ids:
for scenario in [39833]:
    # if scenario == 39833:
    #     continue
    pols = policy_dict[scenario]
    hv = HypervolumeMetric(pols, problem)
    gd = GenerationalDistanceMetric(pols, problem, d=1)
    ei = EpsilonIndicatorMetric(pols, problem)
    ig = InvertedGenerationalDistanceMetric(pols, problem, d=1)
    sm = SpacingMetric(problem)

    convergence_metrics[scenario] = []

    for archive in archive_dict[scenario]:
        print(f"Calculating metrics for scenario {scenario}...")
        metrics = []
        for nfe, a in archive.items():
            print(f"Calculating metrics for NFE {nfe}...")
            scores = {
                "generational_distance": gd.calculate(a),
                "hypervolume": hv.calculate(a),
                "epsilon_indicator": ei.calculate(a),
                "inverted_gd": ig.calculate(a),
                "spacing": sm.calculate(a),
                "nfe": int(nfe),
            }
            metrics.append(scores)
        metrics = pd.DataFrame.from_dict(metrics)
        metrics.sort_values(by="nfe", inplace=True)
        convergence_metrics[scenario].append(metrics)
        
        # Save each scenario's metrics to CSV
        metrics.to_csv(f"results/convergence_metrics_scenario_{scenario}.csv", index=False)

print("Convergence metrics have been saved to CSV files.")
