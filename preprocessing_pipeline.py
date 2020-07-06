import pandas as pd
from preprocessing import id_parsing, sample_filtering, sample_aggregation, \
    normalization, classifier_target, transformation

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


def process_biom(df: pd.DataFrame, meta_df: pd.DataFrame, verbose=False):
    steps = [
        # Filter out the bad samples (sample prefixes are based on pre-parsed
        # values. do not reorder below id_parsing)
        sample_filtering.build_prefix_filter(BAD_SAMPLE_PREFIXES),
        # Parse the IDs and rename to match metadata
        id_parsing.build(),
        # Run some aggregation function when multiple ids map to the same
        # sample ID, (due to technical replicates)
        sample_aggregation.build("sum"),
        # Filter to rows that match metadata sample ids
        sample_filtering.build_shared_filter(meta_df.index),
        # TODO:  Ensure data is still paired by removing any samples that no
        #  longer have matched pairs
        # Specifically remove samples that have no household matched pair
        sample_filtering.build_exact_filter(BAD_SAMPLE_IDS),
        # Subset to rows with a particular metadata value
        # sample_filtering.build_whitelist_metadata_value(meta_df,
        #                                                 "treatment_status",
        #                                                 ['Off', 'Control']
        #                                                 ),

        # Apply some normalization strategy to deal with compositionality of
        # the data, stemming from various sources - whether biological effects
        # and sample coverage/amount or from aggregation of varying numbers of
        # technical replicates.
        # TODO:  Some kind of normalization of rows in the dataframe
        #  What are our options?:  CHOOSE 1 (2?)
        #    Rarefaction such that row adds to X
        #    Normalize such that row adds to X
        #    Pseudocounts and Isometric Log Transform (sp?)
        #      Read GNEISS and Fuller (sp?) papers
        #      * AST? - https://huttenhower.sph.harvard.edu/maaslin/
        #        Arc-sin transformation
        #      * --ILR? - Yoshiki's Fave!--
        #      * ALR?
        #      * CLR?
        #      https://en.wikipedia.org/wiki/Compositional_data#Linear_transformations
        #
        # normalization.build("rarefy", 10000),
        normalization.build("divide_total", 10000)
    ]
    return _run_pipeline(df, steps, verbose)


def process_metadata(df: pd.DataFrame, valid_sample_ids, verbose=False):
    steps = [
        # Filter to rows that match sequence sample ids
        sample_filtering.build_shared_filter(valid_sample_ids),
        # Filter out a specific sample that had no matched household pairing
        sample_filtering.build_exact_filter(BAD_SAMPLE_IDS)

        # TODO:  Ensure data is still paired by removing any samples that no
        #  longer have matched pairs
    ]
    return _run_pipeline(df, steps, verbose)


def build_target_column(df: pd.DataFrame,
                        meta_df: pd.DataFrame,
                        verbose=False):
    steps = [
        # TODO: Could ideally try doing PCA after stripping off the target
        #  column so it was the last thing before sending in the model
        #  But doing it before building target column doesn't seem to matter
        #  at all so maybe isn't valuable.
        transformation.build_pca(20),
        # classifier_target.build("disease_state", meta_df),
        classifier_target.build("household_concat", meta_df)
    ]
    return _run_pipeline(df, steps, verbose)


def _run_pipeline(df, steps, verbose=True):
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
