# Examine Akkermansia, the most often reported feature
from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.table_info import BiomTable


def configure():
    akkermansia_feature_set = FeatureSet.build_feature_set(
        "Akkermansia",
        "./dataset/feature_sets/just_akkermansia.tsv"
    )
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    return AnalysisFactory(
        BiomTable("species"),
        metadata_filepath,
        "Akkermansia"
    ).with_feature_set(akkermansia_feature_set)


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner().run(configure())

