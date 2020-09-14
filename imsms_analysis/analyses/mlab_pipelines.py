# Try out a couple mlab models and custom pipelines
from q2_mlab import ClassificationTask

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    return AnalysisFactory(
        ["species"],
        metadata_filepath
    ).with_algorithm(list(ClassificationTask.algorithms.keys()) + ["RandomForestSVD"])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner.run(configure())
