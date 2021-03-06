# Recapitulate Probstel 2018 list of important genera
from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.table_info import BiomTable


def configure():
    probstel = FeatureSet.build_feature_set(
        "Probstel",
        "./dataset/feature_sets/literature_review_Probstel_Baranzini_2018.tsv"
    )
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    all_genera = AnalysisFactory(
        BiomTable("genus"),
        metadata_filepath,
        "All-Genera"
    )

    probstel_features = AnalysisFactory(
        BiomTable("genus"),
        metadata_filepath,
    ).with_feature_set(probstel.create_univariate_sets("Univariate-") + [probstel])

    return MultiFactory([all_genera, probstel_features])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
