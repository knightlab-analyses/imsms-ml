# Examine the data
from analysis_runner import SerialRunner
from common import biom_util
from common.analysis_factory import AnalysisFactory
from common.feature_set import FeatureSet


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    return AnalysisFactory(
        "genus",
        metadata_filepath
    )


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    config = list(configure().gen_configurations())[0]
    print(config.biom_filepath)
    genome_ids = biom_util.read_biom_metadata(config.biom_filepath)
    print(genome_ids)
    genome_ids.to_csv("./results/genome_ids.tsv", sep="\t")


