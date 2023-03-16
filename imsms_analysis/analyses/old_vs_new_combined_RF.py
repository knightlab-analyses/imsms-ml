from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.common.train_test import Passthrough, SplitByMetadata, \
    PairedSplit
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    ChainedTransform, RelativeAbundanceFilter, PairwisePearsonTransform

old_metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"
combined_metadata_filepath = "./dataset/metadata/combined_iMSMS_metadata.tsv"


def configure_both():

    df_processing = ChainedTransform(
        [
            RelativeAbundanceFilter(1/10000),
            PairwisePearsonTransform(.95)
        ]
    )

    old_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/combined-none.biom"
        ]),
        combined_metadata_filepath,
        "old"
    ) \
        .with_pair_strategy(["paired_subtract_sex_balanced"]) \
        .with_normalization(Normalization.DEFAULT) \
        .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
        .with_train_test(
        [
            PairedSplit()
        ])\
        .with_feature_transform(df_processing)

    new_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        combined_metadata_filepath,
        "new"
    ) \
        .with_pair_strategy(["paired_subtract_sex_balanced"]) \
        .with_normalization(Normalization.DEFAULT) \
        .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
        .with_train_test(
        [
            PairedSplit()
        ])\
        .with_feature_transform(df_processing)

    both_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/combined-none.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        combined_metadata_filepath,
        "combined_data"
    ) \
        .with_pair_strategy(["paired_subtract_sex_balanced"]) \
        .with_normalization(Normalization.DEFAULT) \
        .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
        .with_train_test(
            [
                SplitByMetadata(meta_col="prep", train_meta=["old"]),
                SplitByMetadata(meta_col="prep", train_meta=["new"]),
                PairedSplit()
            ]
        ) \
        .with_feature_transform(df_processing)

    return MultiFactory([old_fact, new_fact, both_fact])
    # return new_fact


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner().run(configure_both())
