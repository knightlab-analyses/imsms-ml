import biom
import pandas as pd
from q2_feature_table import rarefy
from qiime2 import Artifact

from common.named_functor import NamedFunctor
from state.pipeline_state import PipelineState


# TODO:  Some kind of normalization of rows in the dataframe
#  What are our options?:  CHOOSE 1 (2?)
#    Rarefaction such that row adds to X
#    Normalize such that row adds to X
#    Pseudocounts and Isometric Log Transform (sp?)
#      Read GNEISS and Fuller (sp?) papers
#      * AST? - https://huttenhower.sph.harvard.edu/maaslin/
#        Arc-sin transformation
#      * --ILR? - Yoshiki's Fave!--
#      * ALR?
#      * CLR?
#      https://en.wikipedia.org/wiki/Compositional_data#Linear_transformations
#
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
def rarefy_wrapper(state: PipelineState, target_count: int) -> PipelineState:
    table = Artifact.import_data("FeatureTable[Frequency]", state.df) \
        .view(biom.Table)
    table = rarefy(table, target_count)
    df = Artifact.import_data("FeatureTable[Frequency]", table) \
        .view(pd.DataFrame)
    return state.update_df(df)


# Divides each row by the total across that row,
# then multiplies by target_count.  This normalizes the total read count of a
# row to sum to target_count.
def divide_total(state: PipelineState, target_count: int) -> PipelineState:
    df = state.df.div(state.df.sum(axis=1) / target_count, axis=0)
    return state.update_df(df)
