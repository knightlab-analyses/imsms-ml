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
# df = pd.read_csv("./results/RandomizedTestSetsGenusAndSpecies_all.csv", sep=',')

# Alternate species,genus
# value_vars1 = []
# for i in range(25):
#     value_vars1.append("Raw-species" + str(i))
#     value_vars1.append("Raw-genus" + str(i))
# # All species then all genus
# value_vars2 = []
# for i in range(25):
#     value_vars2.append("Raw-species" + str(i))
# for i in range(25):
#     value_vars2.append("Raw-genus" + str(i))
#
# df = pd.melt(df,
#              value_vars=value_vars1,
#              # value_vars=value_vars2,
#              var_name="Randomized Test Set",
#              value_name="Accuracy")

df = pd.read_csv("./results/paired_multiple_test_sets.csv", sep=',')
df = pd.melt(df,
             value_vars=df.columns.tolist()[1:],
             var_name="Randomized Test Set",
             value_name="Accuracy")

# df = pd.read_csv("./results/RandomizedTestSetsGenusAndSpecies_all.csv", sep=',')
# value_vars1 = ["Raw-species0", "Raw-genus0"]
# df = pd.melt(df,
#              value_vars=value_vars1,
#              # value_vars=value_vars2,
#              var_name="Randomized Test Set",
#              value_name="Accuracy")


sns.set(style="ticks")
g = sns.catplot(x="Randomized Test Set", y="Accuracy", data=df)
ax = g.ax
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
ax.axhline(.5, ls='--')
# ax2.axhline(30, ls='--')
plt.tight_layout()
plt.show()