# Examine the data
from analysis_runner import SerialRunner
from common.analysis_factory import AnalysisFactory
from common.feature_set import FeatureSet

from imsms_analysis.common.table_info import BiomTable


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    return AnalysisFactory(
        BiomTable("genus"),
        metadata_filepath
    )


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    config = list(configure().gen_configurations())[0]
    genome_ids = config.table_info.read_biom_metadata()
    print(genome_ids)
    genome_ids.to_csv("./results/genome_ids.tsv", sep="\t")


