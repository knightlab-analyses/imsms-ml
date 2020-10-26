import matplotlib.pyplot as plt
import pandas as pd
from imsms_analysis.common.named_functor import NamedFunctor
import seaborn as sns
import numpy as np


def plot_correlation_matrix():
    return NamedFunctor("Plot Correlation Heatmap",
                        lambda state, mode: _plot_correlation_matrix_deluxe(state))


def plot_scatter():
    return NamedFunctor("Plot Scatter",
                        _plot_scatter)


# def plot_category():
#     return NamedFunctor("Plot Category",
#                         _plot_categorical)


# See https://stackoverflow.com/questions/29432629/plot-correlation-matrix-using-pandas
# answer by Dick Fox
def _plot_correlation_matrix_deluxe(state):
    df = state.df
    print("Building Correlation Matrix")
    cor = df.corr(method="pearson")
    print("Showing Correlation Matrix")
    f = plt.figure(figsize=(19, 15))
    plt.matshow(cor, fignum=f.number)
    for (i, j), z in np.ndenumerate(cor):
        plt.text(j, i, '{:0.1f}'.format(z), ha='center', va='center')
    plt.xticks(range(df.shape[1]), df.columns, fontsize=14, rotation=45)
    plt.yticks(range(df.shape[1]), df.columns, fontsize=14)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=14)
    plt.title('Correlation Matrix', fontsize=16);

    print("Done")
    plt.show()
    plt.close()

    return state


def _plot_scatter(state, mode):
    # Stupid workaround for LDA only producing one component
    X = state.df.iloc[:,0]
    label_x = state.df.columns[0]
    if len(state.df.columns) >= 2:
        Y = state.df.iloc[:,1]
        label_y = state.df.columns[1]
    else:
        Y = state.target
        label_y = "Target"

    plt.scatter(X,Y, c=state.target)
    plt.title("Dim Reduction (" + str(mode) + ")")
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.show()
    plt.close()

    return state


def plot_categorical(state, mode, title):
    df = state.df
    target = state.target

    df["target"] = target.astype("category")

    ax = sns.violinplot(data=df,
                        x=df.columns[0],
                        y="target",
                        hue="target")
    ax.set_title(str(mode))
    # This would be a classifier that divides at 0, but I think LDA actually
    # divides at intercept_ (and along the coef_ axis, rather than the
    # scalings_ axis used for transformation)
    # plt.axvline(color="grey", linestyle="--")

    plt.title(title)
    return state