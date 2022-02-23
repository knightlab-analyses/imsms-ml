# Examine Akkermansia, the most often reported feature
from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.events.plot_lda import LDAPlot


def configure():
    akkermansia_feature_set = FeatureSet.build_feature_set(
        "Top Mimics",
        "./dataset/feature_sets/top_mimics_genome_ids.tsv"
    )
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    return AnalysisFactory(
        BiomTable("none"),
        metadata_filepath
    )\
    .with_lda([1]) \
    .with_feature_set(akkermansia_feature_set.create_univariate_sets()) \
    .with_pair_strategy("paired_subtract_sex_balanced") \
    .with_normalization(Normalization.CLR) \


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    runner = SerialRunner()
    lda_plot = LDAPlot(rows=4, enable_plots=False)
    lda_plot.hook_events(runner)
    runner.run(configure())
    lda_plot.print_acc()


