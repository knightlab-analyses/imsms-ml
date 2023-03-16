from imsms_analysis.analyses.old_and_new_lme import get_species
from imsms_analysis.analysis_runner import SerialRunner, DryRunner, TableRunner
from imsms_analysis.common.PairwisePearson import pairwise_pearson
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
from imsms_analysis.common.train_test import SplitByMetadata, \
    PairedSplit, Passthrough
from imsms_analysis.common.woltka_metadata import filter_and_sort_df
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    ChainedTransform, RelativeAbundanceFilter, PairwisePearsonTransform
import pandas as pd
from collections import defaultdict

new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"
combined_metadata_filepath = "./dataset/metadata/combined_iMSMS_metadata.tsv"


def get_species(woltka_meta_df, gotu):
    return woltka_meta_df[woltka_meta_df["#genome"] == gotu]["species"].iloc[0]


def configure():
    new_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            # "./dataset/biom/combined-none.biom", # Uncomment for both datasets in one csv
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        combined_metadata_filepath,
        "none"
    ).with_pair_strategy(["unpaired"]) \
        .with_normalization(Normalization.NONE) \
        .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
        .with_train_test(
        [
            Passthrough()
        ]
    )

    return new_fact


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    results = TableRunner().run(configure())
    woltka_meta_df = CSVTable("dataset/metadata/woltka_metadata.tsv", delimiter="\t").load_dataframe()

    print(woltka_meta_df[["phylum", "class", "order", "family", "genus", "species"]])
    dfs = {}
    for config, train, test in results:
        dfs[config.analysis_name] = train.df

        extended_metadata_filepath = "./dataset/metadata/iMSMS_phenotypes_for_Knight_Lab_20221104.tsv"
        ex_meta = pd.read_csv(extended_metadata_filepath, sep="\t", index_col="filtered_sample_name")

        for idx in train.df.index:
            if idx not in ex_meta.index:
                print("Can't find sample:", idx)
        foo = ex_meta[["Collection_Site"]].join(train.df[["G000005825"]])
        foo = foo[foo["G000005825"].isna()]
        print(foo)
        for i in sorted(foo.index):
            print(i)
        break

        new_tables = {}
        for collapse_level in ["phylum", "class", "order", "family", "genus", "species"]:
            groupings = defaultdict(list)
            for genome_id in train.df.columns:
                level_value = woltka_meta_df[woltka_meta_df["#genome"] == genome_id][collapse_level].iloc[0]
                groupings[level_value].append(genome_id)

            new_cols = {}
            for level_value in groupings:
                new_cols[level_value] = train.df[groupings[level_value]].sum(axis=1)

            new_tables[collapse_level] = pd.DataFrame(new_cols)
            print(collapse_level)
            print(new_tables[collapse_level])

            new_tables[collapse_level].index.name = "sampleid"
            # new_tables[collapse_level].to_csv("./dataset/csv/" + collapse_level + ".tsv", sep="\t", quotechar='|')

            # print(pd.read_csv("./dataset/csv/" + collapse_level + ".tsv", sep="\t", quotechar="|"))
