# Try standard dimensionality reductions and embeddings.  If these retain
# useful information, maybe we can visualize results.
from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    # umap = AnalysisFactory(
    #     "species",
    #     metadata_filepath,
    #     "UMAP"
    # ).with_umap()\
    #     .with_num_seeds(50)\
    #     .with_pair_strategy("unpaired")

    # pca = AnalysisFactory(
    #     "species",
    #     metadata_filepath,
    #     "PCA(1)"
    # ).with_pca([1])\
    #     .with_num_seeds(50)\
    #     .with_normalization(Normalization("CLR", "CLR"))\
    #     .with_pair_strategy("paired_subtract")

    lda = AnalysisFactory(
        "species",
        metadata_filepath,
        "LDA(1)"
    ).with_lda([1])\
        .with_num_seeds(5)\
        .with_normalization([Normalization.DEFAULT, Normalization("CLR", "CLR")])\
        .with_pair_strategy(["paired_subtract"])\
        .with_num_training_sets(5)

    # raw = AnalysisFactory(
    #     "species",
    #     metadata_filepath,
    #     "Species"
    # )
    return MultiFactory([
        # umap,
        lda,
        # pca,
        # raw,
    ])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner.run(configure())

