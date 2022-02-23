from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_config import AnalysisConfig
from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState

import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("TkAgg")


class RawScatterPlot:
    def __init__(self, plot_configs):
        self.plot_configs = plot_configs
        pass

    def hook_events(self, runner: SerialRunner):
        def _after_preprocess_step(
                config: AnalysisConfig,
                last_step: NamedFunctor,
                state: PipelineState,
                mode: str):
            if last_step.name == "Filter Empty Samples":
                self.plot_scatters(config, state, mode)
            pass
        runner.callbacks.after_preprocess_step.register(_after_preprocess_step)

    def plot_scatters(self, config, state, mode):
        df = state.df
        print("Number of samples:", df.shape[0])
        print("Number of genome IDs:", df.shape[1])
        for plot_config in self.plot_configs:
            title = plot_config[2]
            if title is None:
                title = config.analysis_name + "-" + mode
            ax = df.plot.scatter(plot_config[0], plot_config[1], title=title)
            # ax.axis('equal')
            if plot_config[3] is not None:
                ax.set_xlabel(plot_config[3])
            if plot_config[4] is not None:
                ax.set_ylabel(plot_config[4])

            summed = df.sum()
            print(plot_config[0], summed[plot_config[0]])
            print(plot_config[1], summed[plot_config[1]])
        plt.show()