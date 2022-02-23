# Examine specific woltka IDs
from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.events.analysis_callbacks import AnalysisCallbacks
from imsms_analysis.events.plot_lda import LDAPlot

from imsms_analysis.analysis import run_preprocessing
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

GENOME_IDS = \
    [
        "G001406335",  # Fusicatenibacter
        "G000020225",  #	349741	Akkermansia	Akkermansia muciniphila
        "G000436395",  #	1263034	Akkermansia	Akkermansia muciniphila CAG:154
        "G000437075",  #	1262691	Akkermansia	Akkermansia sp. CAG:344
        "G000723745",  #	239935	Akkermansia	Akkermansia muciniphila
        "G000980515",  #	1638783	Akkermansia	Akkermansia sp. UNK.MGS-1
        "G001578645",  #	1574264	Akkermansia	Akkermansia sp. KLE1797
        "G001580195",  #	1574265	Akkermansia	Akkermansia sp. KLE1798
        "G001647615",  #	1131336	Akkermansia	Akkermansia sp. KLE1605
        "G001683795",  #	1679444	Akkermansia	Akkermansia glycaniphila
        "G001917295",  #	1896967	Akkermansia	Akkermansia sp. 54_46
        "G001940945",  #	1929996	Akkermansia	Akkermansia sp. Phil8
        "G900097105",  #	1679444	Akkermansia	Akkermansia glycaniphila
    ]


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    return AnalysisFactory(
        BiomTable("none"),
        metadata_filepath
    ) \
        .with_pair_strategy(["unpaired", "paired_subtract_sex_balanced"]) \
        .with_normalization([Normalization.CLR, Normalization.DEFAULT])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    factory = configure() # use setup from a particular analysis.
    configs = list(factory.gen_configurations())

    print(",".join([config.analysis_name for config in configs]))
    chosen_config = [config for config in configs if (config.analysis_name == "unpaired-Divide10000")][0]

    _,_,train_state,test_state = run_preprocessing(chosen_config, AnalysisCallbacks())

    df = train_state.df
    df['target'] = train_state.target
    df['target'] = df['target'].map({0: "Control", 1: "MS"})

    for GENOME_ID in GENOME_IDS:
        g = sns.swarmplot(x=df[GENOME_ID], y='target', orient='h', data=df)
        plt.show()
