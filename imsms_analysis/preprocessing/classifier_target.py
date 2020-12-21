import pandas as pd

from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState
from imsms_analysis.preprocessing.id_parsing import _parse_household_id

from numpy.random import default_rng
import numpy as np

_CONCAT_RANDOM_SEED = 1261399238688719593838

# The LDA accuracy results are all over the place depending on this random seed
# maybe we don't have enough samples to properly subsample for sex bias?
_CHOICE_RANDOM_SEED = 2116932983867891958383


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
    elif pair_strategy == "paired_subtract_sex_balanced":
        return NamedFunctor(
            "Target: " + meta_col_name,
            lambda state, mode:
                matched_pair_subtract_sex_balanced(state, meta_col_name, one_set)
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

def matched_pair_subtract_sex_balanced(state: PipelineState,
                        meta_col_name: str,
                        one_set: set) -> PipelineState:

    state = _target(state, meta_col_name, one_set)
    state.df["__sex__"] = state.meta_df.apply(
        lambda row: 1 if row["sex"] == "F" else 0,
        axis=1)

    state.df['__target__'] = state.target
    state.df['__household__'] = state.df.index
    state.df['__household__'] = state.df['__household__'].apply(_parse_household_id)

    households = state.df['__household__'].tolist()
    households = set(households)

    MM_hh = set()
    MF_hh = set()
    FM_hh = set()
    FF_hh = set()
    for hh in households:
        hh_frame = state.df[state.df['__household__'] == hh]
        if hh_frame["__sex__"].sum() == 2:
            FF_hh.add(hh)
        elif hh_frame["__sex__"].sum() == 0:
            MM_hh.add(hh)
        elif ((hh_frame["__sex__"] == 1) & (hh_frame["__target__"] == 1)).sum() == 1:
            FM_hh.add(hh)
        else:
            MF_hh.add(hh)

    print("Lengths:")
    print(len(MM_hh), len(FF_hh), len(FM_hh), len(MF_hh))
    print("MM")
    print(MM_hh)
    print("FF")
    print(FF_hh)

    # Pick a subset
    r = default_rng(_CHOICE_RANDOM_SEED)
    accept_set = r.choice(sorted(list(FM_hh)), len(MF_hh), replace=False).tolist()

    accept_set = accept_set + list(FF_hh) + list(MM_hh) + list(MF_hh)
    print("ACCEPT SET: ", len(accept_set))
    state.df = state.df[state.df['__household__'].isin(accept_set)]
    state.df = state.df.drop(["__household__", "__target__"], axis=1)

    meta_accept_set = [s.replace("-", "") for s in accept_set]
    state.meta_df = state.meta_df[state.meta_df['household'].isin(meta_accept_set)]

    (left, right) = _split_left_right(state, meta_col_name, one_set)

    left = left.sort_index()
    right = right.sort_index()
    df = right - left

    # TODO FIXME HACK:  Does target's type matter?  Do we need to
    #  turn these into ints/booleans?
    target = df['target'] / 2 + .5

    # Pick subset of households with


    # MM 0
    # FF 0
    # MF -1
    # FM 1
    A = (df['target'] == -1) & (df['__sex__'] == -1)
    B = (df['target'] == -1) & (df['__sex__'] == 0)
    C = (df['target'] == -1) & (df['__sex__'] == 1)
    D = (df['target'] == 1) & (df['__sex__'] == -1)
    E = (df['target'] == 1) & (df['__sex__'] == 0)
    F = (df['target'] == 1) & (df['__sex__'] == 1)

    print(A.sum(), B.sum(), C.sum())
    print(D.sum(), E.sum(), F.sum())

    print((A | B | C | D | E | F).sum())

    df = df.drop('target', axis=1)
    df = df.drop('__sex__', axis=1)

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
