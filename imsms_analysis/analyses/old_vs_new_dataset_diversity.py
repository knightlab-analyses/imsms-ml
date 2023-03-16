from skbio import DistanceMatrix
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

import skbio

from imsms_analysis.common.train_test import TrainTest, Passthrough

# TODO FIXME HACK: Needs a different method to sex balance the dataset since we can't subtract and use alpha diversity metrics.

old_metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"
combined_metadata_filepath = "./dataset/metadata/combined_iMSMS_metadata.tsv"


def build_combined_metadata():
    old_meta = Metadata.load(old_metadata_filepath).to_dataframe()
    old_meta["prep"] = "old"
    new_meta = Metadata.load(new_metadata_filepath).to_dataframe()
    new_meta["prep"] = "new"

    print(old_meta.head())
    print(new_meta.head())
    old_cols = set(old_meta.columns)
    new_cols = set(new_meta.columns)
    matched_cols = old_cols.intersection(new_cols)
    old_only = old_cols.difference(new_cols)
    new_only = new_cols.difference(old_cols)

    print("Matched")
    print(sorted(list(matched_cols)))
    print("Only Old")
    print(sorted(list(old_only)))
    print("Only New")
    print(sorted(list(new_only)))

    matched_cols = list(sorted(list(matched_cols)))
    old_meta = old_meta[matched_cols]
    new_meta = new_meta[matched_cols]

    keep_new = ~new_meta.index.isin(old_meta.index)
    new_meta = new_meta.loc[keep_new,:]

    final = pd.concat([old_meta, new_meta], axis=0)
    final.index.name = "sampleid"
    final.to_csv(combined_metadata_filepath, sep='\t')


def configure():
    old_fact = AnalysisFactory(
        BiomTable("none"),
        old_metadata_filepath,
        "old_data"
    ) \
        .with_pair_strategy("unpaired") \
        .with_normalization(Normalization.NONE) \
        .with_train_test(Passthrough())

    new_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        new_metadata_filepath,
        "new_data"
    ) \
        .with_pair_strategy("unpaired") \
        .with_normalization(Normalization.NONE) \
        .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
        .with_train_test(Passthrough())

    return MultiFactory([old_fact, new_fact])


def configure_both():
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
        .with_pair_strategy("unpaired") \
        .with_normalization(Normalization.NONE) \
        .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
        .with_train_test(Passthrough())
    return both_fact


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    # build_combined_metadata()
    # exit(-1)

    multi_fact = configure()
    SavePreprocessedTables().run(multi_fact)
    both_fact = configure_both()
    SavePreprocessedTables().run(both_fact)

    old_metadata = Metadata.load(old_metadata_filepath)
    new_metadata = Metadata.load(new_metadata_filepath)
    both_metadata = Metadata.load(combined_metadata_filepath)

    ALPHA = False
    ALPHA_DIFF_BOTH = False
    BETA = False
    BETA_DIFF_BOTH = False

    column = 'sex'
    if ALPHA:
        for metric in ['shannon', 'chao1']:
            for config in multi_fact.gen_configurations():
                print(config.analysis_name)
                path = "tables/"+config.analysis_name+"_train.qza"
                table = Artifact.load(path)

                alpha_result = alpha(table=table, metric=metric)
                alpha_diversity = alpha_result.alpha_diversity
                series = alpha_diversity.view(pd.Series)

                print(series)

                # Argh, how do I tell it what I care about?
                if "old" in config.analysis_name:
                    vis_alpha = alpha_group_significance(alpha_diversity, old_metadata)
                else:
                    vis_alpha = alpha_group_significance(alpha_diversity, new_metadata)

                print(vis_alpha)
                vis_alpha.visualization.save("tables/"+config.analysis_name+"_alpha_vis.qzv")

    if ALPHA_DIFF_BOTH:
        for metric in ['shannon', 'chao1']:
            for config in configure_both().gen_configurations():
                print(config.analysis_name)
                path = "tables/"+config.analysis_name+"_train.qza"
                table = Artifact.load(path)

                alpha_result = alpha(table=table, metric=metric)
                alpha_diversity = alpha_result.alpha_diversity
                series = alpha_diversity.view(pd.Series)

                print(series)

                # Argh, how do I tell it what I care about?
                vis_alpha = alpha_group_significance(alpha_diversity, both_metadata)

                print(vis_alpha)
                vis_alpha.visualization.save("tables/"+config.analysis_name+"_"+metric+"_alpha_vis.qzv")

    if BETA:
        for metric in ['aitchison']:
            names = []
            metrics = []
            pval = []
            pseudof = []
            for config in multi_fact.gen_configurations():
                print(config.analysis_name)
                path = "tables/"+config.analysis_name+"_train.qza"
                table = Artifact.load(path)

                beta_result = beta(table=table, metric=metric, pseudocount=1, n_jobs=-2)
                dist_mat = beta_result.distance_matrix.view(DistanceMatrix)
                if "old" in config.analysis_name:
                    metadata = old_metadata
                else:
                    metadata = new_metadata
                result = skbio.stats.distance.permanova(dist_mat, metadata.to_dataframe(), column="sex")

                # vis_beta = beta_group_significance(
                #     distance_matrix=dist_mat, # TODO: What kind of distance matrix does it want??
                #     metadata=metadata.get_column('disease'),
                #     method='permanova',
                #     pairwise=False
                # )
                # print(vis_beta)
                # vis_beta.visualization.save("tables/"+config.analysis_name+"_beta_vis_jaccard_disease.qzv")

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
            result_df.to_csv("./results/" + metric + "_" + column + ".tsv", sep='\t')

    if BETA_DIFF_BOTH:
        column = "disease"
        for metric in ['aitchison']:
            names = []
            metrics = []
            pval = []
            pseudof = []
            for config in configure_both().gen_configurations():
                print(config.analysis_name)
                path = "tables/"+config.analysis_name+"_train.qza"
                table = Artifact.load(path)

                beta_result = beta(table=table, metric=metric, pseudocount=1, n_jobs=-2)
                dist_mat = beta_result.distance_matrix.view(DistanceMatrix)
                result = skbio.stats.distance.permanova(dist_mat, both_metadata.to_dataframe(), column=column)

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
            result_df.to_csv("./results/" + metric + "_" + column + ".tsv", sep='\t')
