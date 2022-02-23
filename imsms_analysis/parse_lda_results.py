import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

def read_species():
    df = pd.read_csv("plottedResults/all_species_univariate_lda.csv", index_col=0)
    df = df.transpose()
    df.columns = ["Accuracy"]

    # Remove the mixed linear model and probstel genera results
    df = df.drop(["Species-T1-test",
                 "Species-T2-test",
                 "Species-T3-test",
                 "Species-T4-test",
                 "Species-T5-test",
                 "Species-T6-test",
                 "Species-T7-test",
                 "Species-T8-test",
                 "Species-T9-test",
                 "Species-T10-test",
                 "Probstel-test",
                 "Akkermansia239934-test",
                 "Bifidobacterium1678-test",
                 "Bilophila35832-test",
                 "Blautia572511-test",
                 "Butyricimonas574697-test",
                 "Christensenella990721-test",
                 "Coprococcus33042-test",
                 "Desulfovibrio872-test",
                 "Faecalibacterium216851-test",
                 "Haemophilus724-test",
                 "Methanobrevibacter2172-test",
                 "Paraprevotella577309-test",
                 "Pedobacter84567-test",
                 "Pseudomonas286-test",
                 "Slackia84108-test"])
    return df


def read_pathways():
    df = pd.read_csv("plottedResults/pathways_lda_all.csv", index_col=0)
    df = df.transpose()
    df.columns = ["Accuracy"]
    return df


def read_vfdb():
    df = pd.read_csv("plottedResults/vfdb_lda_all.csv", index_col=0)
    df = df.transpose()
    df.columns = ["Accuracy"]
    return df


def read_akkermansia():
    df = pd.read_csv("plottedResults/lda_akkermansia.csv", index_col=0)
    df = df.transpose()
    df.columns = ["Accuracy"]
    return df

def read_top_mimics():
    df = pd.read_csv("plottedResults/lda_top_mimics.csv", index_col=0)
    df = df.transpose()
    df.columns = ["Accuracy"]
    return df

def read_literature():
    df = pd.read_csv("plottedResults/lda_literature_search.csv", index_col=0)
    df = df.transpose()
    df.columns = ["Accuracy"]
    return df


df = read_species()
df_mimics = read_top_mimics()
df_akk = read_akkermansia()
df_lit = read_literature()

# df = read_pathways()
# df = read_vfdb()
df = df.sort_values("Accuracy", axis=0, ascending=False)
# print(df)
df = df * 183
bins = range(184)
df.hist(column="Accuracy", bins=bins)
# df.hist(column="Accuracy")
plt.title("Univariate LDA Result Histogram")
plt.xlabel("# Correct (Out of 183)")
plt.ylabel("Count")

plt.axvline(103, color='g', label="p=.05 (single classifier)", ls="--")
plt.axvline(120, color='g', label="p=.05 (multiple test correction)", ls="-.")
# plt.axvline(df_akk.loc["Akkermansia sp. CAG:3441262691-test"]["Accuracy"] * 183, color='r', label="Akkermansia sp. CAG:344")
# plt.axvline(df_akk.loc["Akkermansia muciniphila CAG:1541263034-test"]["Accuracy"] * 183, color="g", label="Akkermansia muciniphila CAG:154")
# plt.axvline(df_akk.loc["Akkermansia muciniphila (239935)239935-test"]["Accuracy"] * 183, color="y", label="Akkermansia muciniphila (239935)")
# for index, row in df_mimics.iterrows():
#     print(row.name, row[0])
#     if not "Akkermansia" in row.name:
#         plt.axvline(row["Accuracy"] * 183, color="grey", label=row.name)

plt.legend()
plt.show()
genera_map = defaultdict(list)

for index, row in df_lit.iterrows():
    genera_map[row.name.split()[0]].append(row)

for genus in genera_map:
    print(genus)
    continue
    df.hist(column="Accuracy", bins=bins)
    plt.title("Univariate LDA: " + genus)
    plt.xlabel("# Correct (Out of 183)")
    plt.ylabel("Count")
    plt.axvline(103, color='g', label="p=.05 (single classifier)", ls="--")

    for row in genera_map[genus]:
        print(row.name, row[0])
        if row["Accuracy"] > 103/183:
            plt.axvline(row["Accuracy"] * 183, color="green", label=row.name)
        else:
            plt.axvline(row["Accuracy"] * 183, color="grey")
    plt.legend()
    plt.show()
