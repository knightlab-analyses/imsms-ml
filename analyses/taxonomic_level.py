# Examine models trained at different levels of taxonomic assignment

from analysis_runner import SerialRunner, DryRunner
from common.analysis_factory import AnalysisFactory, MultiFactory


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    woltka_levels = AnalysisFactory(
        ["phylum", "class", "order", "family", "genus", "species"],
        metadata_filepath
    )
    woltka_transforms = AnalysisFactory(
        ["enzrxn2reaction", "none", "pathway2class", "reaction2pathway"],
        metadata_filepath
    )

    return MultiFactory([woltka_levels, woltka_transforms])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner.run(configure())
