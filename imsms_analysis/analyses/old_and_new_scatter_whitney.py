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
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")

old_metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"
combined_metadata_filepath = "./dataset/metadata/combined_iMSMS_metadata.tsv"
import scipy


def configure_both():

    def set_factory_params(fact):
        df_processing = ChainedTransform(
            [
                RelativeAbundanceFilter(1/10000),
                PairwisePearsonTransform(.95)
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
    # return MultiFactory([old_fact, new_fact])
    # return MultiFactory([old_fact, new_fact, both_fact])
    # return new_fact
    return both_fact


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    results = TableRunner().run(configure_both())
    woltka_meta_df = CSVTable("dataset/metadata/woltka_metadata.tsv", delimiter="\t").load_dataframe()


    def make_sns_df(state, genus, refs=None):
        if refs is None:
            sns_df = filter_and_sort_df(state.df, woltka_meta_df, genus)
        else:
            refs2 = [r for r in refs if r in state.df.columns]
            sns_df = state.df[refs2]

        genus_cols = sns_df.columns
        print(sns_df.shape)
        sns_df[genus] = sns_df.sum(axis=1)
        sns_df = sns_df.drop(genus_cols, axis=1)
        sns_df = sns_df.reset_index()
        sns_df = sns_df.melt(id_vars='index', var_name='genome_id', value_name='count')
        state.target.name = "target"
        sns_df = sns_df.join(state.target, on="index")
        return sns_df


    i = 1
    for config, train, test in results:
        print(config.analysis_name, train.df.shape, test.df.shape)

        print("Eisenbergiella", "G001717135" in train.df.columns)
        print("Lachnospiraceae bacterium NLAE-zl-G231", "G900113595" in train.df.columns)

        df, sets = pairwise_pearson(train.df, thresh=0.95)

        # Hungatella "G000160095", "G000235505"


        for rep in sets:
            if "G000160095" in sets[rep] or "G000235505" in sets[rep]:
                print("Found Hungatella")
                print(rep, sets[rep])

        # Hard to tell the difference between Eisenbergiella G001717135 and Lachnospiraceae G900113595
        # Sometimes pairwise pearson calls both 1 thing, sometimes it calls them the other thing.
        # plt.scatter(x=train.df["G001717135"], y=train.df["G000020225"])
        # plt.show()
        # plt.scatter(x=train.df["G001717135"], y=train.df["G000160095"])
        # plt.show()
        # plt.scatter(x=train.df["G001717135"], y=train.df["G000235505"])
        # plt.show()

        # plt.subplot(2, 1, i)
        # i += 1
        sns.boxenplot(data=make_sns_df(train, genus="Akkermansia"), x='genome_id', y="count", hue="target")

        # sns.swarmplot(data=make_sns_df(train, genus="Ruthenibacterium"), x='genome_id', y="count", hue="target")
        # plt.show()
        #
        # sns.swarmplot(data=make_sns_df(train, genus="Hungatella"), x='genome_id', y="count", hue="target")
        # plt.show()
        #
        # # Hard to tell the difference between Eisenbergiella G001717135 and Lachnospiraceae G900113595
        # sns.swarmplot(data=make_sns_df(train, genus="Eisenbergiella", refs=['G001717135', 'G900113595']), x='genome_id', y="count", hue="target")
        # plt.show()
        #
        # # Maybe check just prausnitzii
        # sns.swarmplot(data=make_sns_df(train, genus="Faecalibacterium"), x='genome_id', y="count", hue="target")
        # plt.show()
        #
        # # Maybe check just prausnitzii
        # sns.swarmplot(data=make_sns_df(train, genus="Blautia"), x='genome_id', y="count", hue="target")
        # plt.show()

    # plt.show()
