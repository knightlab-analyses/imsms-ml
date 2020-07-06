import json
import biom
from biom import load_table
from qiime2 import Artifact, Metadata
from sklearn.model_selection import ParameterGrid
import q2_mlab
import pandas as pd
import preprocessing_pipeline

# Load sequence DataFrame
biom_table = load_table("./dataset/biom/combined-reaction2pathway.biom")
table = Artifact.import_data("FeatureTable[Frequency]", biom_table)
df = table.view(pd.DataFrame)

# print(biom_table.metadata_to_dataframe(axis="observation"))
# print(df)

# Load metadata DataFrame
metadata = Metadata.load('./dataset/metadata/iMSMS_1140samples_metadata.tsv')
meta_df = metadata.to_dataframe()

# Preprocess sequence dataframe
df = preprocessing_pipeline.process_biom(df, meta_df, verbose=False)
# Preprocess metadata dataframe
meta_df = preprocessing_pipeline.process_metadata(meta_df,
                                                  df.index, verbose=False)
# Build target column
df = preprocessing_pipeline.build_target_column(df, meta_df, verbose=False)

# Shuffle the data so the machine learning can't learn anything based on order
df = df.sample(frac=1)

# Split out the target column (order must match that of df in the current ver)
target = df['target']

# -REMOVE the target column from df, unless you want 100% accuracy :P-
df = df.drop('target', axis=1)

# Convert necessary types for regression-benchmarking
final_biom = Artifact.import_data("FeatureTable[Frequency]", df)\
    .view(biom.Table)

# LinearSVR_grids = {'C': [1e-4, 1e-3, 1e-2, 1e-1, 1e1,
#                             1e2, 1e3, 1e4, 1e5, 1e6, 1e7],
#                     'epsilon':[1e-2, 1e-1, 0, 1],
#                     'loss': ['squared_epsilon_insensitive',
#                             'epsilon_insensitive'],
#                     'random_state': [2018]
# }

RandomForestClassifier_grids = {
    # Define a grid here from sklearn api
    'random_state': [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
}

LinearSVC_grids = {'penalty': {'l2'},
                   'tol': [1e-4, 1e-2, 1e-1],
                   'loss': ['hinge', 'squared_hinge'],
                   'random_state': [2018]
                   }

reg_params = json.dumps(list(ParameterGrid(RandomForestClassifier_grids))[0])

results = q2_mlab.unit_benchmark(
    table=final_biom,
    metadata=target,
    algorithm="RandomForestClassifier",
    params=reg_params,
    distance_matrix=None
)

print(results)
print(results.columns)
for col in ["ACCURACY", "AUPRC", "AUROC", "F1"]:
    print("Max", col, ":", max(results[col]))
