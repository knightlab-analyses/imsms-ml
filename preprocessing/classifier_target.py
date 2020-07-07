import pandas as pd
import numpy as np

from common.named_functor import NamedFunctor


def build(option, meta_df):
    if option == "household_concat":
        return NamedFunctor("Household (concat)",
                            lambda df: matched_pair_concat(df, meta_df))
    if option == "disease_state":
        return NamedFunctor("Disease State",
                            lambda df: disease_state(df, meta_df))
    if option == "site":
        return NamedFunctor("Site",
                            lambda df: site(df, meta_df))


# concatenate rows corresponding to household.  Households are assumed to be
# consecutive pairs of rows in the dataframe.
# Flip a coin to determine whether MS or control comes first within the row.
# Set target = 0 if MS comes first, target = 1 if control comes first.
def matched_pair_concat(df: pd.DataFrame, meta_df: pd.DataFrame):
    df = disease_state(df, meta_df)
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
    df['target'] = df['Rtarget']
    df = df.drop('Ltarget', axis=1)
    df = df.drop('Rtarget', axis=1)
    return df


def _parse_household_id(sample_id: str):
    # Input of form Q.71401.0009.2016.02.23
    # Output of form 71401-0009
    return sample_id[0:3] + sample_id[5:]


def _target(df: pd.DataFrame, meta_df: pd.DataFrame,
            meta_col_name: str, one_set: set):
    target = meta_df.apply(
        lambda row: 1 if row[meta_col_name] in one_set else 0,
        axis=1)
    df['target'] = target
    return df


# Append a target column to df based on lookup of disease state in meta.
def disease_state(df: pd.DataFrame, meta_df: pd.DataFrame):
    target = meta_df.apply(lambda row: 1 if row["disease"] == "MS" else 0,
                           axis=1)
    df['target'] = target
    return df


# Append a target column to df based on lookup of disease state in meta.
def site(df: pd.DataFrame, meta_df: pd.DataFrame):
    target = meta_df.apply(lambda row: 1 if row["site"] == "San Francisco"
                           else 0,
                           axis=1)
    df['target'] = target
    return df
