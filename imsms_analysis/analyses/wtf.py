import os

from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
import pandas as pd
import biom
from matplotlib import pyplot as plt

from imsms_analysis.events.plot_lda import LDAPlot

os.chdir("..")

akkermansia_feature_set = FeatureSet.build_feature_set(
    "Akkermansia (all)",
    "./dataset/feature_sets/just_akkermansia_wol.tsv"
)


# df1 = BiomTable("none").load_dataframe()
# df2 = BiomTable("none", "./dataset/biom/filtered_akkermansia.biom").load_dataframe()
df3 = BiomTable("none", "./dataset/biom/fixed_akkermansia.biom").load_dataframe()


for x in ["SV0", "SV1", "SV2", "SV3"]:
    for y in ["SV0", "SV1", "SV2", "SV3"]:
        df3.plot.scatter(x, y)

# dfx = df1.drop(df2.columns, axis=1)
# dfx = dfx.join(df3)
#
# f_table = biom.table.Table(dfx.to_numpy().T, dfx.columns, dfx.index)
# with biom.util.biom_open('./dataset/biom/fixed_akkermansia_merged.biom', 'w') as f:
#     f_table.to_hdf5(f, "fixed table")


# df3 = BiomTable("species").load_dataframe()["1262691"]



# print((df2 - df3).sum())

# SerialRunner().run(
#     AnalysisFactory(
#         BiomTable("none",),
#         "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
#         "df1"
#     ) \
#         .with_feature_set(FeatureSet("df2", ["G000437075"])) \
#         .with_pair_strategy("paired_subtract_sex_balanced") \
#         .with_normalization(Normalization.DEFAULT)
# )

fact = AnalysisFactory(
    BiomTable("none", "./dataset/biom/fixed_akkermansia_merged.biom"),
    "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    "df2"
) \
.with_feature_set([
    FeatureSet("sv0", ["SV0"]),
    FeatureSet("sv1", ["SV1"]),
    FeatureSet("sv2", ["SV2"]),
    FeatureSet("sv3", ["SV3"]),
    FeatureSet("svAll", ["SV0", "SV1", "SV2", "SV3"])
]) \
.with_pair_strategy("paired_subtract_sex_balanced") \
.with_normalization(Normalization.CLR) \
.with_lda(1)

runner = SerialRunner()
lda_plot = LDAPlot(rows=1, enable_plots=True)
lda_plot.hook_events(runner)
runner.run(fact)

fact2 = AnalysisFactory(
    BiomTable("none", "./dataset/biom/filtered_akkermansia_merged.biom"),
    "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
    "df2"
) \
    .with_feature_set(akkermansia_feature_set.create_univariate_sets()) \
    .with_pair_strategy("paired_subtract_sex_balanced") \
    .with_normalization([Normalization.CLR]) \
    .with_lda(1)

runner.run(fact2)
lda_plot.print_acc()

# SerialRunner().run(
#     AnalysisFactory(
#         BiomTable("species"),
#         "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
#         "df3"
#     ) \
#     .with_feature_set(FeatureSet("df3", ["1262691"])) \
#     .with_pair_strategy("paired_subtract_sex_balanced") \
#     .with_normalization(Normalization.DEFAULT)
# )