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
    # woltka_levels = AnalysisFactory(
    #     [
    #         BiomTable("species"),
    #     ],
    #     metadata_filepath,
    #     "species"
    # ).with_pair_strategy("unpaired")\
    #     .with_normalization(Normalization.NONE)\
    # .with_metadata_filter(
    #     MetadataFilter("NoBlanks", "empo_3", ["Animal distal gut"])
    # )


    zebra = AnalysisFactory(
        [BiomTable("none")],
        metadata_filepath
    ).with_metadata_filter(
        MetadataFilter("NoBlanks", "empo_3", ["Animal distal gut"])
    )\
        .with_pair_strategy("unpaired")\
        .with_normalization(Normalization.NONE)\
        .with_feature_filter(
            [ZebraFilter(round(0.05 * x, 2), "./dataset/metadata/finrisk_cov.tsv") for x in range(0,20)] +
            [
                ZebraFilter(.96, "./dataset/metadata/finrisk_cov.tsv"),
                ZebraFilter(.97, "./dataset/metadata/finrisk_cov.tsv"),
                ZebraFilter(.98, "./dataset/metadata/finrisk_cov.tsv"),
                ZebraFilter(.99, "./dataset/metadata/finrisk_cov.tsv"),
                ZebraFilter(.999, "./dataset/metadata/finrisk_cov.tsv"),
            ]
    )

    return MultiFactory([
        # woltka_levels,
        zebra,
    ])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    factory = configure()
    SavePreprocessedTables().run(factory)
    metadata = Metadata.load(metadata_filepath)
    print(metadata)

    column = 'sex'
    for metric in ['jaccard', 'aitchison']:
        names = []
        metrics = []
        pval = []
        pseudof = []
        for config in factory.gen_configurations():
            print(config.analysis_name)
            path = "tables/"+config.analysis_name+"_train.qza"
            table = Artifact.load(path)

            # alpha_result = alpha(table=table, metric='shannon')
            # alpha_diversity = alpha_result.alpha_diversity
            # series = alpha_diversity.view(pd.Series)
            # print(series)
            #
            # # Argh, how do I tell it what I care about?
            # vis_alpha = alpha_group_significance(alpha_diversity, metadata)
            # print(vis_alpha)
            # vis_alpha.visualization.save("tables/"+config.analysis_name+"_alpha_vis.qzv")

            beta_result = beta(table=table, metric=metric, pseudocount=1, n_jobs=-2)
            dist_mat = beta_result.distance_matrix.view(DistanceMatrix)

            result = skbio.stats.distance.permanova(dist_mat, metadata.to_dataframe(), column=column)

            # vis_beta = beta_group_significance(
            #     distance_matrix=dist_mat,
            #     metadata=metadata.get_column(column),
            #     method='permanova',
            #     pairwise=False
            # )
            # print(vis_beta)
            # vis_beta.visualization.save("tables/"+config.analysis_name+"_beta_vis_jaccard_" + column + ".qzv")

            print(config.analysis_name, result['p-value'], result['test statistic'])

            names.append(config.analysis_name)
            metrics.append(metric)
            pval.append(result['p-value'])
            pseudof.append(result['test statistic'])

        result_df = pd.DataFrame(
            {
                "analysis_name":names,
                "metric":metrics,
                "pvalue":pval,
                "pseudo-F":pseudof
            }
        )
        result_df.to_csv("./results/finrisk_zebra_" + metric + "_" + column +".tsv", sep='\t')

