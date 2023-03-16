import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import sqlite3
import numpy as np
from scipy.stats import binom
matplotlib.use('TkAgg')

def read_species():
    df = pd.read_csv("plottedResults/univariate_zebra_lda_all.csv", index_col=0)
    # df = pd.read_csv("plottedResults/all_species_univariate_lda.csv", index_col=0)
    df = df.transpose()
    df.columns = ["Accuracy"]

    # Remove the mixed linear model and probstel genera results
    # df = df.drop(["Species-T1-test",
    #              "Species-T2-test",
    #              "Species-T3-test",
    #              "Species-T4-test",
    #              "Species-T5-test",
    #              "Species-T6-test",
    #              "Species-T7-test",
    #              "Species-T8-test",
    #              "Species-T9-test",
    #              "Species-T10-test",
    #              "Probstel-test",
    #              "Akkermansia239934-test",
    #              "Bifidobacterium1678-test",
    #              "Bilophila35832-test",
    #              "Blautia572511-test",
    #              "Butyricimonas574697-test",
    #              "Christensenella990721-test",
    #              "Coprococcus33042-test",
    #              "Desulfovibrio872-test",
    #              "Faecalibacterium216851-test",
    #              "Haemophilus724-test",
    #              "Methanobrevibacter2172-test",
    #              "Paraprevotella577309-test",
    #              "Pedobacter84567-test",
    #              "Pseudomonas286-test",
    #              "Slackia84108-test"])
    print(df)
    print(df.shape)
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

def add_info(df):
    names = []
    conn = sqlite3.connect("mimics.db")
    c = conn.cursor()

    for s in df.index:
        ss = s.split("-")
        genome_id = ss[0]
        c.execute("SELECT species from genome where genome_id=?", (genome_id,))
        r = c.fetchone()
        names.append(r[0])

    df["species"] = names
    return df

df = read_species()
df_mimics = read_top_mimics()
df_akk = read_akkermansia()
df_lit = read_literature()

df = add_info(df)

# df = read_pathways()
# df = read_vfdb()
# df = df.sort_values("Accuracy", axis=0, ascending=False)

print("PASSING")
df['count'] = df['Accuracy'] * 183
df_pass = df[df['Accuracy'] > (110/183)]
dfpass = df_pass.sort_values(by='Accuracy', ascending=False)
print(df_pass)
df_pass.to_csv("pass_110.csv")
print("END PASSING")


# print(df)
df = df * 183
bins = range(184)
df.hist(column="Accuracy", bins=bins)
# df.hist(column="Accuracy")
plt.title("Univariate LDA Result Histogram")
plt.xlabel("# Correct (Out of 183)")
plt.ylabel("Count")

plt.axvline(103, color='g', label="p=.05 (single classifier)", ls="--")
plt.axvline(117, color='g', label="p=.05 (Bonferroni adj)", ls="-.") # With Zebra Filter

binomial_dist = binom.pmf(np.arange(0,184), 183, 0.5) * 889
plt.axvline(91.5, color='gray', ls=':')
plt.plot(np.arange(0,184), binomial_dist, color='red', linestyle='-.')


# plt.axvline(120, color='g', label="p=.05 (multiple test correction)", ls="-.") # All Unfiltered

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

fig, axes = plt.subplots(3, 4, sharex=True, sharey=True)
print(axes)
genus_i = 0
for genus in ["Akkermansia"]:  # genera_map:
    # plt.subplot(3,4,genus_i + 1)
    # print(genus)
    # continue
    ax = axes[genus_i // 4][genus_i % 4]

    fig, ax = plt.subplots()

    df.hist(column="Accuracy", bins=bins, ax=ax)
    genus_i += 1
    # if genus_i in [9,10,11,12,21,22,23,24]:
    ax.set_xlabel("# Correct (Out of 183)")
    ax.set_xlim(60,123)
    if genus_i in [1,5,9,13,17,21]:
        ax.set_ylabel("Count")
    ax.axvline(103, color='g', label="p=.05", ls="--")

    num_pass = 0
    total_count = 0
    for row in genera_map[genus]:
        total_count += 1
        print(row.name, row[0])
        if row["Accuracy"] > 103/183:
            ax.axvline(row["Accuracy"] * 183, color="green")#, label=row.name)
            num_pass += 1
        else:
            ax.axvline(row["Accuracy"] * 183, color="grey")

    ax.title.set_text(genus + " " + str(num_pass) + "/" + str(total_count))

    ax.legend()
    plt.suptitle("Univariate LDA")
    if genus_i % 12 == 0:
        plt.show()
        fig, axes = plt.subplots(3, 4, sharex=True, sharey=True)
        genus_i = 0
plt.show()
