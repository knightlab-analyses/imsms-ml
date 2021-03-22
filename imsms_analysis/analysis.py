import json
import biom
from biom import load_table
from qiime2 import Artifact, Metadata
from sklearn.model_selection import ParameterGrid
import q2_mlab
import pandas as pd
from imsms_analysis import preprocessing_pipeline

# Load sequence DataFrame
from imsms_analysis.common.analysis_config import AnalysisConfig
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common import plotter
from imsms_analysis.events.analysis_callbacks import AnalysisCallbacks
from imsms_analysis.state.pipeline_state import PipelineState
import pdb


def _print_read_count_info(df):
    import csv
    print("--------------------------------------")
    """ Open up a mimic file and print read counts from the raw dataframe """
    with open("dataset/feature_transforms/mog_mimics40.csv") as f:
        rr = csv.reader(f)
        headers = next(rr, None)
        gid = headers.index("genome_id")
        print("\t".join([str(x) for x in headers + ["Read Count"]]))

        for row in rr:
            key = row[gid]
            count = 0

            if key in df.columns:
                count = df[key].sum()
                print("\t".join([str(x) for x in row + [count]]))
    print("--------------------------------------")
    exit(0)



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


def run_preprocessing(analysis_config, callbacks: AnalysisCallbacks):
    callbacks.start_analysis(analysis_config)
    
    analysis_name = analysis_config.analysis_name
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
    dim_reduction = analysis_config.dimensionality_reduction
    normalization = analysis_config.normalization
    if normalization is None:
        normalization = Normalization.DEFAULT
    feature_transform = analysis_config.feature_transform
    # TODO: Probably need to keep the config for the algorithm next to the algo
    #  blahhh.

    df = analysis_config.table_info.load_dataframe()
    _print_read_count_info(df)

    # print("RAGE")
    # print(biom_filepath)
    # print(df.columns)
    # print(df['88431'])
    # print(df['411462'])
    # print("END RAGE")

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
        analysis_config,
        state,
        callbacks,
        restricted_feature_set=feature_set_index,
        training_set_index=training_set_index,
        verbose=False,
        pair_strategy=pair_strategy,
        metadata_filter=metadata_filter,
        dim_reduction=dim_reduction,
        normalization=normalization,
        feature_transform=feature_transform,
        meta_encoder=analysis_config.meta_encoder,
        downsample_count=analysis_config.downsample_count
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

    # print(df.columns)
    # plotter.simple_swarm(df, meta_df, "239935", "disease")
    # return

    # Convert necessary types for regression-benchmarking
    final_biom = Artifact.import_data("FeatureTable[Frequency]", df)\
        .view(biom.Table)
    
    return final_biom, target, train_state, test_state


def run_analysis(analysis_config, callbacks: AnalysisCallbacks):
    (
        final_biom,
        target,
        train_state,
        test_state
    ) = run_preprocessing(analysis_config, callbacks)

    _print_read_count_info(train_state.df)

    analysis_name = analysis_config.analysis_name
    n_random_seeds = analysis_config.n_random_seeds
    if n_random_seeds is None:
        n_random_seeds = 50
    algorithm = analysis_config.mlab_algorithm
    if algorithm is None:
        algorithm = "RandomForestClassifier"

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

    # Optimal parameters determined from grid search, rated by cross validation
    # performance.
    # Note: Many more estimators and no bootstrapping, this makes it take
    # substantially longer to run.
    # RandomForestClassifier_grids = {
    #     'bootstrap': [False],
    #     'criterion': ['gini'],
    #     'max_depth': [3],
    #     'max_features': ['log2'],
    #     'max_samples': [0.75],
    #     'min_samples_split': [2],
    #     'min_samples_leaf': [0.21],
    #     'n_estimators': [5000],
    #     'random_state': list(range(2020, 2020 + n_random_seeds))
    # }

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
            algorithm=algorithm,
            params=reg_params,
            distance_matrix=None
        )

        print(results_table)
        print(results_table.columns)
        for col in ["ACCURACY", "AUPRC", "AUROC", "F1"]:
            print("Max", col, ":", max(results_table[col]))

        print(best_accuracy)
        print("MY MODEL:")
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