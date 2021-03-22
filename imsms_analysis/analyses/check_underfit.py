# Examine models trained on varying size subsets of training set

from imsms_analysis.analysis_runner import SerialRunner, DryRunner, ParallelRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    woltka_levels = AnalysisFactory(
        [BiomTable("species")],
        metadata_filepath
    ).with_downsampling([25, 50, 75, 100, 125, 150, 175, 200, 225, 250, None])\
        .with_normalization(Normalization.CLR)\
        .with_pair_strategy(["paired_subtract", "paired_subtract_sex_balanced"])

    return MultiFactory([woltka_levels])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
