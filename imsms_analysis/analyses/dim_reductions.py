# Try standard dimensionality reductions and embeddings.  If these retain
# useful information, maybe we can visualize results.
from analysis_runner import SerialRunner, DryRunner
from common.analysis_factory import AnalysisFactory, MultiFactory
from common.feature_set import FeatureSet


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    umap = AnalysisFactory(
        "species",
        metadata_filepath,
        "UMAP"
    ).with_umap()

    pca = AnalysisFactory(
        "species",
        metadata_filepath,
    ).with_pca([10,50,100,250,500,1000,2000])

    raw = AnalysisFactory(
        "species",
        metadata_filepath,
        "Species"
    )
    return MultiFactory([umap, pca, raw])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner.run(configure())

