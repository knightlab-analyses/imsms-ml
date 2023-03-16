# Examine models trained at different levels of taxonomic assignment

from imsms_analysis.analysis_runner import SerialRunner, DryRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
from imsms_analysis.events.plot_lda import LDAPlot
from imsms_analysis.preprocessing import sample_filtering, id_parsing
from imsms_analysis.preprocessing_pipeline import BAD_SAMPLE_PREFIXES
from imsms_analysis.state.pipeline_state import PipelineState
import pandas as pd

def fix_input_table(df):
    df = df.set_index("sample")
    df["remainder"] = df["total_reads"] - df["target_reads"]
    df = df.drop("total_reads", axis=1)
    df.index.name = None
    df.columns.name = None

    ps = PipelineState(df, pd.DataFrame(), None)
    ps = sample_filtering.build_prefix_filter(BAD_SAMPLE_PREFIXES)(ps, "filter")
    ps = id_parsing.build()(ps, "filter")
    return ps.df


def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    csv_filepath = "../akkermansia_stuff/counts_CBIA010000065.1_5057-6325.csv"

    pathways = AnalysisFactory(
        [
            CSVTable(
                csv_filepath,
                table_name="CDD94772.1-GeneCount",
                on_load_transform=fix_input_table,
                sep="\t")
        ],
        metadata_filepath
    ) \
        .with_lda([1]) \
        .with_normalization(Normalization.NONE) \
        .with_pair_strategy("paired_subtract_sex_balanced")

    return MultiFactory([pathways])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    runner = SerialRunner()
    lda_plot = LDAPlot(rows=1, enable_plots=False)
    lda_plot.hook_events(runner)
    runner.run(configure())
    lda_plot.print_acc()