from imsms_analysis.analysis_runner import SerialRunner, TableRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
import pandas as pd

from imsms_analysis.common.train_test import Passthrough
from imsms_analysis.preprocessing.id_parsing import _parse_sample_id, _parse_disease_state, _parse_household_id

import scipy
import matplotlib
import seaborn as sns
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt


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
        .with_normalization(Normalization.NONE)

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
        .with_normalization(Normalization.NONE) \
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

    old_samples = set(dfs["old"].index)
    new_samples = set(dfs["new"].index)
    extended_samples = set(ex_meta.index)

    old_missing = sorted(old_samples.difference(extended_samples))
    new_missing = sorted(new_samples.difference(extended_samples))
    print("No Ex-Meta Old Samples:")
    print(old_missing)

    print("No Ex-Meta New Samples:")
    print(new_missing)

    meta_dfs["old"] = meta_dfs["old"].drop(old_missing)
    meta_dfs["new"] = meta_dfs["new"].drop(new_missing)

    meta_dfs["old"] = meta_dfs["old"].join(ex_meta)
    meta_dfs["new"] = meta_dfs["new"].join(ex_meta)

    # Renames to sync up columns
    meta_dfs["new"]["age"] = meta_dfs["new"]["host_age"]
    meta_dfs["new"]["bmi"] = meta_dfs["new"]["host_body_mass_index"]

    old_meta_cols = set(meta_dfs["old"].columns)
    new_meta_cols = set(meta_dfs["new"].columns)

    both_cols = sorted(old_meta_cols.intersection(new_meta_cols))
    print("only old")
    print(sorted(old_meta_cols.difference(new_meta_cols)))

    print("both")
    print(both_cols)

    print("Only new")
    print(sorted(new_meta_cols.difference(old_meta_cols)))

    categorical = [
        "Collection_Site",
        "Disease_Course",
        "Disease_Status",
        "Sex",
        "Treatment_Status",
        "Treatment_Type",
        "disease",
        "disease_course",
        "sex"
    ]

    meta_dfs["old"]["dataset"] = "old"
    meta_dfs["new"]["dataset"] = "new"
    combined = pd.concat([meta_dfs["old"], meta_dfs["new"]])
    print(combined["dataset"])

    # Convert duplicate names
    combined["Collection_Site"] = combined["Collection_Site"].apply(lambda x: "San Sebastian" if x == "SanSeb" else x)

    DO_CATEGORICAL = True
    if DO_CATEGORICAL:
        combined_categorical = combined.fillna("missing")
        for col in categorical:
            contingency = pd.crosstab(combined_categorical["dataset"], combined_categorical[col], dropna=False)
            print(contingency)
            chi_sq, p, dof, exp = scipy.stats.chi2_contingency(contingency)
            print(chi_sq)
            print(p)
            print(exp)

            if p > 0.5:
                print("no diff")
            else:
                contingency_pct = contingency.div(contingency.sum(axis=1), axis=0)

                chi_sq_prop = (((contingency - exp)**2) / exp) / chi_sq
                chi_sq_prop = pd.DataFrame(chi_sq_prop, contingency.index, contingency.columns)
                chi_sq_prop = chi_sq_prop.fillna(0)
                chi_sq_prop = chi_sq_prop.sum()
                chi_sq_prop = pd.DataFrame([chi_sq_prop])

                fig, axes = plt.subplots(2, 1, sharex=True)
                sns.heatmap(contingency_pct, fmt=".2f", annot=True, square=True, ax=axes[0])
                plt.xlabel("")
                axes[0].set_title("Observed Ratios")

                sns.heatmap(chi_sq_prop, fmt=".2f", annot=True, square=True, ax=axes[1])
                plt.title("Contribution To Chi Sq")
                plt.yticks([])

                plt.suptitle(col + "\nChiSq=" + format(chi_sq, ".2f") + " p=" + format(p, ".2E"))
                plt.show()

    numerical = [
        "age",
        "bmi",
        "EDSS",
        "MSSS"
    ]

    combined["age"] = pd.to_numeric(combined["age"])  # argh.
    combined["bmi"] = pd.to_numeric(combined["bmi"])
    combined["EDSS"] = pd.to_numeric(combined["EDSS"].str.split().str[0]) #Argh!  Why are they annotating numeric scores!?
    combined["MSSS"] = pd.to_numeric(combined["MSSS"])

    fig, axes = plt.subplots(1, 4)
    DO_NUMERICAL = True
    if DO_NUMERICAL:
        for c in range(len(numerical)):
            col = numerical[c]
            data = pd.melt(combined[["dataset", col]], id_vars="dataset")
            sns.boxplot(data=data, x="dataset", y="value", ax=axes[c])
            axes[c].set_xlabel("")
            axes[c].set_ylabel(col)
            a = combined[combined["dataset"] == "old"][col].dropna()
            b = combined[combined["dataset"] == "new"][col].dropna()
            t, p = scipy.stats.ttest_ind(a, b, axis=0, equal_var=False)
            print(col, t, p)
            axes[c].set_title(col)
            plt.text(0.5, 0.99, "t={:.2f}\np={:.2E}".format(t, p),
                     horizontalalignment='center',
                     verticalalignment='top',
                     size=12,
                     transform=axes[c].transAxes
                     )
        plt.show()
