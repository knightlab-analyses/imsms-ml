import json
import biom
from biom import load_table
from qiime2 import Artifact, Metadata
from sklearn.model_selection import ParameterGrid
import q2_mlab
import pandas as pd
import preprocessing_pipeline

biom_table = load_table("./dataset/biom/combined-genus.biom")
table = Artifact.import_data("FeatureTable[Frequency]", biom_table)
df = table.view(pd.DataFrame)
df = preprocessing_pipeline.fix_input(df, verbose=False)
table = Artifact.import_data("FeatureTable[Frequency]", df)

metadata = Metadata.load('./dataset/metadata/iMSMS_1140samples_metadata.tsv')
metadata = metadata.to_dataframe()

# distance_matrix = Artifact.load(os.path.join(TEST_DIR, 'aitchison_distance_matrix.qza'))

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

final_biom = table.view(biom.Table)

results = q2_mlab.unit_benchmark(
    table=final_biom,
    metadata=metadata["age"],
    algorithm="LinearSVR",
    params=reg_params,
    n_jobs=1,
    distance_matrix=None
)

# In[17]:


table.view(biom.Table).shape

# In[22]:


results

# In[25]:


results.head(12)

# In[29]:


results.CV_IDX.value_counts()

# In[ ]:
