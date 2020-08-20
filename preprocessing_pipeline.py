import pandas as pd

from dataset.sample_sets.fixed_training_set import retrieve_training_set
from preprocessing import id_parsing, sample_filtering, sample_aggregation, \
    normalization, classifier_target, train_test_split, column_transformation
from preprocessing.column_transformation import build_column_filter
from preprocessing.train_test_split import TrainTest
from state.pipeline_state import PipelineState

BAD_SAMPLE_PREFIXES = [
    'NA.',
    'UCSF.',
    'COLUMN.',
    'Column.',
    'Q.DOD',
    'Zymo.',
    'Mag.Bead.Zymo.'
]

BAD_SAMPLE_IDS = ["71601-0158", "71602-0158"]


def process(state: PipelineState,
            restricted_feature_set: list = None,
            training_set_index: int = 0,
            verbose=False,
            pair_strategy="household_concat",
            metadata_filter=None,
            dim_reduction=None):
    filtered = _filter_samples(state, verbose)
    train, test = _split_test_set(filtered,
                                  training_set_index,
                                  verbose)
    return _apply_transforms(train,
                             test,
                             restricted_feature_set,
                             verbose,
                             pair_strategy=pair_strategy,
                             metadata_filter=metadata_filter,
                             dim_reduction=dim_reduction)


# Run all steps required before we can split out the test set.  This must be
# restricted to operations that can be done at the level of individual samples
# (or technically paired samples of households), so as to avoid any interaction
# between test data and training data.
def _filter_samples(state: PipelineState,
                    verbose=False):
    # noinspection PyListCreation
    steps = []

    # Filter out the bad samples (sample prefixes are based on pre-parsed
    # values. do not reorder below id_parsing)
    steps.append(sample_filtering.build_prefix_filter(BAD_SAMPLE_PREFIXES))
    # Parse the IDs and rename to match metadata
    steps.append(id_parsing.build())
    # Run some aggregation function when multiple ids map to the same
    # sample ID, (due to technical replicates)
    steps.append(sample_aggregation.build("sum"))
    # Filter to rows shared between samples and metadata
    steps.append(sample_filtering.build_shared_filter())
    # Manually remove samples that have no household matched pair
    steps.append(sample_filtering.build_exact_filter(BAD_SAMPLE_IDS))
    # Filter out any samples that have row sum zero, these will be impossible
    # to normalize later.
    steps.append(sample_filtering.build_filter_out_empty_samples())

    return _run_pipeline(state, steps, verbose, mode='filter')


# The test set must be split out at the level of household pairs.  This should
# be done as early in the processing as possible to avoid accidental leakage
# of test set data into the processing.  It is not acceptable to learn
# parameters from the test set, so any type of learned feature (Like PCA)
# must store its settings (ie, what column vectors to use) based on training
# set data, then reuse those transformations on the test set.
def _split_test_set(state: PipelineState,
                    training_set_index=0,
                    verbose=False) -> TrainTest:
    train_set_households = retrieve_training_set(training_set_index)
    return train_test_split.split_fixed_set(state,
                                            train_set_households,
                                            verbose)
    # return train_test_split.split(state,
    #                               .5,
    #                               verbose)


def _apply_transforms(train_state: PipelineState,
                      test_state: PipelineState,
                      restricted_feature_set: list = None,
                      verbose=False,
                      pair_strategy="paired_concat",
                      metadata_filter=None,
                      dim_reduction=None):
    # noinspection PyListCreation
    steps = []

    # Subset to household pairs whose individual samples are within particular
    # metadata values.  Can use these to determine if your model is detecting
    # microbes correlating with confounding variables.
    if metadata_filter is not None:
        steps.append(sample_filtering.build_whitelist_metadata_value(
            metadata_filter.column_name,
            metadata_filter.acceptable_values
        ))
    # Apply some normalization strategy to deal with compositionality of
    # the data, stemming from various sources - whether biological effects
    # and sample coverage/amount or from aggregation of varying numbers of
    # technical replicates.
    steps.append(normalization.build("divide_total", 10000))
    if restricted_feature_set is not None:
        steps.append(build_column_filter(restricted_feature_set))

    # Build target series
    steps.append(
        classifier_target.build(
            "disease",
            {"MS"},
            pair_strategy=pair_strategy
        )
    )
    # Run PCA - This is a bit wonky in the simplex space,
    # and even more wonky in the household concatted rows space.
    # Give this more thought
    # Further, the PCA must be learned on the training set
    # (With a separate learned feature per cross validation index!)
    # and applied on the test set (no learning PCA on the test data!)
    # So keep this disabled until we can rethink how to structure this.
    if dim_reduction is not None:
        if dim_reduction.transform == "pca":
            steps.append(column_transformation.build_pca(**dim_reduction.kwargs))  # TODO: 20 might actually be too few!
        elif dim_reduction.transform == "umap":
            steps.append(column_transformation.build_umap(**dim_reduction.kwargs))
        else:
            raise Exception("Unknown Transform:" + dim_reduction.transform)

    train, test = (
        _run_pipeline(train_state, steps, verbose, mode='train'),
        _run_pipeline(test_state, steps, verbose, mode='test')
    )
    return train, test


def _run_pipeline(state, steps, verbose=False, mode='train'):
    if verbose:
        print("Input: ")
        print(state)

    for s in steps:
        if verbose:
            print("Begin Step:", s)
        state = s(state, mode)
        if verbose:
            print("Result After:", s)
            print(state)
    return state
