# Compare models built when subsetting by disease course
from analysis_runner import SerialRunner
from common.analysis_factory import AnalysisFactory
from common.metadata_filter import MetadataFilter


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    filters = [
        None,  # TODO:  This comes back named None, maybe some way to create an
               #  identity filter with a specified name?
        MetadataFilter("RRMS", "disease_course", ["RRMS", "Control"]),
        MetadataFilter("PPMS", "disease_course", ["PPMS", "Control"]),
        MetadataFilter("SPMS", "disease_course", ["SPMS", "Control"])
    ]

    return AnalysisFactory(
        "species",
        metadata_filepath
    ).with_metadata_filter(filters)


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner.run(configure())
