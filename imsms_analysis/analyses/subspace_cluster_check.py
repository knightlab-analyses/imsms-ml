from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.events.plot_lda import LDAPlot


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    fact1 = AnalysisFactory(
        BiomTable("none", "./dataset/biom/filtered_akkermansia.biom"),
        metadata_filepath,
        "Filtered-Akkermansia"
    ) \
        .with_feature_set(FeatureSet("Akkermansia", ["G000437075", "G000020225", "G000436395", "G000723745", "G000980515", "G001578645", "G001580195", "G001647615", "G001683795", "G001917295", "G001940945", "G900097105"])
                          .create_univariate_sets())\
        .with_normalization([Normalization.DEFAULT]) \
        .with_pair_strategy(["paired_subtract_sex_balanced"])


    fact2 = AnalysisFactory(
        BiomTable("none", "./dataset/biom/fixed_akkermansia.biom"),
        metadata_filepath,
        "Fixed-Akkermansia"
    ) \
        .with_feature_set(FeatureSet("FixedAkkermansia", ["SV0", "SV1", "SV2", "SV3"]).create_univariate_sets()) \
        .with_normalization([Normalization.DEFAULT]) \
        .with_pair_strategy(["paired_subtract_sex_balanced"])

    return MultiFactory([fact1, fact2])

if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    print(BiomTable("none", "./dataset/biom/filtered_akkermansia.biom").load_dataframe())

    runner = SerialRunner()
    lda_plot = LDAPlot(rows=4, enable_plots=True)
    lda_plot.hook_events(runner)
    runner.run(configure())
    lda_plot.print_acc()


