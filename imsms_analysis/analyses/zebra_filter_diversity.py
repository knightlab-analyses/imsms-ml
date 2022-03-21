import math
import traceback
from qiime2 import Artifact, Metadata, Visualization

from imsms_analysis.analysis_runner import SerialRunner, DryRunner, \
    ParallelRunner, SavePreprocessedTables
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_filter import ZebraFilter
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.common.train_test import Passthrough
from imsms_analysis.preprocessing.id_parsing import parse_imsms_id, parse_sol_id, parse_FR02_id, parse_finrisk_id
import pandas as pd

from qiime2.plugins.diversity.methods import alpha, beta
from qiime2.plugins.diversity.visualizers import alpha_group_significance
from qiime2.plugins.diversity.visualizers import beta_group_significance

from imsms_analysis.common.target_set import TargetSet
from skbio import DistanceMatrix
import skbio

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")


finrisk_settings = {
    "user_friendly": "FINRISK",
    "output_name": "finrisk",
    "metadata_fp": "./dataset/metadata/finrisk_metadata.tsv",
    "biom_table": BiomTable("none", "./dataset/biom/finrisk-combined-none.biom"),
    "cov_fp": "./dataset/metadata/finrisk_cov.tsv",
    "metadata_filter": MetadataFilter("NoBlanks", "sex", ["male", "female"]),
    "target_set": TargetSet("Male/Female", "sex", ["male"]),
    "id_parse_func": parse_finrisk_id,
    "normalization": [Normalization.RAREFY10K, Normalization.RAREFY100K, Normalization.RAREFY500K]
}
sol_settings = {
    "user_friendly": "SOL",
    "output_name": "sol",
    "metadata_fp": "./dataset/metadata/sol_prep_metadata.tsv",
    "biom_table": BiomTable("none", "./dataset/biom/sol_public_99006-none.biom"),
    "cov_fp": "./dataset/metadata/finrisk_cov.tsv",
    "metadata_filter": MetadataFilter("NoBlanks", "sex", ["male", "female"]),
    "target_set": TargetSet("Male/Female", "sex", ["male"]),
    "id_parse_func": parse_sol_id,
    "normalization": [Normalization.RAREFY10K, Normalization.RAREFY100K, Normalization.RAREFY500K]
}
imsms_settings = {
    "user_friendly": "iMSMS",
    "output_name": "imsms",
    "metadata_fp": "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    "biom_table": BiomTable("none", "./dataset/biom/imsms-combined-none.biom"),
    "cov_fp": "./dataset/metadata/imsms_cov.csv",
    "metadata_filter": MetadataFilter("NoBlanks", "sex", ["M", "F"]),
    "target_set": TargetSet("Male/Female", "sex", ["M"]),
    "id_parse_func": parse_imsms_id,
    "normalization": [Normalization.RAREFY10K, Normalization.RAREFY100K, Normalization.RAREFY500K]
}

settings = finrisk_settings

metadata_filepath = settings["metadata_fp"]
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
        [settings["biom_table"]],
        settings["metadata_fp"]
    ) \
        .with_metadata_filter(settings["metadata_filter"])\
        .with_target_set([settings["target_set"]])\
        .with_train_test(Passthrough())\
        .with_pair_strategy("unpaired")\
        .with_normalization(settings["normalization"])\
        .with_id_parse_func(settings["id_parse_func"])\
        .with_feature_filter(
            [ZebraFilter(round(0.05 * x, 2), settings["cov_fp"]) for x in range(0,20)] +
            [
                ZebraFilter(.96, settings["cov_fp"]),
                ZebraFilter(.97, settings["cov_fp"]),
                ZebraFilter(.98, settings["cov_fp"]),
                ZebraFilter(.99, settings["cov_fp"]),
                ZebraFilter(.999, settings["cov_fp"]),
            ]
    )

    return MultiFactory([
        # woltka_levels,
        zebra,
    ])


def plot_zebra_summary(factory, dataset_name):
    analysis_names = []
    zebra_thresh = []
    num_features = []
    sample_sizes = []
    rarefy_count = []
    for config in factory.gen_configurations():
        print(config.analysis_name)
        path = "tables/"+config.analysis_name+"_train.qza"
        table = Artifact.load(path)
        df = table.view(pd.DataFrame)

        analysis_names.append(config.analysis_name)
        zebra_thresh.append(float(config.analysis_name.split(":")[1].split("-")[0]))
        rarefy_count.append(config.analysis_name.split("-")[1])
        sample_sizes.append(df.sum(axis=1))
        num_features.append(df.shape[1])

    print(num_features)

    print(len(sample_sizes))
    feature_count_df = pd.DataFrame(data={
        "zebra_thresh": zebra_thresh,
        "rarefy_count": rarefy_count,
        "num_features": num_features
    })

    ax = feature_count_df.set_index("zebra_thresh").groupby('rarefy_count')["num_features"].plot(legend=True)
    for key in ["Rarefy10k", "Rarefy100k", "Rarefy500k"]:
        axes = ax[key]
        handles, labels = axes.get_legend_handles_labels()
        print(handles, labels)
        axes.legend([handles[1],handles[0],handles[2]], [labels[1],labels[0],labels[2]])


# plt.scatter(zebra_thresh, num_features)
    plt.xlabel("Zebra Coverage Threshold")
    plt.ylabel("Features Passing Coverage Threshold")
    plt.title(dataset_name + " Features By Coverage")
    plt.show()

    sum_df = pd.DataFrame(data=sample_sizes, index=analysis_names)
    sum_df = sum_df.transpose()
    sum_df = sum_df.applymap(math.log10)
    sum_df.columns = zebra_thresh
    sum_df.boxplot()
    plt.xlabel("Zebra Coverage Threshold")
    plt.ylabel("log10(#Sample Reads)")
    plt.title(dataset_name + " Sample Read Counts Post Filtering")
    plt.show()


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    factory = configure()
    # SavePreprocessedTables().run(factory)
    metadata = Metadata.load(metadata_filepath)
    print(metadata)

    plot_zebra_summary(factory, settings["user_friendly"])

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

            print(table)

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

            try:
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
            except:
                traceback.print_exc()

        result_df = pd.DataFrame(
            {
                "analysis_name":names,
                "metric":metrics,
                "pvalue":pval,
                "pseudo-F":pseudof
            }
        )
        result_df.to_csv("./results/" + settings["output_name"] + "_zebra_" + metric + "_" + column +".tsv", sep='\t')

