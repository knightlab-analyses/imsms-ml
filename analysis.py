import json
import biom
from biom import load_table
from qiime2 import Artifact, Metadata
from sklearn.model_selection import ParameterGrid
import q2_mlab
import pandas as pd
import preprocessing_pipeline

# Load sequence DataFrame
biom_table = load_table("./dataset/biom/combined-genus.biom")
table = Artifact.import_data("FeatureTable[Frequency]", biom_table)
df = table.view(pd.DataFrame)

# Load metadata DataFrame
metadata = Metadata.load('./dataset/metadata/iMSMS_1140samples_metadata.tsv')
meta_df = metadata.to_dataframe()

# Preprocess sequence dataframe
df = preprocessing_pipeline.process_biom(df, meta_df.index, verbose=False)
# Preprocess metadata dataframe
meta_df = preprocessing_pipeline.process_metadata(meta_df, df.index, verbose=False)

# Convert necessary types for regression-benchmarking
final_biom = Artifact.import_data("FeatureTable[Frequency]", df)\
    .view(biom.Table)


LinearSVR_grids = {'C': [1e-4, 1e-3, 1e-2, 1e-1, 1e1,
                            1e2, 1e3, 1e4, 1e5, 1e6, 1e7],
                    'epsilon':[1e-2, 1e-1, 0, 1],
                    'loss': ['squared_epsilon_insensitive',
                            'epsilon_insensitive'],
                    'random_state': [2018]
}

# RandomForestClassifier_grids: {
#         # Define a grid here from sklearn api
# }

# LinearSVC_grids = {'penalty': {'l1', 'l2'},
#                    'tol': [1e-4, 1e-2, 1e-1],
#                    'loss': ['hinge', 'squared_hinge'],
#                    'random_state': [2018]
#                    }

reg_params = json.dumps(list(ParameterGrid(LinearSVR_grids))[0])

target = meta_df.apply(lambda row: 1 if row["disease"] == "MS" else 0, axis=1)
print(target)

results = q2_mlab.unit_benchmark(
    table=final_biom,
    metadata=target,
    algorithm="LinearSVR",
    params=reg_params,
    n_jobs=1,
    distance_matrix=None
)

print(results)