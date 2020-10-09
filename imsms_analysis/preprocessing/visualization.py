import matplotlib.pyplot as plt
import pandas as pd

from imsms_analysis.common.named_functor import NamedFunctor


def plot_correlation_matrix():
    return NamedFunctor("Plot Correlation Heatmap",
                        lambda state, mode: _plot_correlation_matrix_deluxe(state.df))


# See https://stackoverflow.com/questions/29432629/plot-correlation-matrix-using-pandas
# answer by Dick Fox
def _plot_correlation_matrix_deluxe(df):
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