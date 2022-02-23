# Examine models trained at different levels of taxonomic assignment
from q2_mlab import ClassificationTask

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    FeatureTransformer, NetworkTransformer


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    hc_off = "./dataset/feature_sets/hc_off.tsv"
    hc_treated = "./dataset/feature_sets/hc_treated.tsv"
    ms_off = "./dataset/feature_sets/ms_off.tsv"
    ms_treated = "./dataset/feature_sets/ms_treated.tsv"

    # shuffle = AnalysisFactory(
    #     ["none"],
    #     metadata_filepath
    # ).with_feature_transform(
    #     [FeatureTransformer("MBP30_Shuffle"+str(x), mbp30, shuffle_seed=x)
    #      for x in range(10)]
    # )

    woltka_transforms = AnalysisFactory(
        [BiomTable("species")],
        metadata_filepath,
    ).with_feature_transform(
        [
            NetworkTransformer("ms.off", ms_off),
            NetworkTransformer("ms.treated", ms_treated),
            NetworkTransformer("hc.off", hc_off),
            NetworkTransformer("hc.treated", hc_treated)
         ]) \
        .with_normalization(Normalization("CLR", "CLR")) \
        .with_pair_strategy("paired_subtract_sex_balanced") \
        .with_metadata_filter([
        None,
        MetadataFilter(
            "Off Treatment",
            "treatment_status",
            ["Off", "Control"]
        )
    ])



    woltka_species = AnalysisFactory(
        [BiomTable("species")],
        metadata_filepath,
        "All Species",
    ).with_normalization(Normalization("CLR", "CLR")) \
    .with_pair_strategy("paired_subtract_sex_balanced")

    return MultiFactory([woltka_species, woltka_transforms])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    DryRunner().run(configure())
    SerialRunner().run(configure())
