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
from common.MetadataFilter import MetadataFilter
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


def _build_restricted_feature_set(filepath=None):
    if filepath is None:
        return None

    feature_set = pd.read_csv(filepath,
                              sep='\t',
                              index_col='ID',
                              dtype=str)
    # Dumb Panda ignores type
    feature_set.index = feature_set.index.astype(str)
    feature_set_index = feature_set.index.tolist()

    return feature_set_index


def _build_restricted_feature_sets_individual(filepath=None):
    feature_set_index = _build_restricted_feature_set(filepath)
    if feature_set_index is None:
        return None
    return [[x] for x in feature_set_index]


def run_analysis(analysis_name,
                 biom_filepath,
                 metadata_filepath,
                 feature_set_index=None,
                 training_set_index=0,
                 paired=True,
                 metadata_filter=None):
    biom_table = load_table(biom_filepath)
    table = Artifact.import_data("FeatureTable[Frequency]", biom_table)
    df = table.view(pd.DataFrame)

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
        paired=paired,
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
        'random_state': list(range(2020, 2020+50))
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


if __name__ == "__main__":
    test_accuracies = []

    # Recapitulate Probstel 2018 list of important genera
    # all_important_genera = _build_restricted_feature_set(
    #     "./dataset/feature_sets/literature_review_Probstel_Baranzini_2018.tsv"
    # )
    # important_genera = _build_restricted_feature_sets_individual(
    #     "./dataset/feature_sets/literature_review_Probstel_Baranzini_2018.tsv"
    # )
    # test_acc, mean_cross_acc = run_analysis(
    #     "Probstel-Important-Genera",
    #     biom_filepath="./dataset/biom/combined-genus.biom",
    #     metadata_filepath=
    #     "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #     feature_set_index=all_important_genera
    # )
    # test_accuracies.append(test_acc)

    # test_acc, mean_cross_acc = run_analysis(
    #     "All-Genera",
    #     biom_filepath="./dataset/biom/combined-genus.biom",
    #     metadata_filepath=
    #     "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #     feature_set_index=None
    # )
    # test_accuracies.append(test_acc)

    # for genus in important_genera:
    #     test_acc, mean_cross_acc = run_analysis(
    #         "Genus-" + genus[0],
    #         biom_filepath="./dataset/biom/combined-genus.biom",
    #         metadata_filepath=
    #         "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #         feature_set_index=genus
    #     )
    #     test_accuracies.append(test_acc)

    # akkermansia_feature_set_index = _build_restricted_feature_set("./dataset/feature_sets/just_akkermansia.tsv")
    # test_acc, mean_cross_acc = run_analysis(
    #     "Akkermansia muciniphila-" + str(i),
    #     biom_filepath="./dataset/biom/combined-species.biom",
    #     metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #     feature_set_index=akkermansia_feature_set_index
    # )
    # test_accuracies.append(test_acc)

    # for i in range(10):
    #     test_acc, mean_cross_acc = run_analysis(
    #         "RawSpeciesPaired-RandomizedTestSet-" + str(i),
    #         biom_filepath="./dataset/biom/combined-species.biom",
    #         metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #         feature_set_index=None,
    #         paired=True
    #     )
    #     test_accuracies.append(test_acc)
    #
    # for i in range(10):
    #     test_acc, mean_cross_acc = run_analysis(
    #         "RawSpeciesUnpaired-RandomizedTestSet-" + str(i),
    #         biom_filepath="./dataset/biom/combined-species.biom",
    #         metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #         restricted_feature_set_filepath=None,
    #         paired=False
    #     )
    #     test_accuracies.append(test_acc)

    # for i in range(1):
    #     for biom_file in [
    #                       # "phylum", "class", "order",
    #                       # "family",
    #                       "genus",
    #                       "species",
    #                       # "enzrxn2reaction",
    #                       # "pathway2class",
    #                       # "protein",
    #                       # "reaction2pathway"
    #         ]:
    #         test_acc, mean_cross_acc = run_analysis(
    #             "Raw-" + biom_file + str(i),
    #             biom_filepath="./dataset/biom/combined-"+biom_file+".biom",
    #             metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #             feature_set_index=None,
    #             training_set_index=i
    #         )
    #         test_accuracies.append(test_acc)

    # for m_filter in [
    #     None,
    #     MetadataFilter("disease_course", ["RRMS", "Control"]),
    #     MetadataFilter("disease_course", ["PPMS", "Control"]),
    #     MetadataFilter("disease_course", ["SPMS", "Control"])
    # ]:
    #     name = "Species"
    #     if m_filter is not None:
    #         name = name + m_filter.acceptable_values[0]
    #     test_acc, mean_cross_acc = run_analysis(
    #         name,
    #         biom_filepath="./dataset/biom/combined-species.biom",
    #         metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #         feature_set_index=None,
    #         training_set_index=0,
    #         metadata_filter=m_filter
    #     )
    #     test_accuracies.append(test_acc)

    # for m_filter in [
    #     None,
    #     MetadataFilter("site", ["San Sebastian", "Control"]),
    #     MetadataFilter("site", ["San Francisco", "Control"]),
    #     MetadataFilter("site", ["Pittsburgh", "Control"]),
    #     MetadataFilter("site", ["New York", "Control"]),
    #     MetadataFilter("site", ["Edinburgh", "Control"]),
    #     MetadataFilter("site", ["Buenos Aires", "Control"]),
    #     MetadataFilter("site", ["Boston", "Control"])
    # ]:
    #     name = "Species"
    #     if m_filter is not None:
    #         name = name + m_filter.acceptable_values[0]
    #     test_acc, mean_cross_acc = run_analysis(
    #         name,
    #         biom_filepath="./dataset/biom/combined-species.biom",
    #         metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #         feature_set_index=None,
    #         training_set_index=0,
    #         metadata_filter=m_filter
    #     )
    #     test_accuracies.append(test_acc)

    # test_acc, mean_cross_acc = run_analysis(
    #     "AST",
    #     biom_filepath="./dataset/biom/combined-species.biom",
    #     metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #     restricted_feature_set_filepath=
    #     "./dataset/feature_sets/MS_associated_species_AST.tsv"
    # )
    # test_accuracies.append(test_acc)
    #
    # test_acc, mean_cross_acc = run_analysis(
    #     "CLR",
    #     biom_filepath="./dataset/biom/combined-species.biom",
    #     metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #     restricted_feature_set_filepath=
    #     "./dataset/feature_sets/MS_associated_species_CLR.tsv"
    # )
    # test_accuracies.append(test_acc)
    #
    # test_acc, mean_cross_acc = run_analysis(
    #     "TMM",
    #     biom_filepath="./dataset/biom/combined-species.biom",
    #     metadata_filepath="./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    #     restricted_feature_set_filepath=
    #     "./dataset/feature_sets/MS_associated_species_TMM.tsv"
    # )
    # test_accuracies.append(test_acc)

    print(test_accuracies)
    results_df = pd.concat(test_accuracies, axis=1)
    results_df.to_csv("./results/all.csv")

    summary_df = pd.concat([results_df.mean(), results_df.std()], axis=1)
    summary_df.columns = ["Mean Test Acc", "Std Dev Test Acc"]
    summary_df.to_csv("./results/summary.csv")

    print(summary_df)
