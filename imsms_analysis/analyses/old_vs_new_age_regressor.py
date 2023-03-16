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

from sklearn.ensemble import RandomForestRegressor


def configure():
    old_metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"

    old_fact = AnalysisFactory(
        BiomTable("none"),
        old_metadata_filepath,
        "old"
    ) \
        .with_train_test(PairedSplit()) \
        .with_pair_strategy("unpaired") \
        .with_normalization([Normalization.NONE, Normalization.DEFAULT, Normalization.CLR]) \

    new_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        new_metadata_filepath,
        "new"
    ) \
        .with_train_test(PairedSplit()) \
        .with_pair_strategy("unpaired") \
        .with_normalization([Normalization.NONE, Normalization.DEFAULT, Normalization.CLR]) \
        .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"]))

    return MultiFactory([old_fact, new_fact])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    extended_metadata_filepath = "./dataset/metadata/iMSMS_phenotypes_for_Knight_Lab_20221104.tsv"
    ex_meta = pd.read_csv(extended_metadata_filepath, sep="\t", index_col="filtered_sample_name")

    dfs = {}
    meta_dfs = {}

    for config, train, test in TableRunner().run(configure()):
        dfs[config.analysis_name] = train.df
        meta_dfs[config.analysis_name] = train.meta_df
        if "age" not in train.meta_df.columns:
            train.meta_df["age"] = pd.to_numeric(train.meta_df["host_age"])
            test.meta_df["age"] = pd.to_numeric(test.meta_df["host_age"])
        age_target = train.df.join(train.meta_df[["age"]])["age"]

        rfr = RandomForestRegressor()
        rfr.fit(train.df, age_target)

        age_pred = rfr.predict(test.df)
        age_true = test.df.join(test.meta_df[["age"]])["age"]

        coefficient_of_determination = rfr.score(test.df, age_true)

        plt.scatter(age_pred, age_true)
        plt.xlabel("Predicted Age")
        plt.ylabel("True Age")
        plt.axis("equal")
        plt.title("iMSMS " + config.analysis_name + " Age Prediction\nR^2=" + str(coefficient_of_determination))
        plt.savefig("./age_regression/iMSMS" + config.analysis_name + "_age_pred.png")
        plt.show()
