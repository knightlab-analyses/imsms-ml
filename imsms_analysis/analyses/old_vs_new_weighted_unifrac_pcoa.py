from imsms_analysis.analysis_runner import SerialRunner, TableRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
import pandas as pd

from imsms_analysis.common.train_test import Passthrough, UnpairedSplit, \
    PairedSplit
from imsms_analysis.preprocessing.id_parsing import _parse_sample_id, _parse_disease_state, _parse_household_id

import scipy
import matplotlib
import seaborn as sns
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import skbio.diversity
from skbio.diversity import beta_diversity
from skbio import TreeNode

from skbio.stats.ordination import pcoa
from sklearn.ensemble import RandomForestRegressor


def configure():
    old_metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"

    old_fact = AnalysisFactory(
        BiomTable("none"),
        old_metadata_filepath,
        "old"
    ) \
        .with_train_test(Passthrough()) \
        .with_pair_strategy("unpaired") \
        .with_normalization([Normalization.NONE]) \

    new_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        new_metadata_filepath,
        "new"
    ) \
        .with_train_test(Passthrough()) \
        .with_pair_strategy("unpaired") \
        .with_normalization([Normalization.NONE]) \
        .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"]))

    return MultiFactory([new_fact])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    extended_metadata_filepath = "./dataset/metadata/iMSMS_phenotypes_for_Knight_Lab_20221104.tsv"
    ex_meta = pd.read_csv(extended_metadata_filepath, sep="\t", index_col="filtered_sample_name")

    wolr1tree = TreeNode.read("./dataset/nwk/wolr1tree.nwk")

    for config, train, test in TableRunner().run(configure()):
        train.meta_df = train.meta_df.join(ex_meta)
        print(train.meta_df.columns)

        weighted_unifrac_dm = beta_diversity(
            "weighted_unifrac",
            train.df.to_numpy(),
            train.df.index,
            tree=wolr1tree,
            otu_ids=train.df.columns
        )

        saveme = pd.DataFrame(
            weighted_unifrac_dm.data,
            index=weighted_unifrac_dm.ids,
            columns=weighted_unifrac_dm.ids
        )
        saveme.to_csv(config.analysis_name + "_weighted_unifrac_dm.tsv", sep="\t")

        weighted_unifrac_pc = pcoa(weighted_unifrac_dm)

        metadata_columns_old = \
            ["site", "sex", "disease",
             "disease_course", "treatment_type", "ethinicity"]

        metadata_columns_new = \
            ["Collection_Site", "sex", "Disease_Status",
             "Disease_Course", "Treatment_Status", "Treatment_Type"]

        metadata_columns = metadata_columns_new
        if config.analysis_name.startswith("old"):
            metadata_columns = metadata_columns_old

        for c in metadata_columns:
            col_only = train.meta_df[[c]].fillna("missing")
            fig = weighted_unifrac_pc.plot(
                col_only, c,
                axis_labels=('PC 1', 'PC 2', 'PC 3'),
                title='Samples colored by ' + c, cmap='jet', s=50)
            plt.savefig("./pcoa/weighted_unifrac/" + config.analysis_name + "_" + c + ".png")
            plt.show()

