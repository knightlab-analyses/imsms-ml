import math

from imsms_analysis.common.PairwisePearson import pairwise_pearson
from imsms_analysis.common.table_info import BiomTable, CSVTable
from imsms_analysis.common.woltka_metadata import filter_and_sort_df

import os
import seaborn as sns
from os import path
import pandas as pd
import numpy as np
from datetime import date
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt, animation

from imsms_analysis.preprocessing.id_parsing import _parse_sample_id

from skbio import DistanceMatrix
from qiime2 import Artifact, Metadata, Visualization
from q2_feature_table import rarefy

from imsms_analysis.analysis_runner import SerialRunner, DryRunner, \
    ParallelRunner, SavePreprocessedTables
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_filter import ZebraFilter
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
import pandas as pd

from qiime2.plugins.diversity.methods import alpha, beta
from qiime2.plugins.diversity.visualizers import alpha_group_significance
from qiime2.plugins.diversity.visualizers import beta_group_significance

import skbio
import biom


def load_input():
    df = BiomTable("none", biom_filepath=[
        "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
        "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
        "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
    ]).load_dataframe()

    df = df[df.index.str.startswith("11326.Q.FMT")]
    def remap_indices(idx):
        # Argh, someone has fat fingers and typed two periods
        idx = idx.replace("..", ".")
        # Argh, sample index (5th column) has duplicates and gaps, sort by time instead.
        # Also they'd prefer to rename 001C (the control sample) to 004
        ss = idx.split(".")
        if ss[3] == "001C":
            ss[3] = "004"
        idx = ".".join([ss[3], ss[5], ss[6], ss[7]])

        return idx

    df.index = df.index.map(remap_indices)
    df = df.sort_index()

    meta_df = pd.read_csv("./dataset/metadata/patient_info_fmt.csv")
    new_index = []
    for i, row in meta_df.iterrows():
        ss = row["Date"].split("/")
        yyyy = "20" + ss[2]
        mm = ss[0].zfill(2)
        dd = ss[1].zfill(2)

        pn = row["Patient Number"]
        if pn == "001C":
            pn = "004"
        new_index.append(".".join([pn, yyyy, mm, dd]))

    meta_df.index = new_index
    print(meta_df)

    return df, meta_df


def build_fake_treatment(df):
    # TODO FIXME HACK:  Ask Xiaohui for a better list.
    # The metadata dates are useless,
    # here's a rough guess based on alpha diversity
    fake_meta = ["PRE"] * 2 + ["AB"] * 1 + ["POST"] * 7 + \
                ["PRE"] * 1 + ["AB"] * 1 + ["POST"] * 8 + \
                ["PRE"] * 1 + ["AB"] * 1 + ["POST"] * 7 + \
                ["CNTL"] * 5 + \
                ["PRE"] * 1 + \
                ["PRE"] * 2 + ["AB"] * 1 + ["POST"] * 5
    treatment = pd.Series(fake_meta, index=df.index)
    return treatment


def do_alpha_plots(df):
    df_table = Artifact.import_data("FeatureTable[Frequency]", df)
    alpha_result = alpha(table=df_table, metric='shannon')
    alpha_diversity = alpha_result.alpha_diversity
    series = alpha_diversity.view(pd.Series)

    print(series)

    vals_dict = {}
    xs = []
    ys = []
    last_subj = None
    for i, y in series.items():
        ss = i.split('.')
        subj = ss[0]
        x = date(int(ss[-3]), int(ss[-2]), int(ss[-1]))
        if subj != last_subj:
            if last_subj is not None:
                vals_dict[last_subj] = (xs, ys)
                xs = []
                ys = []
            last_subj = subj
        xs.append(x)
        ys.append(y)
    vals_dict[last_subj] = (xs,ys)

    for subj in vals_dict:
        xs,ys = vals_dict[subj]
        plt.plot(xs, ys, label=subj, marker='o')
        plt.title("Alpha Diversity (Shannon)")
    plt.legend()
    ticks = [date(2019,1,1), date(2020,1,1), date(2021,1,1)]
    plt.xticks(ticks, [str(t) for t in ticks])
    plt.show()


