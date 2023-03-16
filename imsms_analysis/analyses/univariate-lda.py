
# Other people report a lot of stuff, do any of these actually hold up against our dataset?
from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.events.plot_lda import LDAPlot


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    return AnalysisFactory(
        BiomTable("none"),
        metadata_filepath
    ) \
        .with_lda([1]) \
        .with_feature_set(FeatureSet.create_univariate_zebra("../zebra.csv", 0.25)) \
        .with_normalization(Normalization.CLR) \
        .with_pair_strategy("paired_subtract_sex_balanced") \

if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    runner = SerialRunner()
    runner.run(configure())
    lda_plot = LDAPlot(rows=4, enable_plots=False)
    lda_plot.hook_events(runner)
    runner.run(configure())
    lda_plot.print_acc()


