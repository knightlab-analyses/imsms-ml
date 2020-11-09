# Linear regression was run on training set 0 to determine most important
# categories.  We pass those selected features into an RF model to see how
# it performs.

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    # We split the data into 10 50/50 train/test sets (the ten divisions overlap)
    # We ran linear regression on all training sets (see phyloseq)
    # We took top hits that pass fdr threshold
    # We looked at how frequently each species appeared in these top lists
    # The four most frequent appeared in 8 out of 10 lists.
    # See dataset/feature_sets/MS_associated_species_fdr0.05_in_10_training_set.csv
    # Ruthenibacterium lactatiformans
    # Peptococcus niger
    # Coprococcus comes
    # Dorea longicatena
    fset_top_scorers = FeatureSet("TopScorers", ["1550024", "2741", "410072", "88431"])
    fset_combos = fset_top_scorers.create_all_combos()
    facts = []

    facts.append(
        AnalysisFactory(
            ["species"],
            metadata_filepath,
            "species"
        )
    )
    # TODO FIXME HACK:  There is no held out test set that these top scorers
    #  haven't seen before.  So I'm a little worried that we are cheating
    #  here.  If this shows promise, can redo the train set generation to
    #  ensure there is a set that is completely held out from all training sets
    facts.append(
        AnalysisFactory(
            ['species'],
            metadata_filepath
        ).with_feature_set(fset_combos)
    )

    return MultiFactory(facts)


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    SerialRunner().run(configure())