def do_beta_plots(df, treatment):
    df_table = Artifact.import_data("FeatureTable[Frequency]", df)
    df_prepost = df[treatment.isin(["PRE", "POST"])]
    df_table_prepost = Artifact.import_data("FeatureTable[Frequency]", df_prepost)

    for metric in ['aitchison']:
        beta_result = beta(table=df_table, metric=metric, pseudocount=1, n_jobs=-2)
    dist_mat = beta_result.distance_matrix.view(DistanceMatrix)

    beta_result_prepost = beta(table=df_table_prepost, metric=metric, pseudocount=1, n_jobs=-2)
    dist_mat_prepost = beta_result_prepost.distance_matrix.view(DistanceMatrix)

    metric_df = dist_mat.to_data_frame()
    print(metric_df)
    print("MAX")
    vmin = 0
    vmax = math.ceil(metric_df.max().max())

    sample_index = 1
    new_cols = []
    old_ss0 = None
    for c in metric_df.columns:
        ss = c.split(".")
        if ss[0] != old_ss0:
            sample_index = 1
            old_ss0 = ss[0]
        new_cols.append(ss[0] + "." + str(sample_index).zfill(2))
        sample_index += 1

    print(new_cols)

    metric_df.index = new_cols
    metric_df.columns = new_cols
    sns.heatmap(metric_df, vmin=vmin, vmax=vmax)
    plt.title("Beta Diversity (" + metric + ")")
    plt.show()

    idx_pre = (treatment == "PRE")
    print("What the hecko?")
    print(idx_pre.values)
    beta_pre = metric_df.loc[idx_pre.values, idx_pre.values]

    idx_post = (treatment == "POST")
    beta_post = metric_df.loc[idx_post.values, idx_post.values]

    sns.heatmap(beta_pre, vmin=vmin, vmax=vmax)
    plt.title("Beta Diversity (Pre-FMT) (" + metric + ")")
    plt.show()

    sns.heatmap(beta_post, vmin=vmin, vmax=vmax)
    plt.title("Beta Diversity (Post-FMT) (" + metric + ")")
    plt.show()

    result = skbio.stats.distance.permanova(dist_mat, treatment)
    print(result)
    result_prepost = skbio.stats.distance.permanova(dist_mat_prepost, treatment[treatment.isin(["PRE", "POST"])])
    print(result_prepost)


def do_swarm_plots(df, treatment, woltka_meta_df, target_genera):
    for genus in target_genera:
        filtered_df = filter_and_sort_df(df, woltka_meta_df, genus, min_genus_count=0)
        if filtered_df.empty:
            continue

        filtered_df = filtered_df.reset_index()

        melted = filtered_df.melt("index", var_name='cols', value_name='reads')
        melted["sample"] = melted["index"].apply(lambda x: x.split(".")[0])
        melted["treatment"] = melted["index"].apply(lambda x: treatment[x])

        ax = sns.swarmplot(data=melted, x="cols", y="reads", hue="treatment")
        ax.set_xlabel("")
        ax.tick_params(axis='x', labelrotation=45)
        plt.subplots_adjust(bottom=0.2)
        plt.title(genus)
        plt.savefig('fmt/swarm_' + str(genus) + '_treatment.png', bbox_inches='tight')
        plt.show()

        ax = sns.swarmplot(data=melted, x="cols", y="reads", hue="sample")
        ax.set_xlabel("")
        ax.tick_params(axis='x', labelrotation=45)
        plt.subplots_adjust(bottom=0.2)
        plt.title(genus)
        plt.savefig('fmt/swarm_' + str(genus) + '_sample.png', bbox_inches='tight')
        plt.show()


def do_scatter_plots(df, treatment, woltka_meta_df, target_genera, col1=None, col2=None):
    for genus in target_genera:
        filtered_df = filter_and_sort_df(df, woltka_meta_df, genus, min_genus_count=0)
        filtered_df["sample"] = pd.Series(filtered_df.index, index=filtered_df.index).apply(lambda x: x.split(".")[0])
        filtered_df["treatment"] = pd.Series(filtered_df.index, index=filtered_df.index).apply(lambda x: treatment[x])

        c1 = filtered_df.columns[0]
        c2 = filtered_df.columns[1]
        if col1 is not None:
            c1 = col1
        if col2 is not None:
            c2 = col2

        if c2 == "sample":
            continue
        if c1 == "sample":
            continue

        for sample in sorted(filtered_df["sample"].unique()):
            per_sample = filtered_df[filtered_df["sample"] == sample]
            x = per_sample[c1].values
            y = per_sample[c2].values
            plt.scatter(x,y, label=sample)
            plt.xlabel(c1)
            plt.ylabel(c2)
        plt.legend()
        plt.title(genus)
        plt.show()


