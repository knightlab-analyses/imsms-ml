# Try standard dimensionality reductions and embeddings.  If these retain
# useful information, maybe we can visualize results.
from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    FeatureTransformer
from imsms_analysis.events.plot_lda import LDAPlot


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    fset_species = FeatureSet(
        "SPECIES",
        ["239935", "853"],
        ["Akkermansia", "Faecalibacterium"]
    )

    lda = AnalysisFactory(
        BiomTable("species"),
        metadata_filepath
    ).with_lda([1]) \
        .with_pair_strategy(["paired_subtract"])\
        .with_normalization([Normalization("CLR", "CLR")])\
        .with_feature_set([fset_species])

    return lda


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    runner = SerialRunner()
    lda_plot = LDAPlot()
    lda_plot.hook_events(runner)
    runner.run(configure())
    lda_plot.print_acc()