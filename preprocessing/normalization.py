import biom
import pandas as pd
from q2_feature_table import rarefy
from qiime2 import Artifact

from common.named_functor import NamedFunctor


def build(method_name, target_count):
    if method_name == 'rarefy':
        return NamedFunctor("Rarefy", lambda df: rarefy_wrapper(df,
                                                                target_count))
    if method_name == 'divide_total':
        return NamedFunctor("Average Replicates",
                            lambda df: divide_total(df, target_count))
    if method_name == 'ILR':
        raise NotImplemented()
    if method_name == 'CLR':
        raise NotImplemented()
    if method_name == 'ALR':
        raise NotImplemented()


# Uses the qiime2 rarefy functionality to rarefy each row's counts.
def rarefy_wrapper(df: pd.DataFrame, target_count: int) -> pd.DataFrame:
    table = Artifact.import_data("FeatureTable[Frequency]", df) \
        .view(biom.Table)
    table = rarefy(table, target_count)
    df = Artifact.import_data("FeatureTable[Frequency]", table) \
        .view(pd.DataFrame)
    return df


# Divides each row by the total across that row,
# then multiplies by target_count.  This normalizes the total read count of a
# row to sum to target_count.
def divide_total(df: pd.DataFrame, target_count: int) -> pd.DataFrame:
    df = df.div(df.sum(axis=1) / target_count, axis=0)
    return df
