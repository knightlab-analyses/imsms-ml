import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Paired vs unpaired
# paired = pd.read_csv("./results/RawSpeciesPaired.csv", sep=',')
# unpaired = pd.read_csv("./results/RawSpeciesUnpaired.csv", sep=',')
#
# paired = paired['TestAccuracy']
# unpaired = unpaired['TestAccuracy']
#
# paired = paired.rename("Paired (Concatenation)")
# unpaired = unpaired.rename("Unpaired")
#
# df = pd.concat([paired, unpaired], axis=1)
# df = pd.melt(df, value_vars=['Paired (Concatenation)', "Unpaired"],
#              var_name="Feature Set",
#              value_name="Accuracy")
#
# sns.set(style="ticks")
# g = sns.catplot(x="Feature Set", y="Accuracy", data=df)
# plt.show()


# Phylogeny Level
# df = pd.read_csv("./results/phylogeny_level_all.csv", sep=',')
#
#
# df = pd.melt(df,
#              value_vars=["Phylum", "Class", "Order",
#                          "Family", "Genus", "Species"],
#              var_name="Feature Set",
#              value_name="Accuracy")
#
# sns.set(style="ticks")
# g = sns.catplot(x="Feature Set", y="Accuracy", data=df)
# plt.show()


# Akkermansia
# df = pd.read_csv("./results/Akkermansia muciniphila.csv", sep=',')
#
# df = pd.melt(df,
#              value_vars=["Akkermansia muciniphila"],
#              var_name="Feature Set",
#              value_name="Accuracy")
#
# sns.set(style="ticks")
# g = sns.catplot(x="Feature Set", y="Accuracy", data=df)
# plt.show()


# Probstel Lit Review
# df = pd.read_csv("./results/probstel_all.csv", sep=',')
#
# df = pd.melt(df,
#              value_vars=[
#                  "Pröbstel",
#                  "Genus",
#                  "Akkermansia",
#                  "Bifidobacterium",
#                  "Bilophila",
#                  "Blautia",
#                  "Butyricimonas",
#                  "Christensenella",
#                  "Coprococcus",
#                  "Desulfovibrio",
#                  "Faecalibacterium",
#                  "Haemophilus",
#                  "Methanobrevibacter",
#                  "Paraprevotella",
#                  "Pedobacter",
#                  "Pseudomonas",
#                  "Slackia"
#              ],
#              var_name="Feature Set",
#              value_name="Accuracy")


# Randomized Test Set Tests
df = pd.read_csv("./results/RandomizedTestSetsGenusAndSpecies_all.csv", sep=',')

df = pd.melt(df,
             value_vars=[
                 "Raw-species0",
                 "Raw-genus0",
                 "Raw-species1",
                 "Raw-genus1",
                 "Raw-species2",
                 "Raw-genus2",
                 "Raw-species3",
                 "Raw-genus3",
                 "Raw-species4",
                 "Raw-genus4",
                 "Raw-species5",
                 "Raw-genus5",
                 "Raw-species6",
                 "Raw-genus6",
                 "Raw-species7",
                 "Raw-genus7",
                 "Raw-species8",
                 "Raw-genus8",
                 "Raw-species9",
                 "Raw-genus9",
                 "Raw-species10",
                 "Raw-genus10",
                 "Raw-species11",
                 "Raw-genus11",
                 "Raw-species12",
                 "Raw-genus12",
                 "Raw-species13",
                 "Raw-genus13",
                 "Raw-species14",
                 "Raw-genus14",
                 "Raw-species15",
                 "Raw-genus15",
                 "Raw-species16",
                 "Raw-genus16",
                 "Raw-species17",
                 "Raw-genus17",
                 "Raw-species18",
                 "Raw-genus18",
                 "Raw-species19",
                 "Raw-genus19",
                 "Raw-species20",
                 "Raw-genus20",
                 "Raw-species21",
                 "Raw-genus21",
                 "Raw-species22",
                 "Raw-genus22",
                 "Raw-species23",
                 "Raw-genus23",
                 "Raw-species24",
                 "Raw-genus24",

             ],
             var_name="Randomized Test Set",
             value_name="Accuracy")


sns.set(style="ticks")
g = sns.catplot(x="Randomized Test Set", y="Accuracy", data=df)
ax = g.ax
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.axhline(.5, ls='--')
# ax2.axhline(30, ls='--')
plt.tight_layout()
plt.show()