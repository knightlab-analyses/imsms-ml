import pandas as pd

from common.named_functor import NamedFunctor


def build(bad_prefixes):
    return NamedFunctor(
        "Filter Samples By ID Prefix",
        lambda x: _filter_by_sample_id_prefix(x, bad_prefixes)
    )


def _filter_by_sample_id_prefix(df: pd.DataFrame, bad_prefixes) \
        -> pd.DataFrame:

    if len(bad_prefixes) == 0:
        return df

    bad_rows = df.index.str.startswith(bad_prefixes[0])
    for i in range(1, len(bad_prefixes)):
        bad_rows |= df.index.str.startswith(bad_prefixes[i])
    return df[~bad_rows]
