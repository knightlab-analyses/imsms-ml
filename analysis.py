import json
import biom
from biom import load_table
from qiime2 import Artifact, Metadata
from sklearn.model_selection import ParameterGrid
import q2_mlab
import pandas as pd
import preprocessing_pipeline

# Load sequence DataFrame
from common import plotter
from state.pipeline_state import PipelineState

biom_table = load_table("./dataset/biom/combined-species.biom")
table = Artifact.import_data("FeatureTable[Frequency]", biom_table)
df = table.view(pd.DataFrame)

column_labels = biom_table.metadata_to_dataframe(axis="observation")
print(column_labels)
feature_set = pd.read_csv("./dataset/feature_sets/just_austwickia.tsv",
                          sep='\t',
                          index_col='ID',
                          dtype=str)
feature_set.index = feature_set.index.astype(str)  # Dumb Panda ignores type

# Load metadata DataFrame
metadata = Metadata.load('./dataset/metadata/iMSMS_1140samples_metadata.tsv')
meta_df = metadata.to_dataframe()

state = PipelineState(df, meta_df, None)
# Run Preprocessing
state = preprocessing_pipeline.process(
    state,
    restricted_feature_set=feature_set.index.tolist(),
    verbose=False
)

df = state.df
meta_df = state.meta_df
target = state.target

# Shuffle the data so the machine learning can't learn anything based on order
df = df.sample(frac=1)

# Target and df order must match.  Argh.
df['target'] = target
target = df['target']
df = df.drop(['target'], axis=1)

# plotter.simple_swarm(df, meta_df, "239935", "disease")

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
