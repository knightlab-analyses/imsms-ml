# Examine models trained from clustered snp presence/absence data

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable, MergeTable
from os import listdir
from os.path import isfile, join


def _parse_sample_id(index: str):
    # Input of form 71401.0009
    # Output of form 71401-0009
    ss = index.split('.')
    if len(ss) != 2:
        print("BAD: ", index)
        raise ValueError("Can't convert sample id:", index)

    sample_id = ss[0] + "-" + ss[1]
    # print("GOOD: ", index, "->", sample_id)
    return sample_id


def fix_input_table(df):
    df = df.set_index(df.columns[0])
    df = df.rename(mapper=_parse_sample_id)
    df = df.drop("group", axis=1)
    print(df)
    return df


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    csv_root = "./plots/snp_clustermaps"
    onlyfiles = sorted([f for f in listdir(csv_root) if isfile(join(csv_root, f)) and
                 f.endswith(".csv")])

    tables = [
        CSVTable(join(csv_root, f),
                 table_name=f,
                 on_load_transform=fix_input_table,
                 dtype=str
        )
        for f in onlyfiles
    ]

    snp_clusters = AnalysisFactory(
        [
            MergeTable(tables, onlyfiles)
        ],
        metadata_filepath,
        "SNP Clusters"
    )\
        .with_pair_strategy("paired_subtract_sex_balanced")\
        .with_normalization([Normalization("None", "none"), Normalization.DEFAULT, Normalization("CLR", "CLR")])

    raw = AnalysisFactory(
        BiomTable("species"),
        metadata_filepath,
        "Species"
    )\
        .with_pair_strategy(["paired_subtract_sex_balanced"])\
        .with_normalization([Normalization("None", "none"), Normalization.DEFAULT, Normalization("CLR", "CLR")])\


    return MultiFactory([snp_clusters, raw])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
