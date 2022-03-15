from qiime2 import Artifact, Metadata, Visualization

from imsms_analysis.analysis_runner import SerialRunner, DryRunner, \
    ParallelRunner, SavePreprocessedTables
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_filter import ZebraFilter
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
import pandas as pd

from qiime2.plugins.diversity.methods import alpha, beta
from qiime2.plugins.diversity.visualizers import alpha_group_significance
from qiime2.plugins.diversity.visualizers import beta_group_significance

metadata_filepath = "./dataset/metadata/finrisk_metadata.tsv"
def configure():
    woltka_levels = AnalysisFactory(
        [
            BiomTable("species"),
        ],
        metadata_filepath,
        "species"
    ).with_pair_strategy("unpaired")\
        .with_normalization(Normalization.NONE)\
    .with_metadata_filter(
        MetadataFilter("NoBlanks", "empo_3", ["Animal distal gut"])
    )


    zebra = AnalysisFactory(
        [BiomTable("none")],
        metadata_filepath
    ).with_metadata_filter(
        MetadataFilter("NoBlanks", "empo_3", ["Animal distal gut"])
    )\
        .with_pair_strategy("unpaired")\
        .with_normalization(Normalization.NONE)\
        .with_feature_filter([
        ZebraFilter(.00, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.10, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.25, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.50, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.75, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.90, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.95, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.98, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.99, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.995, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.998, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.999, "./dataset/metadata/finrisk_cov.tsv"),
        ZebraFilter(.9999, "./dataset/metadata/finrisk_cov.tsv"),
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
        df = table.view(pd.DataFrame)
        print(df)
        continue

        alpha_result = alpha(table=table, metric='shannon')
        alpha_diversity = alpha_result.alpha_diversity
        series = alpha_diversity.view(pd.Series)
        print(series)

        # Argh, how do I tell it what I care about?
        vis_alpha = alpha_group_significance(alpha_diversity, metadata)
        print(vis_alpha)
        vis_alpha.visualization.save("tables/"+config.analysis_name+"_alpha_vis.qzv")

        beta_result = beta(table=table, metric='jaccard', pseudocount=1, n_jobs=-2)
        dist_mat = beta_result.distance_matrix

        column = 'sex'
        vis_beta = beta_group_significance(
            distance_matrix=dist_mat,
            metadata=metadata.get_column(column),
            method='permanova',
            pairwise=False
        )
        print(vis_beta)
        vis_beta.visualization.save("tables/"+config.analysis_name+"_beta_vis_jaccard_" + column + ".qzv")
