import matplotlib.pyplot as plt
import pandas as pd
from imsms_analysis.common.named_functor import NamedFunctor
import seaborn as sns


def plot_correlation_matrix():
    return NamedFunctor("Plot Correlation Heatmap",
                        lambda state, mode: _plot_correlation_matrix_deluxe(state))


def plot_scatter():
    return NamedFunctor("Plot Scatter",
                        _plot_scatter)


def plot_category():
    return NamedFunctor("Plot Category",
                        _plot_categorical)


# See https://stackoverflow.com/questions/29432629/plot-correlation-matrix-using-pandas
# answer by Dick Fox
def _plot_correlation_matrix_deluxe(state):
    df = state.df
    print("Building Correlation Matrix")
    cor = df.corr()
    print("Showing Correlation Matrix")
    f = plt.figure(figsize=(19, 15))
    plt.matshow(cor, fignum=f.number)
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

PLOT_HACK = 1
def _plot_categorical(state, mode):
    df = state.df
    target = state.target
    global PLOT_HACK

    df["target"] = target.astype("category")

    plt.subplot(6, 2, PLOT_HACK)
    ax = sns.violinplot(data=df,
                        x=df.columns[0],
                        y="target",
                        hue="target")
    ax.set_title(str(mode))

    titles = [
        "",
        "Unpaired Divide10000 Train",
        "Unpaired Divide10000 Test",
        "Unpaired CLR Train",
        "Unpaired CLR Test",
        "PairedConcat Divide10000 Train",
        "PairedConcat Divide10000 Test",
        "PairedConcat CLR Train",
        "PairedConcat CLR Test",
        "PairedSubtract Divide10000 Train",
        "PairedSubtract Divide10000 Test",
        "PairedSubtract CLR Train",
        "PairedSubtract CLR Test"
    ]

    plt.title(titles[PLOT_HACK])
    PLOT_HACK = PLOT_HACK + 1
    if PLOT_HACK == 13:
        PLOT_HACK = 1
        plt.show()

    return state