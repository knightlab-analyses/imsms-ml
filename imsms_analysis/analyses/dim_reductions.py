# Try standard dimensionality reductions and embeddings.  If these retain
# useful information, maybe we can visualize results.
from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.events.plot_lda import LDAPlot


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    probstel = FeatureSet.build_feature_set(
        "Probstel",
        "./dataset/feature_sets/literature_review_Probstel_Baranzini_2018.tsv"
    )
    probstel_features = AnalysisFactory(
        "genus",
        metadata_filepath,
    ).with_feature_set([probstel] + probstel.create_univariate_sets("Univariate-"))

    fsets = FeatureSet.build_feature_sets("./dataset/feature_sets/MS_associated_species_fdr0.05_in_10_training_set.csv")

    # umap = AnalysisFactory(
    #     "species",
    #     metadata_filepath,
    #     "UMAP"
    # ).with_umap()\
    #     .with_num_seeds(50)\
    #     .with_pair_strategy("unpaired")

    # pca = AnalysisFactory(
    #     "species",
    #     metadata_filepath,
    #     "PCA(1)"
    # ).with_pca([1])\
    #     .with_num_seeds(50)\
    #     .with_normalization(Normalization("CLR", "CLR"))\
    #     .with_pair_strategy("paired_subtract")

    # facts = []
    # for i in range(10):
    #     linreg = AnalysisFactory(
    #         ["species"],
    #         metadata_filepath,
    #         "TestSet" + str(i)
    #     ).with_lda([1]).with_feature_set(fsets[i])\
    #         .with_training_set(i)\
    #         .with_normalization([Normalization("CLR", "CLR")])\
    #         .with_pair_strategy(["paired_subtract"])
    #     facts.append(linreg)

    # lda = AnalysisFactory(
    #     "genus",
    #     metadata_filepath,
    #     "LDA(1)"
    # ).with_lda([1]) \
    #     .with_normalization([Normalization("CLR", "CLR")])\
    #     .with_pair_strategy(["paired_subtract"])\
    #     .with_num_training_sets(10)\
    #     .with_feature_set([probstel])
    #     # .with_num_seeds(5) \


        # FeatureSet("A", ["572511"]),
        # FeatureSet("B", ["572511", "33042"]),
        # FeatureSet("C", ["572511", "33042", "216851"])]

    # raw = AnalysisFactory(
    #     "species",
    #     metadata_filepath,
    #     "Species"
    # )
    # return MultiFactory([
    #     # umap,
    #     lda,
    #     # pca,
    #     # raw,
    # ])
    # return lda
    return MultiFactory(facts)


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    runner = SerialRunner()
    LDAPlot().hook_events(runner)
    runner.run(configure())
