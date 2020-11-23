import pandas as pd
from imsms_analysis.preprocessing.id_parsing import _parse_household_id
import seaborn as sns
import matplotlib.pyplot as plt


def parse_disease_state(sample_id: str):
    return sample_id[4] == '1'


def draw_hist(name, df):
    df = df.copy()
    df["sum"] = df.sum(axis=1)
    print(df)

    df = df.sort_values(by="sum", axis=0, ascending=False)
    print(df)

    df.hist(column="sum", bins=df["sum"].max())
    plt.title(name + " - Histogram: SNPs Contained by X Samples")
    plt.xlabel("#Samples")
    plt.ylabel("#SNPs contained in X Samples")
    # plt.savefig("../../plots/snp_clustermaps/" + name + "-hist.png")
    plt.show()


def draw_clustermap(name, df, MIN_SAMPLES_PER_SNP=21, MIN_SNPS_PER_SAMPLE=1):
    """
    Filter df for snps that appear in at least MIN_SAMPLES_PER_SNP samples,
    Then for samples that have at least MIN_SNPS_PER_SAMPLE snps.

    If you set MIN_SNPS_PER_SAMPLE to 1, then it will hide all the samples
    that don't have snps for this species (many species only occur in some
    small subset of samples)
    """
    df = df.copy()
    df["sum"] = df.sum(axis=1)
    df = df[df["sum"] >= MIN_SAMPLES_PER_SNP]
    print(df)

    df = df.drop(["sum"], axis=1)

    df = df.transpose()
    df["sum"] = df.sum(axis=1)
    df = df[df["sum"] >= MIN_SNPS_PER_SAMPLE]
    print(df)
    df = df.drop(["sum"], axis=1)

    cluster_grid = sns.clustermap(df, metric="hamming")

    # print("Col")
    # print(cluster_grid.dendrogram_col.dendrogram)
    # print("Linkage")
    # print(cluster_grid.dendrogram_col.linkage)
    # print("Row")
    # print(cluster_grid.dendrogram_row.dendrogram)
    # print("Linkage")
    # print(cluster_grid.dendrogram_row.linkage)
    plt.title(name)
    plt.savefig("../../plots/snp_clustermaps/" + name + ".png")
    plt.show()


def split_species(df, species):
    # Keep only columns (SNPS) that relate to this species
    df = df[df.index.str.startswith(specie)]
    return df


# Read the csv
df = pd.read_csv("snps_50_samples_presence.txt", sep='\t')
df = df.sort_index()
print(df)
print(df.columns.tolist())

# Split the dataframe into two parts, those with MS and healthy controls
df_ms = df.filter(axis=1, regex="....1.....")
df_control = df.filter(axis=1, regex="....2.....")
print(df_ms.columns.tolist())
print(df_control.columns.tolist())

species = set([])
for r in df.index:
    prefix = r.split("_")[0:3]
    species.add("_".join(prefix))

for specie in sorted(list(species)):
    for d in [df, df_ms, df_control]:
        spec_df = split_species(d, specie)
        draw_hist(specie, spec_df)
        # draw_clustermap(specie, spec_df)
