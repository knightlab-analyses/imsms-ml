# Examine models trained at different levels of taxonomic assignment
from q2_mlab import ClassificationTask

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    FeatureTransformer


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    mbp25 = "./dataset/feature_transforms/mbp_table25.csv"
    mbp30 = "./dataset/feature_transforms/mbp_table30.csv"
    mbp35 = "./dataset/feature_transforms/mbp_table35.csv"
    mog25 = "./dataset/feature_transforms/mog_table25.csv"
    mog30 = "./dataset/feature_transforms/mog_table30.csv"
    mog35 = "./dataset/feature_transforms/mog_table35.csv"

    hla_drb1_1501_households = \
        ['714-0049', '714-0072', '714-0075', '714-0078', '714-0079',
         '714-0086', '714-0094', '714-0101', '714-0102', '714-0107',
         '714-0110', '714-0111', '714-0118', '714-0119', '714-0122',
         '714-0123', '714-0128', '714-0133', '714-0135', '714-0148',
         '714-0149', '714-0157', '714-0161', '714-0162', '714-0165',
         '714-0167', '714-0172', '714-0176', '714-0184', '714-0189',
         '714-0190', '714-0201', '714-0210', '714-0212', '714-0224',
         '714-0254', '714-0255', '716-0009', '716-0015', '716-0020',
         '716-0031', '716-0032', '716-0035', '716-0039', '716-0052',
         '716-0076', '716-0082', '716-0095', '716-0101', '716-0110',
         '716-0137', '716-0141', '716-0143', '716-0160']

    meta_households = [hh[:3] + hh[4:] for hh in hla_drb1_1501_households]

    mbp_shuffle = AnalysisFactory(
        ["none"],
        metadata_filepath
    ).with_feature_transform(
        [FeatureTransformer("MBP30_Shuffle"+str(x), mbp30, shuffle_seed=x)
         for x in range(10)]
    )

    woltka_transforms = AnalysisFactory(
        ["none"],
        metadata_filepath,
    ).with_feature_transform(
        [FeatureTransformer("MBP25", mbp25),
         FeatureTransformer("MBP30", mbp30),
         FeatureTransformer("MBP35", mbp35)])
         # FeatureTransformer("MOG25", mog25),
         # FeatureTransformer("MOG30", mog30),
         # FeatureTransformer("MOG35", mog35)])
    # .with_metadata_filter(
    #     MetadataFilter(
    #         "DRB1_1501",
    #         "household",
    #         meta_households
    #     )
    # )

    # woltka_raw = AnalysisFactory(
    #     ["species", "none"],
    #     metadata_filepath,
    # )
    # .with_metadata_filter(
    #     MetadataFilter(
    #         "DRB1_1501",
    #         "household",
    #         meta_households
    #     )
    # )

    return MultiFactory([woltka_transforms, mbp_shuffle])
    # return MultiFactory([woltka_transforms, woltka_raw])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
