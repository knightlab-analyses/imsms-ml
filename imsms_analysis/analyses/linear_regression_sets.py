# Linear regression was run on training set 0 to determine most important
# categories.  We pass those selected features into an RF model to see how
# it performs.

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    fset1 = FeatureSet.build_feature_set("Test0", "./dataset/feature_sets/fixed_training_set_MS_associated_species_AST_fdr0.05.tsv")
    fsets = FeatureSet.build_feature_sets("./dataset/feature_sets/MS_associated_species_fdr0.05_in_10_training_set.csv")

    # print(fset1.features)
    # print(fsets[0].features)

    facts = []
    for i in range(10):
        linreg = AnalysisFactory(
            ["species"],
            metadata_filepath,
            "TestSet" + str(i)
        ).with_feature_set(fsets[i]).with_training_set(i)
        facts.append(linreg)

    species = AnalysisFactory(
        ["species"],
        metadata_filepath,
        "species"
    )
    facts.append(species)

    return MultiFactory(facts)

    # linreg = AnalysisFactory(
    #     ["species"],
    #     metadata_filepath
    # ).with_feature_set([
    #     FeatureSet.build_feature_set(
    #         "TrainSet0-FDR0.05",
    #         "./dataset/feature_sets/fixed_training_set_MS_associated_species_AST_fdr0.05.tsv"
    #     ),
    #     FeatureSet.build_feature_set(
    #         "TrainSet0-P0.05",
    #         "./dataset/feature_sets/fixed_training_set_MS_associated_species_AST_p0.05.tsv"
    #     ),
    #     FeatureSet.build_feature_set(
    #         "FullDataLinearRegression(Cheating)",
    #         "./dataset/feature_sets/MS_associated_species_AST.tsv"
    #     )
    # ])

    # species = AnalysisFactory(
    #     ["species"],
    #     metadata_filepath,
    #     "species"
    # )
    # return MultiFactory([linreg, species])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner.run(configure())
