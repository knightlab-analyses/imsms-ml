import pandas as pd
from imsms_analysis.preprocessing.id_parsing import _parse_household_id
import seaborn as sns
import matplotlib.pyplot as plt


def parse_disease_state(sample_id: str):
    return sample_id[4] == '1'


df = pd.read_csv("snps_50_samples_presence.txt", sep='\t')
df = df.sort_index()
print(df)
print(df.columns.tolist())

df_ms = df.filter(axis=1, regex="....1.....")
df_control = df.filter(axis=1, regex="....2.....")
print(df_ms.columns.tolist())
print(df_control.columns.tolist())

df = df[df.index.str.startswith("Akkermansia_muciniphila_55290")]
print(df)
print(df.columns.tolist())

df["sum"] = df.sum(axis=1)
print(df)

df = df.sort_values(by="sum", axis=0, ascending=False)
print(df)

df.hist(column="sum", bins=df["sum"].max())
plt.show()

# df = df[df["sum"] > 5]
# print(df)

# df = df[df["sum"] > 10]
# print(df)
#
df = df[df["sum"] > 20]
print(df)

df = df.drop(["sum"], axis=1)

df = df.transpose()
df["sum"] = df.sum(axis=1)
df = df[df["sum"] > 0]
print(df)
df = df.drop(["sum"], axis=1)

cluster_grid = sns.clustermap(df, metric="hamming")

print("Col")
print(cluster_grid.dendrogram_col.dendrogram)
print("Linkage")
print(cluster_grid.dendrogram_col.linkage)
print("Row")
print(cluster_grid.dendrogram_row.dendrogram)
print("Linkage")
print(cluster_grid.dendrogram_row.linkage)
plt.show()

