# Examine Akkermansia, the most often reported feature
from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.events.plot_lda import LDAPlot


def configure():
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

    akkermansia_feature_set = FeatureSet.build_feature_set(
        "Akkermansia (all)",
        "./dataset/feature_sets/just_akkermansia.tsv"
    )
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    return AnalysisFactory(
        BiomTable("species"),
        metadata_filepath
    )\
    .with_feature_set(akkermansia_feature_set.create_univariate_sets()) \
    .with_pair_strategy(["unpaired", "paired_subtract_sex_balanced"]) \
    .with_normalization([Normalization.CLR, Normalization.DEFAULT]) \
    .with_metadata_filter([
        None,
        MetadataFilter(
            "DRB1_1501",
            "household",
            meta_households
        )
    ])
    # .with_lda([1]) \



if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    runner = SerialRunner()
    lda_plot = LDAPlot(rows=4, enable_plots=False)
    lda_plot.hook_events(runner)
    runner.run(configure())
    lda_plot.print_acc()


