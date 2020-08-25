import pandas as pd

from common.named_functor import NamedFunctor
from state.pipeline_state import PipelineState
from preprocessing.id_parsing import _parse_household_id

from numpy.random import default_rng

_CONCAT_RANDOM_SEED = 1261399238688719593838


def build(meta_col_name: str, one_set: set, pair_strategy="paired_concat"):
    if pair_strategy == "paired_concat":
        return NamedFunctor(
            "Target: " + meta_col_name + "(HouseholdConcat)",
            lambda state, mode:
                matched_pair_concat(state, meta_col_name, one_set)
        )
    elif pair_strategy == "paired_subtract":
        return NamedFunctor(
            "Target: " + meta_col_name + "(HouseholdSubtract)",
            lambda state, mode:
                matched_pair_subtract(state, meta_col_name, one_set)
        )
    elif pair_strategy == "unpaired":
        return NamedFunctor(
            "Target: " + meta_col_name,
            lambda state, mode:
                _target(state, meta_col_name, one_set)
        )

# TODO FIXME HACK:  Should I or should I not guarantee that matched_pair_concat
#  is deterministic?

# concatenate rows corresponding to household.
# Flip a coin to determine whether MS or control comes first within the row.
# Set target = 0 if MS comes first, target = 1 if control comes first.
def matched_pair_concat(state: PipelineState,
                        meta_col_name: str,
                        one_set: set) -> PipelineState:
    (left, right) = _split_left_right(state, meta_col_name, one_set)

    left = left.rename(columns=lambda name: "L"+name)
    right = right.rename(columns=lambda name: "R"+name)

    left = left.sort_index()
    right = right.sort_index()
    df = pd.concat([left, right], axis=1)
    df = df.drop('Ltarget', axis=1)
    target = df['Rtarget']
    df = df.drop('Rtarget', axis=1)
    return state.update(target=target, df=df)


def matched_pair_subtract(state: PipelineState,
                        meta_col_name: str,
                        one_set: set) -> PipelineState:
    (left, right) = _split_left_right(state, meta_col_name, one_set)

    left = left.sort_index()
    right = right.sort_index()
    df = right - left

    # TODO FIXME HACK:  Does target's type matter?  Do we need to
    #  turn these into ints/booleans?
    target = df['target'] / 2 + .5
    df = df.drop('target', axis=1)
    return state.update(target=target, df=df)


def _split_left_right(state, meta_col_name, one_set):
    r = default_rng(_CONCAT_RANDOM_SEED)

    state = _target(state, meta_col_name, one_set)
    df = state.df
    df['target'] = state.target
    df = df.rename(index=_parse_household_id)
    df = df.sort_index()
    splitter = r.integers(2, size=len(df.index) // 2)
    left_rows = []
    right_rows = []
    i = 0
    for t in splitter:
        if t == 0:
            left_rows.append(i)
            right_rows.append(i+1)
        else:
            right_rows.append(i)
            left_rows.append(i+1)
        i += 2

    left = df.iloc[left_rows]
    right = df.iloc[right_rows]

    return (left, right)

def _target(state: PipelineState, meta_col_name: str, one_set: set) \
        -> PipelineState:
    return state.update_target(state.meta_df.apply(
        lambda row: 1 if row[meta_col_name] in one_set else 0,
        axis=1))
