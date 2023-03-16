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
        return fact.with_pair_strategy(["unpaired"]) \
            .with_normalization(Normalization.DEFAULT) \
            .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
            .with_train_test(
            [
                Passthrough()
            ]) \
            .with_feature_transform([RelativeAbundanceFilter(1/10000), ChainedTransform([])])

    old_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/combined-none.biom"
        ]),
        combined_metadata_filepath,
        "old"
    )
    old_fact = set_factory_params(old_fact)
    return old_fact


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    results = TableRunner().run(configure_both())
    woltka_meta_df = CSVTable("dataset/metadata/woltka_metadata.tsv", delimiter="\t").load_dataframe()

    for config, train, test in results:
        print(config.analysis_name)
        print(train.df.shape)

        if config.analysis_name == "old-RelativeAbundance_0.0001":
            passing_cols = pd.DataFrame(data={"passing":train.df.columns})
            print(passing_cols)
            passing_cols.to_csv("old_1per10000.tsv")