def do_line_plots(df, treatment, woltka_meta_df, target_genera, col1=None, col2=None):
    for genus in target_genera:
        filtered_df = filter_and_sort_df(df, woltka_meta_df, genus, min_genus_count=0)
        filtered_df["sample"] = pd.Series(filtered_df.index, index=filtered_df.index).apply(lambda x: x.split(".")[0])
        filtered_df["treatment"] = pd.Series(filtered_df.index, index=filtered_df.index).apply(lambda x: treatment[x])

        fig, ax = plt.subplots()

        if col1 is None:
            col1 = filtered_df.columns[0]
        if col2 is None:
            col2 = filtered_df.columns[1]

        xs = []
        ys = []
        lines = []
        for sample in sorted(filtered_df["sample"].unique()):
            per_sample = filtered_df[filtered_df["sample"] == sample]
            x = per_sample[col1].values
            y = per_sample[col2].values
            line, = plt.plot(x,y, label=sample)
            plt.xlabel(col1)
            plt.ylabel(col2)
            xs.append(x)
            ys.append(y)
            lines.append(line)

        def animate(i):
            i = i % 10
            for idx in range(len(xs)):
                line = lines[idx]
                print(line)
                x = xs[idx]
                y = ys[idx]

                print(x)
                print(y)
                j = min(i, len(x)-1)
                line.set_xdata(x[0:j])
                line.set_ydata(y[0:j])
            return lines

        ani = animation.FuncAnimation(
            fig, animate, interval=500, blit=True, save_count=50)
        plt.legend()
        plt.show()


def parse_sample_date(s):
    ss = s.split(".")
    return date(int(ss[1]), int(ss[2]), int(ss[3]))


def do_time_plots(df, treatment, woltka_meta_df, target_genera, max_spec=1):
    fig = plt.figure(figsize=(12, 8))
    pg = 1
    i = 1
    for genus in target_genera:
        filtered_df = filter_and_sort_df(df, woltka_meta_df, genus, min_genus_count=0)
        num_species = filtered_df.shape[1]
        filtered_df["sample"] = pd.Series(filtered_df.index, index=filtered_df.index).apply(lambda x: x.split(".")[0])
        filtered_df["treatment"] = pd.Series(filtered_df.index, index=filtered_df.index).apply(lambda x: treatment[x])

        for ci in range(min(num_species, max_spec)):
            ax = fig.add_subplot(4, 1, i)
            name = woltka_meta_df[woltka_meta_df["#genome"] == filtered_df.columns[ci]]["species"].iloc[0]
            do_time_plot(filtered_df, name, ax=ax, col=filtered_df.columns[ci])
            i += 1
            if i == 5:
                i = 1
                plt.legend()
                # plt.savefig("./fmt/time_" + str(pg) + ".png")
                plt.show()
                pg += 1
                fig = plt.figure(figsize=(12, 8))

    if i != 1:
        plt.legend()
        # plt.savefig("./fmt/time_" + str(pg) + ".png")
        plt.show()


def do_time_plot(filtered_df, title, col=None, ax=None):
    if col is None:
        col = filtered_df.columns[0]

    should_plot = False
    if ax is None:
        fig = plt.figure(figsize=(12, 8))
        should_plot = True
        ax = fig.add_subplot(1, 1, 1)

    for sample in sorted(filtered_df["sample"].unique()):
        per_sample = filtered_df[filtered_df["sample"] == sample]
        AB_point = per_sample["treatment"] == "AB"
        if AB_point.sum() == 0:
            continue
        AB_point = per_sample[AB_point].iloc[0]
        print(AB_point)

        AB_time = parse_sample_date(AB_point.name)
        all_times = []
        for i in per_sample.index:
            all_times.append(parse_sample_date(i))

        deltas = [t - AB_time for t in all_times]
        x = [d.days for d in deltas]
        y = per_sample[col].values
        ax.plot(x,y, marker="o", label=sample)
        ax.set_xlabel("days post AB")
        if should_plot:
            ax.set_ylabel(col)
        else:
            ax.set_ylabel(title + "\n(" + col + ")")
        ax.axvline(x=0, color="gray", linestyle="--")

    if should_plot:
        plt.title(title + " (" + col + ")")
        plt.legend()
        plt.show()


def get_genus(woltka_meta_df, gotu):
    return woltka_meta_df[woltka_meta_df["#genome"] == gotu]["genus"].iloc[0]


def get_species(woltka_meta_df, gotu):
    return woltka_meta_df[woltka_meta_df["#genome"] == gotu]["species"].iloc[0]


