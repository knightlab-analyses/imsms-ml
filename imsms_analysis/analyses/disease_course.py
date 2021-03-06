# Compare models built when subsetting by disease course
from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.table_info import BiomTable


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
        BiomTable("species"),
        metadata_filepath
    ).with_metadata_filter(filters)


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner().run(configure())
