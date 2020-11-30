import pandas as pd
from scipy.cluster.hierarchy import fcluster

from imsms_analysis.preprocessing.id_parsing import _parse_household_id
import seaborn as sns
import matplotlib.pyplot as plt


NUM_CLUSTERS = {
    "Akkermansia_muciniphila_55290": 4,
    "Alistipes_onderdonkii_55464": 5,
    "Alistipes_putredinis_61533": 8,
    "Bacteroides_caccae_53434": 13,
    "Bacteroides_eggerthii_54457": 3,
    "Bacteroides_massiliensis_44749": 9,
    "Bacteroides_ovatus_58035": 4,
    "Bacteroides_stercoris_56735": 4,
    "Bacteroides_uniformis_57318": 1,
    "Bacteroides_vulgatus_57955": 5,
    "Escherichia_coli_58110": 2,
    "Eubacterium_rectale_56927": 2,
    "Prevotella_copri_61740": 2,
    "Ruminococcus_bromii_62047": 2
}


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


def overlay_clusters(ax, seaborn_cluster_order, cluster_df):
    counts = cluster_df["group"].value_counts()
    print(counts)
    sum = 0
    ax.axhline(sum)
    for g in seaborn_cluster_order:
        sum += counts[g]
        ax.axhline(sum)
        print("Divider:", sum)


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
    ax = cluster_grid.ax_heatmap

    if specie == "Akkermansia_muciniphila_55290":
        print(dir(cluster_grid))

    # print("Col")
    # print(cluster_grid.dendrogram_col.dendrogram)
    # print("Linkage")
    # print(cluster_grid.dendrogram_col.linkage)
    print("Row")
    print(cluster_grid.dendrogram_row.dendrogram)
    print("Linkage")
    print(cluster_grid.dendrogram_row.linkage)
    print("Reordered Indexes")
    print(cluster_grid.dendrogram_row.reordered_ind)

    flat_group = fcluster(cluster_grid.dendrogram_row.linkage,
                  NUM_CLUSTERS[name],
                  criterion='maxclust')

    print("Flattened")
    print(flat_group)

    sample_id = df.index.tolist()
    order = cluster_grid.dendrogram_row.reordered_ind
    ordered_group = list(flat_group)
    for i in range(len(ordered_group)):
        ordered_group[i] = flat_group[order[i]]
    ordered_sample = list(sample_id)
    for i in range(len(sample_id)):
        ordered_sample[i] = sample_id[order[i]]
    print("Did it work?")
    print(ordered_sample)
    print(ordered_group)

    cluster_df = pd.DataFrame(data={"group": ordered_group}, index=ordered_sample)
    print(cluster_df)
    for g in range(1, NUM_CLUSTERS[name] + 1):
        cluster_df["G"+str(g)] = cluster_df["group"] == g
        cluster_df["G"+str(g)] = cluster_df["G"+str(g)].astype(int)
    print(cluster_df)
    cluster_df.to_csv("../../plots/snp_clustermaps/" + name + ".csv")

    # seaborn display isn't always in group order.
    stupid_group_hack = []
    for g in ordered_group:
        if len(stupid_group_hack) == 0 or stupid_group_hack[-1] != g:
            stupid_group_hack.append(g)
    overlay_clusters(ax, stupid_group_hack, cluster_df)

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
    # if specie < "Bacteroides_massiliensis_44749":
    #     continue
    if specie != "Bacteroides_vulgatus_57955":
        # This one takes sooo lonnnggggg
        continue
    d = df
    # for d in [df, df_ms, df_control]:
    spec_df = split_species(d, specie)
    # draw_hist(specie, spec_df)
    draw_clustermap(specie, spec_df)
