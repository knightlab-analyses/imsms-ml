import pandas as pd

from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState
from collections import defaultdict


# Filter out any samples that start with one of these prefixes
def build_prefix_filter(bad_prefixes):
    return NamedFunctor(
        "Filter Samples By ID Prefix",
        lambda state, mode: _filter_out_sample_id_prefix(state, bad_prefixes)
    )


# Filter out any samples with these sample ids
def build_exact_filter(bad_sample_ids):
    return NamedFunctor(
        "Remove Bad Samples",
        lambda state, mode: _filter_out_sample_ids(state, bad_sample_ids)
    )


# Only keep samples with ids shared between df and meta_df
def build_shared_filter():
    return NamedFunctor(
        "Filter Samples To Shared IDs",
        lambda state, mode: _filter_by_shared_ids(state)
    )


# Drop any samples with no data for this set of features
def build_filter_out_empty_samples():
    return NamedFunctor(
        "Filter Empty Samples",
        lambda state, mode: _filter_zero_sum(state)
    )


# Keep only samples with a particular metadata value
# (Lets you subset your input data to filter by, for example, medication,
# so that you aren't just seeing differences due to some drug
# Keeps only samples within the specified metadata_values set for the
# metadata_column
def build_whitelist_metadata_value(metadata_column, metadata_values):
    return NamedFunctor(
        "Subset Samples by " + metadata_column +
        " for " + str(metadata_values),
        lambda x, mode: _filter_by_metadata(
            x,
            metadata_column,
            metadata_values
        )
    )


# Removes all samples from df and meta_df that start with a bad prefix.
def _filter_out_sample_id_prefix(state: PipelineState, bad_prefixes) \
        -> PipelineState:

    if len(bad_prefixes) == 0:
        return state

    def _filter(df):
        bad_rows = df.index.str.startswith(bad_prefixes[0])
        for i in range(1, len(bad_prefixes)):
            bad_rows |= df.index.str.startswith(bad_prefixes[i])
        return df[~bad_rows]

    return state.update(
        df=_filter(state.df),
        meta_df=_filter(state.meta_df)
    )


def _filter_out_sample_ids(state: PipelineState, bad_sample_ids) \
        -> PipelineState:
    if len(bad_sample_ids) == 0:
        return state

    def _filter(df):
        bad_rows = df.index.isin(set(bad_sample_ids))
        return df[~bad_rows]

    return state.update(
        df=_filter(state.df),
        meta_df=_filter(state.meta_df)
    )


def _filter_by_shared_ids(state: PipelineState) -> PipelineState:
    df_set = set(state.df.index)
    meta_set = set(state.meta_df.index)
    valid_set = df_set.intersection(meta_set)

    return state.update(
        df=state.df[state.df.index.isin(valid_set)],
        meta_df=state.meta_df[state.meta_df.index.isin(valid_set)]
    )


def _filter_by_metadata(state: PipelineState,
                        meta_col: str,
                        meta_val: set) -> PipelineState:
    values = state.meta_df[meta_col]

    state.df = state.df.join(values)
    state.df = state.df[state.df[meta_col].isin(meta_val)]
    state.df = state.df.drop([meta_col], axis=1)

    state.meta_df = state.meta_df[state.meta_df[meta_col].isin(meta_val)]
    return _filter_to_matched_pairs(state)


# Under some feature transforms, we pick up nothing at all, and are thus
# unable to normalize the data.  This filter removes such samples.
def _filter_zero_sum(state: PipelineState) -> PipelineState:
    state.df['rowsum'] = state.df.sum(axis=1)
    state.df = state.df[state.df['rowsum'] > 0]
    state.df = state.df.drop(['rowsum'], axis=1)
    return _filter_to_matched_pairs(state)


def _filter_to_matched_pairs(state: PipelineState) -> PipelineState:
    # Finrisk has no matched pairs
    return state


