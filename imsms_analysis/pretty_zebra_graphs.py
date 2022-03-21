import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

matplotlib.use("TkAgg")

inputs = [
    ("./plottedResults/finrisk_zebra_aitchison_sex_rarefy.tsv", "Finrisk Aitchison Male/Female"),
    ("./plottedResults/finrisk_zebra_jaccard_sex_rarefy.tsv", "Finrisk Jaccard Male/Female"),
    # ("./plottedResults/imsms_zebra_aitchison_sex.tsv", "iMSMS Aitchison Male/Female"),
    # ("./plottedResults/imsms_zebra_jaccard_sex.tsv", "iMSMS Jaccard Male/Female"),
    # ("./plottedResults/sol_zebra_aitchison_sex.tsv", "SOL Aitchison Male/Female"),
    # ("./plottedResults/sol_zebra_jaccard_sex.tsv", "SOL Jaccard Male/Female"),
    # ("./plottedResults/imsms_controls_zebra_aitchison_sex.tsv", "iMSMS (Ctrl Only) Aitchison Male/Female"),
    # ("./plottedResults/imsms_controls_zebra_jaccard_sex.tsv", "iMSMS (Ctrl Only) Jaccard Male/Female")
    # ("./plottedResults/imsms_zebra_aitchison_MS.tsv", "iMSMS Aitchison MS/Control"),
    # ("./plottedResults/imsms_zebra_jaccard_MS.tsv", "iMSMS Jaccard MS/Control"),
    # ("./plottedResults/finrisk_zebra_aitchison_FR02_100A.tsv", "Finrisk Aitchison Lactose Free/Control"),
    # ("./plottedResults/finrisk_zebra_jaccard_FR02_100A.tsv", "Finrisk Jaccard Lactose Free/Control"),
]

pval_range = (0,0.5)
pseudo_f_range = (0,6)

def plotit(file, title, index, ax):
    df = pd.read_csv(file, sep='\t')
    analysis_split = df['analysis_name'].str.split("-", expand=True)
    analysis_split.columns = ["zebra", "rarefy"]
    print(analysis_split)
    cov_ratio = analysis_split["zebra"].str.split(":", expand=True)
    cov_ratio.columns=['zebra', 'ratio']

    df['zebra'] = cov_ratio['ratio']
    df['zebra'] = pd.to_numeric(df['zebra'])
    df['rarefy'] = analysis_split['rarefy']

    ax2 = ax.twinx()
    for rarefy_label,dfr in df.groupby(df['rarefy']):
        y_axis = 'pseudo-F (' + rarefy_label + ')'
        dfr = dfr.rename(columns={'pseudo-F': y_axis})
        # Plot the first x and y axes:
        dfr.plot.scatter(x = 'zebra', y = 'pvalue', ax = ax, legend=False, ylim=pval_range)
        dfr.plot.line(x = 'zebra', y = 'pvalue', ax = ax, legend=False, ylim=pval_range)
        dfr.plot.scatter(x = 'zebra', y = y_axis, ax = ax2, secondary_y = False, ylim=pseudo_f_range)
        dfr.plot.line(x = 'zebra', y = y_axis, ax = ax2, secondary_y = False, ylim=pseudo_f_range)

    plt.xticks([0.2 * x for x in range(6)])
    ax.axhline(.05, ls='--', color='orange')
    ax.axhline(.005, ls='--', color='orange')
    ax2.set_ylabel("pseudo-F")
    ax.set_xlabel("Zebra Coverage Threshold")
    plt.title(title)

    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend([handles[1],handles[0],handles[2]], [labels[1],labels[0],labels[2]])

    plt.suptitle("Gender Separation by Permanova Across Coverage Thresholds")


if __name__=="__main__":
    fig, axes = plt.subplots(nrows=1, ncols=2)  # Create the figure and axes object
    for i in range(len(inputs)):
        # plotit(inputs[i][0], inputs[i][1], i, axes[i // 2, i % 2]) # When nrows > 1
        plotit(inputs[i][0], inputs[i][1], i, axes[i % 2])
    plt.tight_layout()
    plt.show()
