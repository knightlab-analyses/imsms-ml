# Examine models trained at different levels of taxonomic assignment

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
from imsms_analysis.events.plot_lda import LDAPlot


def fix_input_table(df):
    df = df.set_index("#ID")
    df = df.transpose()
    df.index.name = None
    df.columns.name = None
    return df


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    csv_filepath = "./dataset/csv/vfdb_imsms_576pairs.txt"

    df = CSVTable(csv_filepath, on_load_transform=fix_input_table, sep="\t")
    df = df.load_dataframe()

    fset = FeatureSet(
        "VirulenceFactor",
        df.columns.tolist()
    )

    pathways = AnalysisFactory(
        [
            CSVTable(
                csv_filepath,
                table_name="VFDB",
                on_load_transform=fix_input_table,
                sep="\t")
        ],
        metadata_filepath
    )\
        .with_lda(1)\
        .with_pair_strategy("paired_subtract_sex_balanced")\
        .with_normalization([Normalization.CLR])\
        .with_feature_set([fset] + fset.create_univariate_sets())

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