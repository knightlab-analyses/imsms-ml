# Examine models trained at different levels of taxonomic assignment

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable


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
    df = df.set_index("#Pathway")
    df = df.transpose()
    df.index.name = None
    df.columns.name = None
    df = df.rename(mapper=_parse_sample_id)
    return df


def keep_pathways_only(df):
    df = fix_input_table(df)
    foo = list(df.filter(regex='\\|'))
    df = df.drop(foo, axis=1)
    return df


def keep_species_specific_pathways_only(df):
    df = fix_input_table(df)
    foo = list(df.filter(regex='\\|'))
    df = df[foo]
    return df


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    csv_filepath = "./dataset/csv/humann2_pathabundance_subject.txt"

    pathways = AnalysisFactory(
        [
            CSVTable(
                csv_filepath,
                table_name="Humann2-PathAbundance",
                on_load_transform=keep_pathways_only,
                sep="\t"),
            CSVTable(
                csv_filepath,
                table_name="Humann2-SpeciesPathAbundance",
                on_load_transform=keep_species_specific_pathways_only,
                sep="\t")
        ],
        metadata_filepath,
        "Humann2PathAbundance"
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


    return MultiFactory([pathways, raw])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
