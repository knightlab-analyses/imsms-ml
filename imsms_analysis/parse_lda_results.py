import pandas as pd
import matplotlib.pyplot as plt

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


# df = read_species()
# df = read_pathways()
df = read_vfdb()
df = df.sort_values("Accuracy", axis=0, ascending=False)
# print(df)
# df = df * 183
# bins = range(184)
# df.hist(column="Accuracy", bins=bins)
df.hist(column="Accuracy")
plt.title("Univariate LDA Result Histogram")
plt.xlabel("Accuracy")
plt.ylabel("Count")
plt.show()