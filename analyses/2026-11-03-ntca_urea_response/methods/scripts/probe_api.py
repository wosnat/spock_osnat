import inspect
from multiomics_explorer import differential_expression_by_gene, to_dataframe
print(inspect.signature(differential_expression_by_gene))
EXP = "10.1038/msb4100087_growth_medium_growth_on_urea_as_med4_microarray"
r = differential_expression_by_gene(experiment_ids=[EXP], locus_tags=["PMM0963"], verbose=True)
print({k: v for k, v in r.items() if k != "results"})
print(r["results"][0])
print(to_dataframe(r).columns.tolist())
