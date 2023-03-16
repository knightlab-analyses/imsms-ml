from imsms_analysis.analyses.old_and_new_lme import get_species
from imsms_analysis.analysis_runner import SerialRunner, DryRunner, TableRunner
from imsms_analysis.common.PairwisePearson import pairwise_pearson
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
from imsms_analysis.common.train_test import SplitByMetadata, \
    PairedSplit, Passthrough
from imsms_analysis.common.woltka_metadata import filter_and_sort_df
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    ChainedTransform, RelativeAbundanceFilter, PairwisePearsonTransform
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
import statsmodels.api as sm
import matplotlib
matplotlib.use("TkAgg")

old_metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"
combined_metadata_filepath = "./dataset/metadata/combined_iMSMS_metadata.tsv"
import scipy


def get_species(woltka_meta_df, gotu):
    return woltka_meta_df[woltka_meta_df["#genome"] == gotu]["species"].iloc[0]

def configure_both():
    def set_factory_params(fact):
        df_processing = ChainedTransform(
            [
                RelativeAbundanceFilter(1/10000),
                # PairwisePearsonTransform(.95)
            ]
        )
        return fact.with_pair_strategy(["unpaired"]) \
            .with_normalization(Normalization.DEFAULT) \
            .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
            .with_train_test(
            [
                Passthrough()
            ]) \
            .with_feature_transform(df_processing)

    old_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/combined-none.biom"
        ]),
        combined_metadata_filepath,
        "old"
    )
    old_fact = set_factory_params(old_fact)

    new_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        combined_metadata_filepath,
        "new"
    )
    new_fact = set_factory_params(new_fact)

    both_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/combined-none.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        combined_metadata_filepath,
        "combined_data"
    )
    # both_fact needs extra train_test splits
    both_fact = set_factory_params(both_fact).with_train_test(
        [
            SplitByMetadata(meta_col="prep", train_meta=["old"]),
            SplitByMetadata(meta_col="prep", train_meta=["new"]),
            PairedSplit()
        ]
    )

    # return old_fact
    return MultiFactory([old_fact, new_fact])
    # return MultiFactory([old_fact, new_fact, both_fact])
    # return new_fact
    # return both_fact


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    results = TableRunner().run(configure_both())
    woltka_meta_df = CSVTable("dataset/metadata/woltka_metadata.tsv", delimiter="\t").load_dataframe()

    i = 1
    dfs = {}
    for config, train, test in results:
        dfs[config.analysis_name] = train.df

    only_old = 0
    only_new = 0

    for genome_id in dfs["new"].columns:
        if genome_id not in dfs["old"].columns:
            print(genome_id, "is only in new dataset")
            only_new += 1

    mwus = {}
    for genome_id in dfs["old"].columns:
        if genome_id not in dfs["new"].columns:
            print(genome_id, "is only in old dataset")
            only_old += 1
            continue
        old_pts = dfs["old"][genome_id]
        new_pts = dfs["new"][genome_id]

        mwu = scipy.stats.mannwhitneyu(old_pts, new_pts)
        mwus[genome_id] = mwu
        print(genome_id, mwu)

    print("Only Old:", only_old)
    print("Only New:", only_new)

    print("Old shape", dfs["old"].shape)
    print("New Shape", dfs["new"].shape)

    plt.hist([mwus[key].pvalue for key in mwus])
    plt.title("Histogram of Mann Whitney U pvalues\n(Old vs New Reference Count)")
    plt.show()

    old_sums = dfs["old"].sum()
    print(dfs["old"].sum())

    abundant_and_different = []
    for genome_id in mwus:
        if mwus[genome_id].pvalue < 1 and old_sums[genome_id] > 10000:
            print("Wow bad: ", genome_id)
            abundant_and_different.append(genome_id)

    abundant_and_different.sort(key=lambda x: mwus[x].pvalue)
    for genome_id in abundant_and_different:
        print(genome_id, mwus[genome_id].pvalue)

    woltka_meta_df = CSVTable("dataset/metadata/woltka_metadata.tsv", delimiter="\t").load_dataframe()
    for genome_id in abundant_and_different:
        # if genome_id != "G000020225":
        #     continue
        olds = dfs["old"][genome_id]
        news = dfs["new"][genome_id]
        types = ["old"] * len(olds) + ["new"] * len(news)
        sns_df = pd.DataFrame({"type": types, genome_id: pd.concat([olds, news])})
        print(sns_df)

        fig, axs = plt.subplots(1, 2)
        sm.qqplot_2samples(news.values, olds.values, line='45', ax=axs[0])
        axs[0].axis("equal")

        sns.catplot(data=sns_df, x="type", y=genome_id, ax=axs[1])
        plt.suptitle(get_species(woltka_meta_df, genome_id) + " MWU:" + str(mwus[genome_id].pvalue))
        plt.show()




