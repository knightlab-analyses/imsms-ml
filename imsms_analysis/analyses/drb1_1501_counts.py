# Examine Akkermansia, the most often reported feature
from imsms_analysis.analysis_runner import SerialRunner, DryRunner, TableRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.common.train_test import Passthrough
from imsms_analysis.events.plot_lda import LDAPlot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")


def configure(drb1_1501):
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    akkermansia_feature_set = FeatureSet.build_feature_set(
        "Akkermansia (all)",
        "./dataset/feature_sets/just_akkermansia.tsv"
    )

    baseline_downsample = AnalysisFactory(
        BiomTable("species"),
        metadata_filepath,
        "downsample"
    ) \
        .with_pair_strategy(["unpaired"]) \
        .with_normalization([Normalization.CLR]) \
        .with_downsampling(126)

    baseline_downsample_2 = AnalysisFactory(
        BiomTable("species"),
        metadata_filepath,
        "downsample_paired"
    ) \
        .with_pair_strategy(["paired_subtract_sex_balanced"]) \
        .with_normalization([Normalization.CLR]) \
        .with_downsampling(46)

    baseline = AnalysisFactory(
        BiomTable("species"),
        metadata_filepath,
        "baseline"
    ) \
        .with_pair_strategy(["unpaired", "paired_subtract_sex_balanced"]) \
        .with_normalization([Normalization.CLR]) \
        # .with_feature_set(akkermansia_feature_set)

    haplotyped_individuals =  AnalysisFactory(
        BiomTable("species"),
        metadata_filepath,
        'haplotyped'
    ) \
        .with_pair_strategy(["unpaired", "paired_subtract_sex_balanced"]) \
        .with_normalization([Normalization.CLR]) \
        .with_metadata_filter([
            MetadataFilter(
                "DRB1_1501",
                "sampleid",
                drb1_1501.index
            )
        ]) \
        # .with_feature_set(akkermansia_feature_set) \

    return haplotyped_individuals
    # return baseline_downsample_2
    return MultiFactory([baseline_downsample, baseline_downsample_2, baseline, haplotyped_individuals])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    df = pd.read_csv("./dataset/allele_info/HLA_alleles_iMSMS_samples.txt", sep='\t')
    drb1_1501 = df['DRB1:15:01']
    print("Num Pos:", drb1_1501.sum())

    # 278 haplotyped individuals
    # 87 are positive for the DRB1_1501

    fact = configure(drb1_1501)
    # SerialRunner().run(fact)
    config,train,test = TableRunner().run(fact)[0]

    train.df['drb1_1501'] = drb1_1501
    print(train.df)
    print(train.meta_df)

    orthogonal_akkermansias = ['1262691', '239935', '1263034', '1574265', '1679444']
    akkermansia_names = [
        'Akkermansia sp. CAG 344',
        'Akkermansia muciniphila',
        'Akkermansia muciniphila sp. CAG 154',
        'Akkermansia sp. KLE1798',
        'Akkermansia glycaniphila'
    ]

    rough = train.df[orthogonal_akkermansias + ['drb1_1501']]
    print(rough)

    # sns.scatterplot(x='1262691', y='239935', hue='drb1_1501', data=rough)
    # plt.show()

    fig, axes = plt.subplots(5,5, sharex=True, sharey=True)
    for y in range(5):
        for x in range(5):
            xs = orthogonal_akkermansias[x]
            ys = orthogonal_akkermansias[y]
            ax = axes[y,x]
            sns.scatterplot(x=xs, y=ys, ax=ax, hue='drb1_1501', data=rough, legend=False)

    fig, axes = plt.subplots(1, 5)
    for y in range(5):
        g = sns.swarmplot(ax=axes[y], x="drb1_1501", y=orthogonal_akkermansias[y], data=rough)
        axes[y].set_ylabel(akkermansia_names[y])
    fig.tight_layout()
    plt.show()
