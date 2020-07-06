import pandas as pd

from common.named_functor import NamedFunctor


# Filter out any samples that start with one of these prefixes
def build_prefix_filter(bad_prefixes):
    return NamedFunctor(
        "Filter Samples By ID Prefix",
        lambda x: _filter_out_sample_id_prefix(x, bad_prefixes)
    )


# Filter out any samples with these sample ids
def build_exact_filter(bad_sample_ids):
    return NamedFunctor(
        "Remove Bad Samples",
        lambda x: _filter_out_sample_ids(x, bad_sample_ids)
    )


# Only keep samples with ids within this set
def build_shared_filter(valid_ids):
    return NamedFunctor(
        "Filter Samples To Shared IDs",
        lambda x: _filter_by_shared_ids(x, valid_ids)
    )


# Subset samples by metadata column (Lets you subset your input data to filter
# by, for example, medication, so that you aren't just seeing differences due
# to some drug
# Keeps only samples within the specified metadata_values set for the
# metadata_column
def build_whitelist_metadata_value(meta_df, metadata_column, metadata_values):
    return NamedFunctor(
        "Subset Samples by " + metadata_column +
        " for " + str(metadata_values),
        lambda x: _filter_by_metadata(x,
                                      meta_df,
                                      metadata_column,
                                      metadata_values)
    )


def _filter_out_sample_id_prefix(df: pd.DataFrame, bad_prefixes) \
        -> pd.DataFrame:

    if len(bad_prefixes) == 0:
        return df

    bad_rows = df.index.str.startswith(bad_prefixes[0])
    for i in range(1, len(bad_prefixes)):
        bad_rows |= df.index.str.startswith(bad_prefixes[i])
    return df[~bad_rows]


def _filter_out_sample_ids(df: pd.DataFrame, bad_sample_ids) -> pd.DataFrame:
    if len(bad_sample_ids) == 0:
        return df
    bad_rows = df.index.isin(set(bad_sample_ids))
    return df[~bad_rows]


def _filter_by_shared_ids(df: pd.DataFrame, valid_sample_ids):
    valid_set = set(valid_sample_ids)
    good_rows = df.index.isin(valid_set)
    return df[good_rows]


def _filter_by_metadata(df: pd.DataFrame, meta_df: pd.DataFrame,
                        meta_col, meta_val):
    values = meta_df[meta_col]
    df = df.join(values)
    df = df[df[meta_col].isin(meta_val)]
    df = df.drop([meta_col], axis=1)
    return df
