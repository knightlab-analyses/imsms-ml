from matplotlib import colors
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier

from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_config import AnalysisConfig
from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.preprocessing.column_transformation import LDAFunctor
from imsms_analysis.state.pipeline_state import PipelineState
from imsms_analysis.preprocessing.visualization import plot_categorical
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class LDAPlot:
    def __init__(self, rows=-1, enable_plots=True):
        self.rows = rows
        self.cols = -1
        self.plot_index = -1
        self.ldas = None
        self.scratch = None
        self.score1 = None
        self.score2 = None
        self.acc_val_titles = []
        self.acc_val_values = []
        self.enable_plots = enable_plots
        self.scratch = None

    def hook_events(self, runner: SerialRunner):
        def _batch_info(configs: list):
            if self.rows == -1:
                self.rows = len(configs)
            self.cols = 2
            self.plot_index = 1
            self.ldas = []

        def _before_preprocess_step(
                config: AnalysisConfig,
                next_step: NamedFunctor,
                state: PipelineState,
                mode: str):
            if next_step.name != "Run LDA":
                return
            self.df_before = state.df

        def _after_preprocess_step(
            config: AnalysisConfig,
            last_step: NamedFunctor,
            state: PipelineState,
            mode: str):

            if last_step.name != "Run LDA":
                return

            print("CONFIG: ", config.analysis_name, "MODE: ", mode)

            acc2 = (last_step._lda.score(self.df_before, state.target))
            print("LDA Acc:", acc2)

            title = config.analysis_name + "-" + mode
            # Cool 2d plot but only works for 2d data, muck with subplot
            # to make it show up
            # if mode == "train":
            #     self.scratch = None
            # self.scratch = plot_data(last_step._lda,
            #     self.df_before,
            #     state.target,
            #     last_step._lda.predict(self.df_before.to_numpy()),
            #     title,
            #     self.scratch
            # )

            self.plot_index = self.plot_index + 1
            if self.enable_plots:
                plt.subplot(self.rows, self.cols, self.plot_index - 1)
                plot_categorical(state, mode, "", colors=["#FF4C4C", "#4C4CFF"])
                plt.text(0, .5, "Accuracy " + str(int(acc2 * 100)) + "%")
                plt.title(mode)
                plt.suptitle(config.analysis_name)

            self.ldas.append(last_step._lda.coef_)

            if self.plot_index == self.rows * self.cols + 1:
                self.plot_index = 1
                if self.enable_plots:
                    plt.show()

            if self.plot_index % 2 == 1:
                self.acc_val_titles.append(title)
                self.acc_val_values.append(acc2)

        runner.callbacks.batch_info.register(_batch_info)
        runner.callbacks.before_preprocess_step.register(_before_preprocess_step)
        runner.callbacks.after_preprocess_step.register(_after_preprocess_step)

    def print_acc(self):
        df = pd.DataFrame.from_records(
            data=[self.acc_val_values],
            columns=self.acc_val_titles
        )
        df.to_csv("./results/lda_all.csv")

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df.transpose())

    def _make_presentation_plot(self, df, target):
        # Stupid workaround for LDA only producing one component
        X = df.iloc[:, 0]
        label_x = df.columns[0]
        if len(df.columns) >= 2:
            Y = df.iloc[:, 1]
            label_y = df.columns[1]
        else:
            Y = target
            label_y = "Target"

        plt.scatter(X, Y, c=target)
        plt.title("Akkermansia and Faecalibacterium")
        plt.xlabel("CLR(Akkermansia)")
        plt.ylabel("CLR(Faecalibacterium)")



#https://scikit-learn.org/stable/auto_examples/classification/plot_lda_qda.html
# #############################################################################
# Plot functions
# Colormap
cmap = colors.LinearSegmentedColormap(
    'red_blue_classes',
    {'red': [(0, 1, 1), (1, 0.7, 0.7)],
     'green': [(0, 0.7, 0.7), (1, 0.7, 0.7)],
     'blue': [(0, 0.7, 0.7), (1, 1, 1)]})
plt.cm.register_cmap(cmap=cmap)


def plot_data(lda, X, y, y_pred, title, model):
    print("COLUMNS:")
    print(X.columns)
    axis_name_x = X.columns[0]
    axis_name_y = X.columns[1]
    X = X.to_numpy()
    y = y.to_numpy()
    if model is None:
        rfc = RandomForestClassifier(n_estimators=100)
        rfc.fit(X, y)
    else:
        test_acc = model.score(X, y)
        rfc = model
    y_pred = rfc.predict(X)

    tp = (y == y_pred)  # True Positive
    tp0, tp1 = tp[y == 0], tp[y == 1]
    X0, X1 = X[y == 0], X[y == 1]
    X0_tp, X0_fp = X0[tp0], X0[~tp0]
    X1_tp, X1_fp = X1[tp1], X1[~tp1]

    ax = plt.gca()

    plt.subplot(2,1,1)
    # class 0: dots
    plt.scatter(X0_tp[:, 0], X0_tp[:, 1], marker='.', color='red')
    plt.scatter(X0_fp[:, 0], X0_fp[:, 1], marker='x',
                s=20, color='#990000')  # dark red

    # class 1: dots
    plt.scatter(X1_tp[:, 0], X1_tp[:, 1], marker='.', color='blue')
    plt.scatter(X1_fp[:, 0], X1_fp[:, 1], marker='x',
                s=20, color='#000099')  # dark blue

    plt.xlabel("Δ" + axis_name_x)
    plt.ylabel("Δ" + axis_name_y)
    plt.title("Random Forest (100 Trees)")

    # class 0 and 1 : areas
    nx, ny = 200, 200
    x_min, x_max = plt.xlim()
    y_min, y_max = plt.ylim()
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, nx),
                         np.linspace(y_min, y_max, ny))

    Z = rfc.predict_proba(np.c_[xx.ravel(), yy.ravel()])
    # Z = lda.predict_proba(np.c_[xx.ravel(), yy.ravel()])
    Z = Z[:, 1].reshape(xx.shape)
    plt.pcolormesh(xx, yy, Z, cmap='red_blue_classes',
                   norm=colors.Normalize(0., 1.), zorder=0)
    plt.contour(xx, yy, Z, [0.5], linewidths=2., colors='white')

    # means
    # plt.plot(lda.means_[0][0], lda.means_[0][1],
    #          '*', color='yellow', markersize=15, markeredgecolor='grey')
    # plt.plot(lda.means_[1][0], lda.means_[1][1],
    #          '*', color='yellow', markersize=15, markeredgecolor='grey')

    plt.subplot(2,1,2)
    # class 0: dots
    plt.scatter(X0_tp[:, 0], X0_tp[:, 1] - (y_max-y_min) * 1/4, marker='.', color='red')
    plt.scatter(X0_fp[:, 0], X0_fp[:, 1] + (y_max-y_min) * 0, marker='x',
                s=20, color='#990000')  # dark red

    # class 1: dots
    plt.scatter(X1_tp[:, 0], X1_tp[:, 1] + (y_max-y_min) * 1/4, marker='.', color='blue')
    plt.scatter(X1_fp[:, 0], X1_fp[:, 1] + (y_max-y_min) * 2/4, marker='x',
                s=20, color='#000099')  # dark blue

    if model is not None:
        plt.text(0, .5, "Accuracy " + str(int(test_acc * 100)) + "%")

    plt.suptitle(title)
    plt.show()
    return rfc
