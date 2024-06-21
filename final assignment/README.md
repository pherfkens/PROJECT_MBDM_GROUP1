# Outline of directory
The project Room for the River for the course EPA141A has primarly been done in this directory. This directory consists of the following files:

Main files inspected to understand the model are [dike_model_function.py](dike_model_function.py), [problem_formulation.py](problem_formulation.py) and [dike_model_simulation.py](dike_model_simulation.py).  
The problem_formulation was used to create [custom_problem_formulation_no_RFR.py](custom_problem_formulation_no_RFR.py), which is a problem formulation for the model, but edited specifically for our problem. 

The files starting with 'funs_(...)' are technical representations of aspects of the system.  

The following files were created for writing the report and providing Dike Rings 1 & 2 with thorough advice, in the order of the report:  

[custom_problem_formulation_no_RFR.py](custom_problem_formulation_no_RFR.py)  
-- Edited problem formulation designed for our own specific problem. Is being used by other notebooks.  
---- Don't need an inputargument, as this problem formulation has been adjusted to our problem.
---- Output is the model and its planning steps.

[base_case.ipynb](base_case.ipynb)  
-- Notebook to generate 50000 experiments for our problem formulation. All ran with the 'base case' policy. 
---- Notebook has as input the number of scenario's (50,000 in our case) and the model being retrieved from the problem formulation as defined earlier.   
---- The output is a tar.gz file containing 50,000 experiments (50000 scenarios * 1 policies * 1 model).  

[SOBOL.ipynb](SOBOL.ipynb)  
-- For the sake of global sensitivity analysis (GSA), the SOBOL technique was used. 
---- As input, scenario's had to be made. The argument uncertainty_sampling=Samplers.SOBOL is needed for this analysis.
---- The output of this notebook are several plots visualizing the SOBOL metrics on different outcomes of the model.  

[Feature_Scoring_&_Dim_Stacking.ipynb](Feature_Scoring_&_Dim_Stacking.ipynb)  
-- Also part of the uncertainty analysis.  Feature scoring & dimensional stacking. 
---- As input the experiments and outcomes, as generated in the base_case notebook, should be used.
---- The notebook's output is multiple plots. For feature scoring, a heatmap shows the degree of correlation between uncertainty and outcomes. The Dimensional stacking produces plots showing which uncertainties most often lead to worst case scenario's.  

[scenario_discovery_prim.ipynb](scenario_discovery_prim.ipynb)   
-- To find scenario's which are the considered the worst for the Dike Ring 1&2, scenario discovery was done. Therefore, a PRIM analysis was performed. This way 5 worst scenario's had been selected. 
---- As input the 50,000 experiments, produced in base_case notebook was used.  
---- The output is a csv with the 5 selected scenario's. Also, a csv with the remaining scenario's in the PRIM box has been created.

[policy_search.py](policy_search.py)  
-- This file takes the five scenarios that were selected, and optimises (using epsilonNSGA2 algorithm) our policy levers for each scenario four times (4 seeds). The nfe is number of function evaluations. So, this is where the optimal policies come from, and it also stores convergence data that is later used to calculate those metricsContains three functions, one to load scenario's and one to save the results from the function `optimize_scenarios(model, scenarios, nfe, epsilon, seeds=4)`.
---- For the input, the model from the get_model function, scenario's csv, nfe, epsilon and number of seeds is 4 by default. 
---- The output includes a number of csv's. The archive being saved as `Policy_search_arch_{scenario.name}_seed{seed}.tar.gz` in the archive folder. The convergence data as `Policy_search_scen{scenario_name}_seed{seed}convergence.csv` and the results data as `Policy_search_scen{scenario_name}_seed{seed}results.csv` both in the results folder.  

[directed_search.ipynb](directed_search.ipynb)   
-- This notebook aims to find 50 diverse policies. It also calculates some covergence metrics to ensure the policies are optimal. 
---- As input 4 csv's need to be read in: the selected scenarios, the results of policy search per scenario per seed, the convergence of policy search per scenario per seed, and the base_case experiments. 
---- The output is a csv with 50 diverse policies.  

[robustness_testing.ipynb](robustness_testing.ipynb)   
-- Notebook to further filter down the 50 diverse policies to only 4 policies, which will then be recommended to the Dike Ring. It calculates the SNR-ratio (signal-to-noise ratio) and plots it for different policies. ALso, the maximum regret is being computed per remainig policy. 
---- As an input, the 50 diverse policies csv is necessary. 
---- The output are different plots from the SNR-ratio calculations, and the maximum regret grids. Finally, a csv is being written with the final 4 policies.  

[vulnerability_testing.ipynb](vulnerability_testing.ipynb)   
-- To test the vulnerability of the remaining policies, a PRIM analysis like in the scenario discovery was done, was performed again. Thereafter, it was clear what scenario's are likely to gain trouble for our policies.
---- As input, multiple csv's should be inputted. The csv with the remaining scenario's in the PRIM box from scenario_discovery_prim.ipynb. The csv with the final policies. 
---- The output contains of multiple PRIM plots, but most importantly the dataframe sorted on least desired values for the outcomes.   


Also, this directory cotain a couple of other directories, where data is stored.   

`archive\` where the archive files are stored from [policy_search.py](policy_search.py).   
`data\` where data is stored deliverd at the start of this project, so the model has the correct data.   
`images\` where images are being saved, so that they can be implemented in the report delivarable.  
`results\` where the convergence and result csv's are being stored, retrieved from [policy_search.py](policy_search.py).      