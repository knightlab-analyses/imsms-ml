# Examine models trained at different levels of taxonomic assignment
from q2_mlab import ClassificationTask

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    FeatureTransformer


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    mbp25 = "./dataset/feature_transforms/mbp_table25.csv"
    mbp30 = "./dataset/feature_transforms/mbp_table30.csv"
    mbp35 = "./dataset/feature_transforms/mbp_table35.csv"

    woltka_transforms = AnalysisFactory(
        ["none"],
        metadata_filepath,
    ).with_feature_transform(
        [FeatureTransformer("MBP25", mbp25),
         FeatureTransformer("MBP30", mbp30),
         FeatureTransformer("MBP35", mbp35)]
    )

    return MultiFactory([woltka_transforms])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner.run(configure())
