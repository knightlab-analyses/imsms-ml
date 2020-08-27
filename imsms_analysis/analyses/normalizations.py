# Try CLR, ALR, Rarefaction, AST, normalize to 10000 etc here to see if these
# transforms affect how the model learns.
from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.normalization import Normalization


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    return AnalysisFactory(
        "species",
        metadata_filepath
    ).with_normalization([Normalization("CLR", "CLR"),
                          Normalization("rarefy", "rarefy", target_count=10000),
                          Normalization("divide_total", "divide_total", target_count=10000)])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner.run(configure())
