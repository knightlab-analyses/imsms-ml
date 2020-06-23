import pandas as pd
from preprocessing import id_parsing, sample_filtering, sample_aggregation

BAD_SAMPLE_PREFIXES = [
    'NA.',
    'UCSF.',
    'COLUMN.',
    'Column.',
    'Q.DOD',
    'Zymo.',
    'Mag.Bead.Zymo.'
]

BAD_SAMPLE_IDS = ["71601-0158", "71601-0158"]


def process_biom(df: pd.DataFrame, valid_sample_ids, verbose=False):
    steps = [
        # Filter out the bad samples (sample prefixes are based on pre-parsed
        # values. do not reorder below id_parsing)
        sample_filtering.build_prefix_filter(BAD_SAMPLE_PREFIXES),
        # Parse the IDs and rename to match metadata
        id_parsing.build(),
        # Run some aggregation function when multiple ids map to the same
        # sample ID, (due to technical replicates)
        sample_aggregation.build("pick"),
        # Filter to rows that match metadata sample ids
        sample_filtering.build_shared_filter(valid_sample_ids),
        # Specifically remove samples that have no household matched pair
        sample_filtering.build_exact_filter(BAD_SAMPLE_IDS)
    ]
    return _run_pipeline(df, steps, verbose)


def process_metadata(df: pd.DataFrame, valid_sample_ids, verbose=False):
    steps = [
        # Filter to rows that match sequence sample ids
        sample_filtering.build_shared_filter(valid_sample_ids),
        # Filter out a specific sample that had no matched household pairing
        sample_filtering.build_exact_filter(BAD_SAMPLE_IDS)
    ]
    return _run_pipeline(df, steps, verbose)


def _run_pipeline(df, steps, verbose=False):
    if verbose:
        print("Input: ")
        print(df)

    for s in steps:
        if verbose:
            print("Begin step:", s)
        df = s(df)
        if verbose:
            print("Result After:", s)
            print(df)
    return df
