import json
import biom
from biom import load_table
from qiime2 import Artifact, Metadata
from sklearn.model_selection import ParameterGrid
import q2_mlab
import pandas as pd
import preprocessing_pipeline

# Load sequence DataFrame
from common import plotter
from state.pipeline_state import PipelineState
import pdb


def eval_model(model, state):
    test_df = state.df
    test_meta_df = state.meta_df
    test_target = state.target

    #  Shuffle the data so the machine learning can't learn
    #  anything based on order
    test_df = test_df.sample(frac=1, random_state=110399473805677 % (2**32))

    # Target and df order must match.  Argh.
    test_df['target'] = test_target
    test_target = test_df['target']
    test_df = test_df.drop(['target'], axis=1)

    print("Indexes Match:")
    print((test_df.index == test_target.index).all())

    y = model.predict(test_df)
    real = test_target

    return (y == real).value_counts()[True] / len(real)


def run_analysis(analysis_config):
    analysis_name = analysis_config.analysis_name
    biom_filepath = analysis_config.biom_filepath
    metadata_filepath = analysis_config.metadata_filepath
    feature_set_index = analysis_config.feature_set_index
    if feature_set_index is not None:
        feature_set_index = feature_set_index.features
    training_set_index = analysis_config.training_set_index
    if training_set_index is None:
        training_set_index = 0
    pair_strategy = analysis_config.pair_strategy
    if pair_strategy is None:
        pair_strategy = "paired_concat"
    metadata_filter = analysis_config.metadata_filter
    n_random_seeds = analysis_config.n_random_seeds
    if n_random_seeds is None:
        n_random_seeds = 50

    biom_table = load_table(biom_filepath)
    table = Artifact.import_data("FeatureTable[Frequency]", biom_table)
    df = table.view(pd.DataFrame)
    print(df)

    # # Look up ids for genera
    # genera = biom_table.metadata_to_dataframe(axis="observation")
    # genera = genera[genera["Name"].isin([
    #     "Akkermansia",
    #     "Bifidobacterium",
    #     "Bilophila",
    #     "Blautia",
    #     "Butyricimonas",
    #     "Coprococcus",
    #     "Christensenella",
    #     "Desulfovibrio",
    #     "Faecalibacterium",
    #     "Haemophilus",
    #     "Methanobrevibacter",
    #     "Mycoplana",
    #     "Paraprevotella",
    #     "Pedobacter",
    #     "Pseudomonas",
    #     "Slackia",
    #     # "Streptococcus thermophiles",
    #     # "Streptococcus salivarius",
    #     # "Faecalibacterium prausnitzi",
    #     # "Coprococcus comes",
    #     # "Anaerostipes hadrus",
    #     # "Eubacterium rectale",
    #     # "Acinetobacter calcoaceticus",
    #     # "Akkermansia muciniphila",
    #     # "Eggerthella lenta"
    # ])]

    # pd.set_option('display.max_rows', None)
    # print(genera.sort_values("Name"))

    # Load metadata DataFrame
    metadata = Metadata.load(metadata_filepath)
    meta_df = metadata.to_dataframe()

    state = PipelineState(df, meta_df, None)
    # Run Preprocessing
    train_state, test_state = preprocessing_pipeline.process(
        state,
        restricted_feature_set=feature_set_index,
        training_set_index=training_set_index,
        verbose=False,
        pair_strategy=pair_strategy,
        metadata_filter=metadata_filter
    )

    df = train_state.df
    meta_df = train_state.meta_df
    target = train_state.target

    # Shuffle the data so the machine learning can't learn anything based on
    # order
    df = df.sample(frac=1, random_state=110399473805677 % (2**32))

    # Target and df order must match.  Argh.
    df['target'] = target
    target = df['target']
    df = df.drop(['target'], axis=1)


    # plotter.simple_swarm(df, meta_df, "239935", "disease")

    # Convert necessary types for regression-benchmarking
    final_biom = Artifact.import_data("FeatureTable[Frequency]", df)\
        .view(biom.Table)

    # LinearSVR_grids = {'C': [1e-4, 1e-3, 1e-2, 1e-1, 1e1,
    #                             1e2, 1e3, 1e4, 1e5, 1e6, 1e7],
    #                     'epsilon':[1e-2, 1e-1, 0, 1],
    #                     'loss': ['squared_epsilon_insensitive',
    #                             'epsilon_insensitive'],
    #                     'random_state': [2018]
    # }

    RandomForestClassifier_grids = {
        # Define a grid here from sklearn api
        'random_state': list(range(2020, 2020 + n_random_seeds))
        # 'random_state': [7]
    }

    # LinearSVC_grids = {'penalty': {'l2'},
    #                    'tol': [1e-4, 1e-2, 1e-1],
    #                    'loss': ['hinge', 'squared_hinge'],
    #                    'random_state': [2018]
    #                    }

    test_acc_results = []
    mean_cross_val_results = []

    param_grid = list(ParameterGrid(RandomForestClassifier_grids))
    for param_set in param_grid:
        reg_params = json.dumps(param_set)
        results_table, best_model, best_accuracy = q2_mlab._unit_benchmark(
            table=final_biom,
            metadata=target,
            algorithm="RandomForestClassifier",
            params=reg_params,
            distance_matrix=None
        )

        print(results_table)
        print(results_table.columns)
        for col in ["ACCURACY", "AUPRC", "AUROC", "F1"]:
            print("Max", col, ":", max(results_table[col]))

        print(best_accuracy)
        print(best_model)

        #######################################
        # BEGIN TEST
        #######################################

        test_accuracy = eval_model(best_model, test_state)
        mean_cross_validation_accuracy = results_table["ACCURACY"].mean()

        print("Test Set Accuracy")
        print(test_accuracy)
        print("Average Cross Validation Accuracy:")
        print(mean_cross_validation_accuracy)

        test_acc_results.append(test_accuracy)
        mean_cross_val_results.append(mean_cross_validation_accuracy)

    results = pd.DataFrame(test_acc_results, columns=["TestAccuracy"])
    results.to_csv("./results/" + analysis_name + ".csv")

    return pd.Series(test_acc_results, name=analysis_name), \
        pd.Series(mean_cross_val_results, name=analysis_name)