def main():
    # Two main questions on the Q.FMT samples:
    #
    # Did the new microbiota colonize?
    # For how long?
    #
    # Samples are
    #
    # 11326.Q.FMT.<sampleid>.<timepoint>.<yyyy.mm.dd>
    #
    # First timepoint is pre fmt? (need metadata, sometimes two)
    #
    # Every patient was given the same microbiota (from a donor)
    # Control did not recieve fmt (but did undergo antibiotic treatment)
    df, meta_df = load_input()
    woltka_meta_df = CSVTable("dataset/metadata/woltka_metadata.tsv", delimiter="\t").load_dataframe()

    # Apply 1 per 100000 relative abundance filtering
    total_sum = df.sum().sum()
    columns_that_pass = df.sum() > total_sum / 100000
    df = df[columns_that_pass[columns_that_pass].index]
    # print(df)

    # Apply pairwise pearson to remove correlated indices
    df = filter_and_sort_df(df, woltka_meta_df, "all", min_genus_count=0)
    pre_pp_df = df
    df, sets = pairwise_pearson(df, thresh=0.95)
    print("Pairwise Pearson Effect")
    print(pre_pp_df.shape)
    print(df.shape)
    to_rep = {}
    for rep in sets:
        for gotu in sets[rep]:
            to_rep[gotu] = rep

    # Constant Sum Scale
    sample_abundance = df.sum(axis=1)
    df = df.T
    df = df / df.sum()
    df = df.T

    gotu = "G000980495"
    rep = to_rep[gotu]
    plt.scatter(pre_pp_df[gotu], pre_pp_df[rep])
    plt.xlabel(get_species(woltka_meta_df, gotu))
    plt.ylabel(get_species(woltka_meta_df, rep))
    plt.show()

    # ARGH.  Dates in metadata don't match so its useless!
    treatment = build_fake_treatment(df)

    # Find dominant microbes in AB samples
    maxes = df.max(axis=1)
    max_idx = df.idxmax(axis=1)
    print("Max in 7:")
    print(max_idx["007.2020.03.01"])
    print(maxes["007.2020.03.01"])

    # Rarefy if you want
    # print(df.sum(axis=1))
    # df_table = Artifact.import_data("FeatureTable[Frequency]", df).view(biom.Table)
    # df_table = rarefy(df_table, 250000)
    # df = Artifact.import_data("FeatureTable[Frequency]", df_table).view(pd.DataFrame)
    # print(df.sum(axis=1))

    # do_alpha_plots(df)
    # do_beta_plots(df, treatment)

    target_genera = [
         "Acetivibrio",
         "Acetobacter",
         "Acidaminococcus",
         "Acinetobacter",
         "Actinomyces",
         "Akkermansia",
         "Alistipes",
         "Alloprevotella",
         "Anaerococcus",
         "Anaerostipes",
         "Anaerotruncus",
         "Arcanobacterium",
         "Atopobium",
         "Azospirillum",
         "Bacillus",
         "Bacteroides",
         "Barnesiella",
         "Bifidobacterium",
         "Blautia",
         "Brachyspira",
         "Brevibacterium",
         "Butyricicoccus",
         "Butyricimonas",
         "Butyrivibrio",
         "Campylobacter",
         "Catenibacterium",
         "Cellulomonas",
         "Chryseobacterium",
         "Citrobacter",
         "Cloacibacillus",
         "Clostridioides",
         "Clostridium",
         "Collinsella",
         "Comamonas",
         "Coprobacillus",
         "Coprococcus",
         "Coraliomargarita",
         "Corynebacterium",
         "Cryptobacterium",
         "Cutibacterium",
         "Desulfovibrio",
         "Dialister",
         "Dorea",
         "Eggerthella",
         "Enorma",
         "Enterobacter",
         "Enterococcus",
         "Erysipelatoclostridium",
         "Escherichia",
         "Eubacterium",
         "Facklamia",
         "Faecalibacterium",
         "Faecalitalea",
         "Fibrobacter",
         "Fusobacterium",
         "Gardnerella",
         "Haemophilus",
         "Heliobacterium",
         "Holdemania",
         "Hungatella",
         "Intestinimonas",
         "Kallipyga",
         "Klebsiella",
         "Kluyvera",
         "Lachnoanaerobaculum",
         "Lachnoclostridium",
         "Lactobacillus",
         "Lactococcus",
         "Lawsonella",
         "Leuconostoc",
         "Megamonas",
         "Megasphaera",
         "Methanobrevibacter",
         "Methanomassiliicoccus",
         "Methanosphaera",
         "Mitsuokella",
         "Mycoplasma",
         "Odoribacter",
         "Oscillibacter",
         "Oxalobacter",
         "Pantoea",
         "Parabacteroides",
         "Paraprevotella",
         "Parasutterella",
         "Pediococcus",
         "Peptoniphilus",
         "Peptostreptococcus",
         "Phascolarctobacterium",
         "Pontibacillus",
         "Porphyromonas",
         "Prevotella",
         "Pseudomonas",
         "Rhodospirillum",
         "Riemerella",
         "Roseburia",
         "Ruminiclostridium",
         "Ruminococcus",
         "Sanguibacteroides",
         "Shigella",
         "Slackia",
         "Solobacterium",
         "Staphylococcus",
         "Streptococcus",
         "Subdoligranulum",
         "Succinatimonas",
         "Succinivibrio",
         "Sulfolobus",
         "Sutterella",
         "Synergistes",
         "Turicibacter",
         "Tyzzerella",
         "Varibaculum",
         "Veillonella",
         "Weissella",
         "Yersinia"
    ]
    ms_target_genera = [
        "Akkermansia",
        "Bifidobacterium",
        "Bilophila",
        "Blautia",
        "Butyricimonas",
        "Christensenella",
        "Coprococcus",
        "Desulfovibrio",
        "Faecalibacterium",
        "Haemophilus",
        "Methanobrevibacter",
        "Paraprevotella",
        "Pedobacter",
        "Pseudomonas",
        "Slackia"
    ]

    co_exclusive_genera = [
        "Acetobacter",
        "Acidaminococcus",
        "Acinetobacter",
        "Actinomyces",
        "Akkermansia",
        "Anaerostipes",
        "Anaerotruncus",
        "Atopobium",
        "Bacillus",
        "Brachyspira",
        "Butyrivibrio",
        "Campylobacter",
        "Catenibacterium",
        "Citrobacter",
        "Cloacibacillus",
        "Comamonas",
        "Coprobacillus",
        "Desulfovibrio",
        "Dialister",
        "Enorma",
        "Fusobacterium",
        "Haemophilus",
        "Lactobacillus",
        "Megamonas",
        "Megasphaera",
        "Methanobrevibacter",
        "Mycoplasma",
        "Odoribacter",
        "Oxalobacter",
        "Paraprevotella",
        "Phascolarctobacterium",
        "Porphyromonas",
        "Prevotella",
        "Pseudomonas",
        "Slackia",
        "Solobacterium",
        "Staphylococcus",
        "Streptococcus",
        "Succinatimonas",
        "Sutterella",
        "Synergistes",
        "Turicibacter"
    ]

    # Save preprocessed table and metadata  at this point for any external plotting
    # print(df)
    # print(treatment)
    #
    # df.to_csv("imsms_fmt_filtered_pp.tsv", sep="\t")
    # treatment.to_csv("imsms_fmt_treatment.tsv", sep="\t")
    #
    # df_table = Artifact.import_data("FeatureTable[Frequency]", df)
    # beta_result = beta(table=df_table, metric="aitchison", pseudocount=1, n_jobs=-2)
    # dist_mat = beta_result.distance_matrix.view(DistanceMatrix)
    # beta_result.distance_matrix.save("imsms_fmt_dist_mat")
    # print(dist_mat)
    # exit(-1)

    df2 = pd.DataFrame(df)
    df2["ReadCount"] = sample_abundance
    df2["sample"] = pd.Series(df2.index, index=df2.index).apply(lambda x: x.split(".")[0])
    df2["treatment"] = pd.Series(df2.index, index=df2.index).apply(lambda x: treatment[x])
    # do_time_plot(df2, "Read Count", col="ReadCount")
    do_time_plots(df, treatment, woltka_meta_df, ["Clostridium"], max_spec=16)
    # do_time_plots(df, treatment, woltka_meta_df, ["Acinetobacter"], max_spec=4)
    # do_time_plots(df, treatment, woltka_meta_df, ["Methanobrevibacter"], max_spec=4)
    # do_time_plots(df, treatment, woltka_meta_df, ["Phascolarctobacterium"], max_spec=4)
    # do_line_plots(df, treatment, woltka_meta_df, ["Akkermansia"], "G000020225", "G000437075")
    # do_time_plots(df, treatment, woltka_meta_df, ["Bacteroides"], max_spec=4)
    # do_scatter_plots(df, treatment, woltka_meta_df, co_exclusive_genera)
    do_time_plots(df, treatment, woltka_meta_df, co_exclusive_genera)
    # do_scatter_plots(df, treatment, woltka_meta_df, ["Bacteroides"])
    # do_swarm_plots(df, treatment, woltka_meta_df, ms_target_genera)
    # do_time_plots(df, treatment, woltka_meta_df, ms_target_genera, max_spec=4)


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    os.chdir("..")
    main()
