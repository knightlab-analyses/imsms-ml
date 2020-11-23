from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.meta_encoder import MetaEncoder
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    FeatureTransformer
from imsms_analysis.events.plot_lda import LDAPlot


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    probstel = FeatureSet.build_feature_set(
        "Probstel",
        "./dataset/feature_sets/literature_review_Probstel_Baranzini_2018.tsv"
    )

    raw = AnalysisFactory(
        "genus",
        metadata_filepath,
        "Probstel"
    ).with_feature_set(probstel)\
        .with_normalization(Normalization("CLR", "CLR"))\
        .with_pair_strategy(["paired_subtract", "paired_subtract_sex_balanced"])
        # .with_meta_encoders([
        #     None,
        #     MetaEncoder(
        #         "sex",
        #         lambda x: 0 if x == "M" else 1
        #     ),
        # ])

    meta_only = AnalysisFactory(
        "genus",
        metadata_filepath,
        "Meta(sex)"
    ) \
        .with_pair_strategy(["paired_subtract", "paired_subtract_sex_balanced"])\
        .with_feature_set(FeatureSet("Empty", []))\
        .with_meta_encoders(MetaEncoder(
            "sex",
            lambda x: 0 if x == "M" else 1
        )
    )

    return MultiFactory([
        raw, meta_only
    ])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    DryRunner().run(configure())
    runner = SerialRunner()
    runner.run(configure())
