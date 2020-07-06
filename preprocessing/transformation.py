import pandas as pd
from sklearn.decomposition import PCA

from common.named_functor import NamedFunctor


def build_pca(num_components):
    return NamedFunctor(
        "Filter Samples By ID Prefix",
        lambda x: _pca(x, num_components)
    )


# PCA probably isn't a legitimate operation in most spaces we're working in,
# (Like probably all machine learning algorithms :D)
# you might consider doing PCoA instead!
# See https://stackoverflow.com/questions/23282130/principal-components-analysis-using-pandas-dataframe  # noqa
def _pca(df, num_components):
    pca_obj = PCA(num_components)
    new_df = pca_obj.fit_transform(df)
    print(pca_obj.explained_variance_ratio_)

    return pd.DataFrame(
        new_df,
        columns=['PCA%i' % i for i in range(num_components)],
        index=df.index)
