import pandas as pd
from sklearn.decomposition import PCA

from common.named_functor import NamedFunctor
from state.pipeline_state import PipelineState


def build_pca(num_components):
    return PCAFunctor(num_components)


def build_column_filter(chosen_columns):
    return NamedFunctor(
        "Restrict to columns (compositional): " + str(chosen_columns),
        lambda state, mode: _restrict_columns_compositional(state,
                                                            chosen_columns)
    )


# PCA probably isn't a legitimate operation in most spaces we're working in,
# (Like probably all machine learning algorithms :D)
# you might consider doing PCoA instead!
# See https://stackoverflow.com/questions/23282130/principal-components-analysis-using-pandas-dataframe  # noqa

# Note also PCA is an operation that requires keeping learned features from the
# training set when applying to the test set and must therefore take the mode
# into account.
class PCAFunctor:
    def __init__(self, num_components):
        self.name = "Run PCA"
        self.num_components = num_components
        self._pca = PCA(num_components)

    def __call__(self, state: PipelineState, mode: str):
        new_df = None
        if mode == 'train':
            new_df = self._pca.fit_transform(state.df)
        elif mode == 'test':
            new_df = self._pca.transform(state.df)

        return state.update_df(pd.DataFrame(
            new_df,
            columns=['PCA%i' % i for i in range(self.num_components)],
            index=state.df.index)
        )

    def __str__(self):
        return "Functor(" + self.name + ")"

    def __repr__(self):
        return "Functor(" + self.name + ")"


# Restricts the set of columns in df to chosen columns, then adds a new column
# "remainder" containing the sum of dropped values, thus maintaining row sums.
def _restrict_columns_compositional(state: PipelineState,
                                    chosen_columns: list) \
        -> PipelineState:
    df = state.df
    remainder = df.drop(chosen_columns, axis=1)
    df['remainder'] = remainder.sum(axis=1)
    restricted = df[chosen_columns + ['remainder']]

    return state.update_df(restricted)
