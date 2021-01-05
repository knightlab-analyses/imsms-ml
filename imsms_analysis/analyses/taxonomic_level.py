# Examine models trained at different levels of taxonomic assignment

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.table_info import BiomTable


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    woltka_levels = AnalysisFactory(
        [BiomTable("phylum"),
         BiomTable("class"),
         BiomTable("order"),
         BiomTable("family"),
         BiomTable("genus"),
         BiomTable("species")],
        metadata_filepath
    )
    woltka_transforms = AnalysisFactory(
        [BiomTable("none"),
         BiomTable("kegg"),
         BiomTable("enzrxn2reaction"),
         BiomTable("pathway2class"),
         BiomTable("reaction2pathway")],
        metadata_filepath
    )

    return MultiFactory([woltka_levels, woltka_transforms])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
