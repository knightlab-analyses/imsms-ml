# Examine models trained at different levels of taxonomic assignment

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
from imsms_analysis.events.plot_lda import LDAPlot


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

    df = CSVTable(csv_filepath, on_load_transform=keep_pathways_only, sep="\t")
    df = df.load_dataframe()

    fset_pathways = FeatureSet(
        "Pathways",
        df.columns.tolist()
    )

    pathways = AnalysisFactory(
        [
            CSVTable(
                csv_filepath,
                table_name="Humann2-PathAbundance",
                on_load_transform=keep_pathways_only,
                sep="\t")
        ],
        metadata_filepath
    )\
        .with_lda(1)\
        .with_pair_strategy("paired_subtract_sex_balanced")\
        .with_normalization([Normalization("CLR", "CLR")]) \
        .with_feature_set([fset_pathways] + fset_pathways.create_univariate_sets())

    return MultiFactory([pathways])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    runner = SerialRunner()
    lda_plot = LDAPlot(rows=1, enable_plots=False)
    lda_plot.hook_events(runner)
    runner.run(configure())
    lda_plot.print_acc()