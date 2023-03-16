from imsms_analysis.preprocessing.id_parsing import _parse_household_id
import numpy as np
import collections

from imsms_analysis.state.pipeline_state import PipelineState
import pandas as pd

TrainTest = collections.namedtuple('TrainTest', 'train test')

# TODO: This is not actually a preprocessor,
#  maybe should be in a different folder?


def passthrough(state):
    tt = TrainTest(
        train=PipelineState(state.df, state.meta_df, state.target),
        test=PipelineState(
            pd.DataFrame(columns=state.df.columns),
            pd.DataFrame(columns=state.meta_df.columns),
            None)
    )
    return tt


def pick_training_households(household_series,
                             fraction_train=.5,
                             verbose=False):
    all_households = household_series.unique()
    train_households = np.random.choice(
        all_households,
        int(len(all_households) * fraction_train),
        replace=False
    )
    return train_households


# Splits the pipeline into training and test sets by household,
# households are assumed to be consecutive pairs of rows by index in the
# dataframe.
def split(state, fraction_train=.5, verbose=False) -> TrainTest:
    household = state.df.index.map(_parse_household_id)
    train_households = pick_training_households(household,
                                                fraction_train,
                                                verbose)
    return split_fixed_set(state, train_households, verbose=False)


def split_fixed_set(state, train_households, verbose=False):
    state.df['household'] = state.df.index.map(_parse_household_id)
    train_df = state.df.loc[state.df['household'].isin(train_households)]
    test_df = state.df.loc[~state.df['household'].isin(train_households)]

    train_index = train_df.index
    test_index = test_df.index

    train_meta = state.meta_df[state.meta_df.index.isin(train_index)]
    test_meta = state.meta_df[state.meta_df.index.isin(test_index)]

    if state.target is not None:
        train_target = state.target[state.target.index.isin(train_index)]
        test_target = state.target[state.target.index.isin(test_index)]
    else:
        train_target = None
        test_target = None

    state.df = state.df.drop('household', axis=1)
    train_df = train_df.drop('household', axis=1)
    test_df = test_df.drop('household', axis=1)

    # print(train_df)
    # print(test_df)

    return TrainTest(
        train=PipelineState(train_df, train_meta, train_target),
        test=PipelineState(test_df, test_meta, test_target)
    )


def split_by_meta(state, metacol, meta_train_vals):
    idx = state.meta_df[metacol].isin(meta_train_vals)
    train_meta = state.meta_df[idx]
    test_meta = state.meta_df[~idx]

    train_index = train_meta.index
    test_index = test_meta.index

    train_df = state.df[state.df.index.isin(train_index)]
    test_df = state.df[state.df.index.isin(test_index)]

    if state.target is not None:
        train_target = state.target[state.target.index.isin(train_index)]
        test_target = state.target[state.target.index.isin(test_index)]
    else:
        train_target = None
        test_target = None

    return TrainTest(
        train=PipelineState(train_df, train_meta, train_target),
        test=PipelineState(test_df, test_meta, test_target)
    )
