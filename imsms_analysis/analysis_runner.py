import pandas as pd

from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.analysis import run_analysis
import traceback

from imsms_analysis.events.analysis_callbacks import AnalysisCallbacks


def _check_unique_names(factory):
    # Check that output files will be uniquely named
    names = set()
    for config in factory.gen_configurations():
        if config.analysis_name in names:
            raise Exception("Duplicate analysis name: " +
                            config.analysis_name +
                            ".  Analysis factory may require code update "
                            "to handle new parameter type")
        names.add(config.analysis_name)


class DryRunner:
    @staticmethod
    def run(factory):
        factory.validate()
        _check_unique_names(factory)

        configs = []
        for config in factory.gen_configurations():
            configs.append(config)

        print("Total Configs: " + str(len(configs)))
        print("Config Names: ")
        for c in configs:
            print(c.analysis_name)


class SerialRunner:

    def __init__(self):
        self.callbacks = AnalysisCallbacks()

    def run(self, factory):
        # Validation stops us from failing after running tests for 100 hours :D

        # Validate files will be found
        factory.validate()
        _check_unique_names(factory)

        # Run test
        test_accuracies = []
        configs = [x for x in factory.gen_configurations()]

        self.callbacks.batch_info(configs)
        for config in configs:
            try:
                test_acc, mean_cross_acc = run_analysis(config, self.callbacks)
                test_accuracies.append(test_acc)
            except Exception as e:
                print("TEST FAILURE.  CONFIG: " + config.analysis_name)
                traceback.print_exc()

        # TODO:  Would probably be smart to save results as we go in case of
        #  catastrophic failure.
        print(test_accuracies)
        results_df = pd.concat(test_accuracies, axis=1)
        results_df.to_csv("./results/all.csv")

        summary_df = pd.concat([results_df.mean(), results_df.std()], axis=1)
        summary_df.columns = ["Mean Test Acc", "Std Dev Test Acc"]
        summary_df.to_csv("./results/summary.csv")
        print(summary_df)


# class ParallelRunner:
#     # TODO: Something something queue some jobs
#     pass
