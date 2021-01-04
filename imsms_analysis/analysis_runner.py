import pandas as pd

from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.analysis import run_analysis, run_preprocessing
import traceback
from q2_mlab import orchestrate_hyperparameter_search
from imsms_analysis.events.analysis_callbacks import AnalysisCallbacks
from os import path, getcwd, makedirs
from qiime2 import Artifact, Metadata


def _check_unique_names(factory):
    # Check that output files will be uniquely named
    names = set()
    for config in factory.gen_configurations():
        if config.analysis_name in names:
            raise Exception(
                "Duplicate analysis name: "
                + config.analysis_name
                + ".  Analysis factory may require code update "
                "to handle new parameter type"
            )
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


# TODO
# Try passing the job array id in the config
# https://waterprogramming.wordpress.com/2013/01/24/pbs-job-submission-with-python/
# ^ for submitting jobs with python
class ParallelRunner:
    def __init__(self):
        self.callbacks = AnalysisCallbacks()

    def run(self, factory):
        factory.validate()
        _check_unique_names(factory)

        configs = []
        for config in factory.gen_configurations():
            configs.append(config)

        # Run test
        configs = [x for x in factory.gen_configurations()]

        self.callbacks.batch_info(configs)
        for config in configs:
            try:
                print(config.analysis_name)
                
                # Run this custom preprocessing
                (
                final_biom,
                train_state,
                test_state
                ) = run_preprocessing(config, self.callbacks)

                base_dir = "dataset"
                dataset = "imsms-mlab"
                preparation = config.analysis_name
                target_name = "disease_binary"
                algorithm = config.mlab_algorithm
                if algorithm is None:
                    algorithm = "RandomForestClassifier"

                # Create the  expected file structure
                results_dir = path.join(
                    base_dir, dataset, preparation, target_name
                )
                if not path.exists(results_dir):
                    makedirs(results_dir)
                
                # Save table and metadata
                table_fp = path.join(
                    base_dir, dataset, preparation, target_name,
                    "filtered_table.qza"
                )
                table_artifact = Artifact.import_data(
                    "FeatureTable[Frequency]", 
                    final_biom
                )
                print("current working directory: ", getcwd())
                table_artifact.save(table_fp)

                metadata_fp = path.join(
                    base_dir, dataset, preparation, target_name,
                    "filtered_metadata.qza"
                )
                metadata_artifact = Artifact.import_data(
                    "SampleData[Target]", train_state.target
                )
                metadata_artifact.save(metadata_fp)

                (
                    script_fp,
                    params_fp,
                    run_info_fp,
                ) = orchestrate_hyperparameter_search(
                    dataset=dataset,
                    preparation=preparation,
                    target=target_name,
                    algorithm=algorithm,
                    repeats=3,  # num CV repeats
                    base_dir=base_dir,  # Directory with mlab structure containing datasets
                    ppn=4,  # processors per node
                    memory=32,  # memory in GB
                    wall=50,  # walltime  in hours
                    chunk_size=100,  # num parameter sets to run per job
                    randomize=True,  # randomly shuffle order of parameter set
                    force=False,  # force overwrite of existing results
                    dry=True,  # dry runs
                    dataset_path=table_fp,
                    metadata_path=metadata_fp,
                )

            except Exception:
                print(f"TEST FAILURE. CONFIG: " + config.analysis_name)
                traceback.print_exc()

