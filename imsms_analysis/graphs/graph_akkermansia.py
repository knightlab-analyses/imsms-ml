# Examine Akkermansia, the most often reported feature
from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.events.analysis_callbacks import AnalysisCallbacks
from imsms_analysis.events.plot_lda import LDAPlot

from imsms_analysis.analyses.akkermansia_lda import configure
from imsms_analysis.analyses.akkermansia_target_gene import configure as config_target_gene
from imsms_analysis.analysis import run_preprocessing
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    factory = configure() # use setup from a particular analysis.
    configs = factory.gen_configurations()
    for c in factory.gen_configurations():
        print(c.analysis_name)
    div10000_config = next(
        config for config in configs
        # if config.analysis_name ==  "Akkermansia sp. KLE16051131336-unpaired-None-Divide10000" )
        if config.analysis_name ==  "Akkermansia sp. Phil81929996-unpaired-None-Divide10000" )
        # if config.analysis_name ==  "Akkermansia sp. CAG:3441262691-unpaired-None-Divide10000" )
    gene_config = next(config_target_gene().gen_configurations())

    _,_,train_state,test_state = run_preprocessing(div10000_config, AnalysisCallbacks())
    _,_,train_state2,test_state2 = run_preprocessing(gene_config, AnalysisCallbacks())

    df = train_state.df.drop("remainder", axis=1).join(train_state2.df.drop("remainder", axis=1))
    df['target'] = train_state.target
    df['target'] = df['target'].map({0: "Control", 1: "MS"})
    df['treatment'] = train_state.meta_df['treatment_type']

    # df = train_state.df
    # df['target'] = train_state.target
    # df['target'] = df['target'].map({0: "Control", 1: "MS"})

    g = sns.swarmplot(x=df.columns[0], y='target', orient='h', data=df)
    plt.title(div10000_config.analysis_name)
    plt.show()
    g = sns.swarmplot(x=df.columns[0], y='treatment', orient='h', data=df)
    plt.title(div10000_config.analysis_name)
    plt.show()
    g = sns.swarmplot(x=df.columns[1], y='target', orient='h', data=df)
    plt.title("TEST-SET Akk Cag 344 CDD94772.1 (Reads/10000)")
    plt.show()
    g = sns.scatterplot(x=df.columns[0], y=df.columns[1], hue=df.columns[2], data=df)
    plt.xlabel("Akkermansia muciniphila (239935) Reads/10000")
    plt.ylabel("CDD94772.1 Reads/10000")
    plt.title("Akkermansia vs CDD94772.1")
    plt.show()

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)

    for target in ['MS', 'Control']:
        print(target, "CDD94772.1 > 0:")
        set1 = df[(df['target'] == target) & (df['target_reads'] > 0)]
        print("count", len(set1))
        print("mean", set1['target_reads'].mean())
        print("median", set1['target_reads'].median())
        print(target, "CDD94772.1 == 0:")
        set2 = df[(df['target'] == target) & (df['target_reads'] == 0)]
        print("count", len(set2))
        print("mean", set2['target_reads'].mean())
        print("median", set2['target_reads'].median())




    exit(-1)
    for config in configs:
        try:
            _, _, train_state, test_state = run_preprocessing(config, AnalysisCallbacks())
            train_state.df['target'] = train_state.target

            if "unpaired" in config.analysis_name:
                train_state.df['target'] = train_state.df['target'].map({0:  "Control", 1: "MS"})
            else:
                train_state.df['target'] = train_state.df['target'].map({0: "Control-MS", 1: "MS-Control"})

            g = sns.swarmplot(x=train_state.df.columns[0], y="target", orient='h', data=train_state.df)
            plt.title(config.analysis_name)
            plt.show()

            # more options can be specified also
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                print(train_state.df)
        except Exception as e:
            print(config.analysis_name)
            print(e)


