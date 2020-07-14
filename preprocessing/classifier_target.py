import pandas as pd
import numpy as np

from common.named_functor import NamedFunctor
from state.pipeline_state import PipelineState
from preprocessing.id_parsing import _parse_household_id


def build(meta_col_name: str, one_set: set, household_matched=False):
    if household_matched:
        return NamedFunctor(
            "Target: " + meta_col_name + "(Household)",
            lambda state, mode:
                matched_pair_concat(state, meta_col_name, one_set)
        )
    else:
        return NamedFunctor(
            "Target: " + meta_col_name,
            lambda state, mode:
                _target(state, meta_col_name, one_set)
        )


# concatenate rows corresponding to household.
# Flip a coin to determine whether MS or control comes first within the row.
# Set target = 0 if MS comes first, target = 1 if control comes first.
def matched_pair_concat(state: PipelineState,
                        meta_col_name: str,
                        one_set: set) -> PipelineState:
    state = _target(state, meta_col_name, one_set)
    df = state.df
    df['target'] = state.target
    df = df.rename(index=_parse_household_id)
    df = df.sort_index()
    splitter = np.random.randint(2, size=len(df.index) // 2)
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

    left = left.rename(columns=lambda name: "L"+name)
    right = right.rename(columns=lambda name: "R"+name)

    left = left.sort_index()
    right = right.sort_index()
    df = pd.concat([left, right], axis=1)
    df = df.drop('Ltarget', axis=1)
    target = df['Rtarget']
    df = df.drop('Rtarget', axis=1)
    return state.update(target=target, df=df)


def _target(state: PipelineState, meta_col_name: str, one_set: set) \
        -> PipelineState:
    return state.update_target(state.meta_df.apply(
        lambda row: 1 if row[meta_col_name] in one_set else 0,
        axis=1))
