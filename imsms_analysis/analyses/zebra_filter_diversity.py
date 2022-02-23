from imsms_analysis.analysis_runner import SerialRunner, DryRunner, ParallelRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_filter import ZebraFilter
from imsms_analysis.common.table_info import BiomTable


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    woltka_levels = AnalysisFactory(
        [
            BiomTable("species"),
        ],
        metadata_filepath
    ).with_pair_strategy([
        "paired_subtract_sex_balanced"
    ])
    zebra = AnalysisFactory(
        [BiomTable("none")],
        metadata_filepath
    ).with_pair_strategy("paired_subtract_sex_balanced") \
    .with_feature_filter([
        ZebraFilter(.00, "../zebra.csv"),
        ZebraFilter(.10, "../zebra.csv"),
        ZebraFilter(.25, "../zebra.csv"),
        ZebraFilter(.50, "../zebra.csv"),
        ZebraFilter(.75, "../zebra.csv"),
        ZebraFilter(.90, "../zebra.csv"),
        ZebraFilter(.95, "../zebra.csv"),
        ZebraFilter(.98, "../zebra.csv"),
        ZebraFilter(.99, "../zebra.csv"),
        ZebraFilter(.995, "../zebra.csv"),
        ZebraFilter(.998, "../zebra.csv"),
        ZebraFilter(.999, "../zebra.csv"),
        ZebraFilter(.9999, "../zebra.csv"),
    ])

    return MultiFactory([
        woltka_levels,
        zebra,
    ])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
