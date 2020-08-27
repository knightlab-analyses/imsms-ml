# Examine molecular mimicry feature sets!
from analysis_runner import SerialRunner, DryRunner
from common.analysis_factory import AnalysisFactory, MultiFactory
from common.feature_set import FeatureSet


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    proteome_avail = FeatureSet.build_feature_set(
        "HasData",
        "./dataset/feature_sets/proteome_available.tsv"
    )

    return AnalysisFactory(
        "none",
        metadata_filepath
    ).with_feature_set([None, proteome_avail])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner.run(configure())
