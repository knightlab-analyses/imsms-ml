import pandas as pd
from preprocessing import id_parsing, sample_filtering, sample_aggregation, \
    normalization, classifier_target
from preprocessing.column_transformation import build_column_filter
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


def process(state: PipelineState, restricted_feature_set=None, verbose=False):
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
    # Subset to rows with a particular metadata value
    # steps.append(sample_filtering.build_whitelist_metadata_value(
    #     "treatment_status",
    #     ['Off', 'Control']
    # ))
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
            household_matched=False
        )
    )
    # Run PCA - This is a bit wonky in the simplex space,
    # and even more wonky in the household concatted rows space.
    # Give this more thought
    # transformation.build_pca(20),  # TODO: 20 might actually be too few!

    return _run_pipeline(state, steps, verbose)


def _run_pipeline(state, steps, verbose=False):
    if verbose:
        print("Input: ")
        print(state)

    for s in steps:
        if verbose:
            print("Begin step:", s)
        state = s(state)
        if verbose:
            print("Result After:", s)
            print(state)
    return state
