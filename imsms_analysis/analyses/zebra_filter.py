from imsms_analysis.analysis_runner import SerialRunner, DryRunner, ParallelRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_filter import ZebraFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.common.target_set import TargetSet


def configure():
    metadata_filepath = "./dataset/metadata/FR02_sampleid_filtered.tsv"

    zebra = AnalysisFactory(
        [BiomTable("none")],
        metadata_filepath
    ).with_normalization(Normalization.CLR) \
     .with_pair_strategy("unpaired_target_balanced") \
     .with_feature_filter([
        ZebraFilter(.00, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.10, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.25, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.50, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.75, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.90, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.95, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.98, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.99, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.995, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.998, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.999, "./dataset/metadata/finrisk_cov.tsv"),
        # ZebraFilter(.9999, "./dataset/metadata/finrisk_cov.tsv"),
    ])\
    .with_target_set([
        TargetSet("Lactose", "FR02_100A", ["2"]),
        # TargetSet("Gluten", "FR02_100B", ["2"]),
        # TargetSet("Food Allergy", "FR02_100C", ["2"]),
        # TargetSet("Diabetic", "FR02_100D", ["2"]),
        # TargetSet("Cholesterol-Lowering", "FR02_100E", ["2"]),
        # TargetSet("Weight-Loser", "FR02_100F", ["2"]),
        # TargetSet("Vegetarian", "FR02_100G", ["2"]),
        # TargetSet("Other-Diet", "FR02_100H", ["2"]),
    ])

    return MultiFactory([
        zebra
    ])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
