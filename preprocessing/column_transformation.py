import pandas as pd
from sklearn.decomposition import PCA

from common.named_functor import NamedFunctor
from state.pipeline_state import PipelineState


def build_pca(num_components):
    return NamedFunctor(
        "Filter Samples By ID Prefix",
        lambda x: _pca(x, num_components)
    )


def build_column_filter(chosen_columns):
    return NamedFunctor(
        "Restrict to columns (compositional): " + str(chosen_columns),
        lambda x: _restrict_columns_compositional(x, chosen_columns)
    )


# PCA probably isn't a legitimate operation in most spaces we're working in,
# (Like probably all machine learning algorithms :D)
# you might consider doing PCoA instead!
# See https://stackoverflow.com/questions/23282130/principal-components-analysis-using-pandas-dataframe  # noqa
def _pca(state: PipelineState, num_components) -> PipelineState:
    pca_obj = PCA(num_components)
    new_df = pca_obj.fit_transform(state.df)

    return state.update_df(pd.DataFrame(
        new_df,
        columns=['PCA%i' % i for i in range(num_components)],
        index=state.df.index))


# Restricts the set of columns in df to chosen columns, then adds a new column
# "remainder" containing the sum of dropped values, thus maintaining row sums.
def _restrict_columns_compositional(state: PipelineState, chosen_columns) \
        -> PipelineState:
    df = state.df
    restricted = df[chosen_columns]
    remainder = df.drop(chosen_columns)
    restricted['remainder'] = remainder.sum(axis=1)

    return state.update_df(restricted)
