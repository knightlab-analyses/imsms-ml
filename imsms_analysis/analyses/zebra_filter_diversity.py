from qiime2 import Artifact, Metadata, Visualization

from imsms_analysis.analysis_runner import SerialRunner, DryRunner, \
    ParallelRunner, SavePreprocessedTables
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_filter import ZebraFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
import pandas as pd

from qiime2.plugins.diversity.methods import alpha, beta
from qiime2.plugins.diversity.visualizers import alpha_group_significance
from qiime2.plugins.diversity.visualizers import beta_group_significance

metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
def configure():
    woltka_levels = AnalysisFactory(
        [
            BiomTable("species"),
        ],
        metadata_filepath,
        "species"
    ).with_pair_strategy("unpaired")\
        .with_normalization(Normalization.NONE)
    zebra = AnalysisFactory(
        [BiomTable("none")],
        metadata_filepath
    ).with_pair_strategy("unpaired")\
        .with_normalization(Normalization.NONE)\
        .with_feature_filter([
        ZebraFilter(.00, "../zebra.csv"),
        ZebraFilter(.10, "../zebra.csv"),
        ZebraFilter(.25, "../zebra.csv"),
        ZebraFilter(.50, "../zebra.csv"),
        ZebraFilter(.75, "../zebra.csv"),
        ZebraFilter(.90, "../zebra.csv"),
        ZebraFilter(.95, "../zebra.csv"),
        ZebraFilter(.98, "../zebra.csv"),
        ZebraFilter(.99, "../zebra.csv"),
        ZebraFilter(.995, "../zebra.csv"),
        ZebraFilter(.998, "../zebra.csv"),
        ZebraFilter(.999, "../zebra.csv"),
        ZebraFilter(.9999, "../zebra.csv"),
    ])

    return MultiFactory([
        woltka_levels,
        zebra,
    ])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    factory = configure()
    # SavePreprocessedTables().run(factory)
    metadata = Metadata.load(metadata_filepath)
    print(metadata)

    for config in factory.gen_configurations():
        print(config.analysis_name)
        path = "tables/"+config.analysis_name+"_train.qza"
        table = Artifact.load(path)

        alpha_result = alpha(table=table, metric='shannon')
        alpha_diversity = alpha_result.alpha_diversity
        series = alpha_diversity.view(pd.Series)

        print(series)

        # Argh, how do I tell it what I care about?
        # vis_alpha = alpha_group_significance(alpha_diversity, metadata)
        # print(vis_alpha)
        # vis_alpha.visualization.save("tables/"+config.analysis_name+"_alpha_vis.qzv")

        beta_result = beta(table=table, metric='jaccard', pseudocount=1, n_jobs=-2)
        dist_mat = beta_result.distance_matrix

        vis_beta = beta_group_significance(
            distance_matrix=dist_mat,
            metadata=metadata.get_column('disease'),
            method='permanova',
            pairwise=False
        )
        print(vis_beta)
        vis_beta.visualization.save("tables/"+config.analysis_name+"_beta_vis_jaccard_disease.qzv")
