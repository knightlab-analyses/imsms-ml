# See how well classifiers trained with a single collection site
# can predict other samples within that same collection site
from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.table_info import BiomTable


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
        BiomTable("species"),
        metadata_filepath,
    ).with_metadata_filter(filters)
()

if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner().run(configure())
