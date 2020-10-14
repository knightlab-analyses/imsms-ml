import pandas as pd
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    FeatureTransformer
from imsms_analysis.state.pipeline_state import PipelineState

import numpy as np
import umap


def build_pca(num_components):
    return PCAFunctor(num_components)


def build_lda(num_components):
    return LDAFunctor(num_components)


def build_umap():
    return UMAPFunctor()


def build_feature_set_transform(transformer):
    def wrapped(state, mode):
        return _apply_feature_transform(state, transformer)

    return NamedFunctor(
        transformer.name,
        wrapped
    )


def sum_columns():
    return NamedFunctor(
        "Sum All Columns",
        lambda state, mode: _sum_columns(state)
    )


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


class LDAFunctor:
    def __init__(self, num_components):
        self.name = "Run LDA"
        self.num_components = num_components
        print("NUM COMPONENTS:", num_components)
        self._lda = LinearDiscriminantAnalysis(n_components=num_components)

    def __call__(self, state: PipelineState, mode: str):
        new_df = None
        if mode == 'train':
            new_df = self._lda.fit_transform(state.df, state.target)
        elif mode == 'test':
            new_df = self._lda.transform(state.df)

        return state.update_df(pd.DataFrame(
            new_df,
            columns=['LDA%i' % i for i in range(self.num_components)],
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

    print(chosen_columns)
    print("Grr")
    print(state.df.columns)

    df = state.df
    remainder = df.drop(chosen_columns, axis=1)

    print(remainder)
    print("VS")
    print(len(chosen_columns))

    df['remainder'] = remainder.sum(axis=1)
    restricted = df[chosen_columns + ['remainder']]

    return state.update_df(restricted)


class UMAPFunctor:
    def __init__(self):
        self.name = "Run UMAP"
        self.reducer = umap.UMAP(random_state=72519857125 % 2 ** 32)

    def __call__(self, state: PipelineState, mode: str):
        new_df = None
        if mode == 'train':
            new_df = self.reducer.fit_transform(state.df)
        elif mode == 'test':
            new_df = self.reducer.transform(state.df)

        # # Plot That Umap!
        # print("MODE:", mode)
        # from matplotlib import pyplot as plt
        # plt.scatter(new_df[:, 0], new_df[:, 1])
        # plt.title("UMAP")
        # plt.xlabel("UMAP0")
        # plt.ylabel("UMAP1")
        # plt.show()
        # plt.close()

        return state.update_df(pd.DataFrame(
            new_df,
            columns=["UMAP1", "UMAP2"],
            index=state.df.index)
        )

    def __str__(self):
        return "Functor(" + self.name + ")"

    def __repr__(self):
        return "Functor(" + self.name + ")"


def _apply_feature_transform(state: PipelineState,
                             transformer: FeatureTransformer):
    return state.update_df(transformer.transform_df(state.df))


def _sum_columns(state: PipelineState):
    series = state.df.sum(axis=1)
    series.name = "score"
    return state.update_df(series.to_frame())
