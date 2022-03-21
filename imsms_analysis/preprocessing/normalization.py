import biom
import pandas as pd
from q2_feature_table import rarefy
from qiime2 import Artifact
from skbio.stats.composition import clr

from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState


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
def build(method_name, target_count=10000):
    if method_name == 'none':
        return NamedFunctor("No Normalization "
                            "(WARN: IGNORES COMPOSITIONALITY)",
                            lambda state, mode: state)

    if method_name == 'rarefy':
        return NamedFunctor("Rarefy",
                            lambda state, mode: rarefy_wrapper(state,
                                                               target_count))
    if method_name == 'divide_total':
        return NamedFunctor("Truncate Ray To Simplex",
                            lambda state, mode: divide_total(state,
                                                             target_count))
    if method_name == 'ILR':
        # Existing functions for this in skbio
        raise NotImplemented()
    if method_name == 'CLR':
        return NamedFunctor("CLR Transform", lambda state, mode: clr_wrapper(state))
    if method_name == 'ALR':
        # Existing functions for this in skbio
        raise NotImplemented()
    if method_name == 'AST':
        raise NotImplemented()


# Uses the qiime2 rarefy functionality to rarefy each row's counts.
def rarefy_wrapper(state: PipelineState, target_count: int) -> PipelineState:
    if state.df.shape[0] == 0:
        return state

    table = Artifact.import_data("FeatureTable[Frequency]", state.df) \
        .view(biom.Table)
    table = rarefy(table, target_count)
    df = Artifact.import_data("FeatureTable[Frequency]", table) \
        .view(pd.DataFrame)
    return state.update_df(df)


def clr_wrapper(state: PipelineState):
    # Unfortunately, clr needs pseudocounts or it crashes out.
    clr_data = clr(state.df.to_numpy() + .5)
    new_df = pd.DataFrame(data=clr_data, index=state.df.index, columns=state.df.columns)
    return state.update_df(new_df)


#ADD Robust CLR from qiime2 here

# Divides each row by the total across that row,
# then multiplies by target_count.  This normalizes the total read count of a
# row to sum to target_count.
def divide_total(state: PipelineState, target_count: int) -> PipelineState:
    df = state.df.div(state.df.sum(axis=1) / target_count, axis=0)
    return state.update_df(df)
