import pandas as pd

from common.named_functor import NamedFunctor


def build_prefix_filter(bad_prefixes):
    return NamedFunctor(
        "Filter Samples By ID Prefix",
        lambda x: _filter_out_sample_id_prefix(x, bad_prefixes)
    )


def build_exact_filter(bad_sample_ids):
    return NamedFunctor(
        "Remove Bad Samples",
        lambda x: _filter_out_sample_ids(x, bad_sample_ids)
    )


def build_shared_filter(valid_ids):
    return NamedFunctor(
        "Filter Samples To Shared IDs",
        lambda x: _filter_by_shared_ids(x, valid_ids)
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
