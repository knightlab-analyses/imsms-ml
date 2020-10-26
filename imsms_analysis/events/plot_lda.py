from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_config import AnalysisConfig
from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState
from imsms_analysis.preprocessing.visualization import plot_categorical
import matplotlib.pyplot as plt
import numpy as np


class LDAPlot:
    def __init__(self):
        self.rows = -1
        self.cols = -1
        self.plot_index = -1
        self.ldas = None
        self.scratch = None
        self.score1 = None
        self.score2 = None

    def hook_events(self, runner: SerialRunner):
        def _batch_info(configs: list):
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
            plt.subplot(self.rows, self.cols, self.plot_index)
            self.plot_index = self.plot_index + 1
            title = config.analysis_name + "-" + mode
            plot_categorical(state, mode, title)

            acc1 = ((state.df["LDA0"] > 0) == (state.target == 1.0)).sum() / state.target.size
            # print(acc1)
            # plt.text(0, .5, "Accuracy " + str(int(acc1 * 100)) + "%")

            acc2 = (last_step._lda.score(self.df_before, state.target))
            print(acc2)
            plt.text(0, .5, "Accuracy " + str(int(acc2 * 100)) + "%")

            if abs(acc1 - acc2) > .05:
                print("BIG DIFF:")
                print(last_step._lda.coef_)
                print(last_step._lda.scalings_)
                print(last_step._lda.intercept_)

            self.ldas.append(last_step._lda.coef_)

            if self.plot_index == self.rows * self.cols + 1:
                self.plot_index = 1
                print("LDA LIST")
                print(self.ldas)
                plt.show()

        runner.callbacks.batch_info.register(_batch_info)
        runner.callbacks.before_preprocess_step.register(_before_preprocess_step)
        runner.callbacks.after_preprocess_step.register(_after_preprocess_step)


