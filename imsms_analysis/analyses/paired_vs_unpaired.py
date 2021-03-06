# Examine pairing strategies (concat, subtract) vs unpaired classifier

from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.table_info import BiomTable


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    return AnalysisFactory(
        BiomTable("species"),
        metadata_filepath
    )\
        .with_pair_strategy(["unpaired", "paired_concat", "paired_subtract"])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
