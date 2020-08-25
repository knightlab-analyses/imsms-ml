# See how well classifiers trained with a single collection site
# can predict other samples within that same collection site
from analysis_runner import SerialRunner, DryRunner
from common.analysis_factory import AnalysisFactory
from common.metadata_filter import MetadataFilter

def configure():
    metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    filters = [
        None,
        MetadataFilter("San Sebastian", "site", ["San Sebastian", "Control"]),
        MetadataFilter("San Francisco", "site", ["San Francisco", "Control"]),
        MetadataFilter("Pittsburgh", "site", ["Pittsburgh", "Control"]),
        MetadataFilter("New York", "site", ["New York", "Control"]),
        MetadataFilter("Edinburgh", "site", ["Edinburgh", "Control"]),
        MetadataFilter("Buenos Aires", "site", ["Buenos Aires", "Control"]),
        MetadataFilter("Boston", "site", ["Boston", "Control"])
    ]
    return AnalysisFactory(
        "species",
        metadata_filepath,
    ).with_metadata_filter(filters)


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    DryRunner.run(configure())
