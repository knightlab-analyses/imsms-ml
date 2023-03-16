from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
import pandas as pd
from imsms_analysis.preprocessing.id_parsing import _parse_sample_id, _parse_disease_state, _parse_household_id


def fix_metadata(output_path):
    def parse_sex(s):
        if s == 'female':
            return 'F'
        elif s == 'male':
            return 'M'
        elif s == 'not provided':
            return "not provided"
        else:
            print("CRAPOLA", s)
            raise ValueError("Unparseable Sex:", s)
    df = CSVTable("./dataset/metadata/11326_20220902-144432.txt", sep="\t").load_dataframe()
    df.index = df['sample_name']
    df = df.drop(["sample_name"], axis=1)
    print(df)
    bad_prefixes = [
        "11326.BLANK",
        "11326.NA",
        "11326.UCSF",
        "11326.COLUMN",
        "11326.Column",
        "11326.Q.DOD",
        "11326.Zymo.",
        "11326.Mag.Bead.Zymo",
        "11326.D.Twin",
        "11326.F.twin",
        "11326.Q.FMT"
    ]

    bad_rows = df.index.str.startswith(bad_prefixes[0])
    for i in range(1, len(bad_prefixes)):
        bad_rows |= df.index.str.startswith(bad_prefixes[i])

    df = df[~bad_rows]
    print(df)
    df = df.rename(mapper=_parse_sample_id)
    df["disease"] = df.index.map(_parse_disease_state)
    df["household"] = df.index.map(_parse_household_id)
    df["household"] = df["household"].apply(lambda x: "".join(x.split("-")))
    df["sex"] = df["sex"].apply(parse_sex)
    print(df)
    df = df[~df.index.duplicated(keep='first')]
    df.to_csv(output_path, sep="\t")


def configure():
    # Regenerate the metadata file
    # fix_metadata("./dataset/metadata/qiita_metadata_filtered.tsv")

    # df_fail = BiomTable("none", biom_filepath=[
    #     "./dataset/biom/qiita_bioms/imsms-none-Jul28-2022.biom",
    #     "./dataset/biom/qiita_bioms/imsms-none-Aug1-2022.biom",
    #     "./dataset/biom/qiita_bioms/imsms-none-Aug3-2022.biom"
    # ]).load_dataframe()
    # print(df_fail)
    # dfsum = df_fail.sum(axis=1)
    # print(df_fail.sum(axis=1))
    # print(df_fail.sum(axis=1).mean())
    # print(df_fail.sum(axis=1).median())
    # 1218 x 1848 (These are the failed samples)

    # manifest = CSVTable("/Users/djhakim/imsms_manifest.txt", sep='\t').load_dataframe()
    # manifest_list = manifest['sample name'].tolist()
    # manifest_list = ["11326." + x for x in manifest_list]
    # print(manifest_list)

    # Check the biom table(s)
    # df = BiomTable("none", biom_filepath=[
    #     "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
    #     "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
    #     "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
    # ]).load_dataframe()

    # # 1424 x 6455 (Higher number of species than we've seen before)

    # setA = set(manifest_list)
    # setB = set(df_list)
    #
    # for a in setA:
    #     if a not in setB:
    #         print("Manifest Only:", a)
    # for b in setB:
    #     if b not in setA:
    #         print("DF Only:", b)


    # dfsum = df.sum(axis=1)
    # print(df.sum(axis=1))
    # print(df.sum(axis=1).mean())
    # print(df.sum(axis=1).median())
    # import pandas as pd
    #
    # short_df = pd.DataFrame(df.index, df.index)
    # print(short_df)
    # short_df.to_csv("~/imsms_list.tsv", sep="\t")
    # exit(-1)
    #
    # print("Is DF OKAY?")
    # with pd.option_context('display.max_rows', None):  # more options can be specified also
    #     print(df)
    # print("Yeah its okay")

    old_metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"

    old_fact = AnalysisFactory(
        BiomTable("none"),
        old_metadata_filepath,
        "Per Genome Counts (old)"
    ) \
        .with_pair_strategy("paired_subtract_sex_balanced") \
        .with_normalization(Normalization.DEFAULT)

    new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"

    randsets = []
    for i in range(10):
        new_fact = AnalysisFactory(
            BiomTable("none", biom_filepath=[
                "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
                "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
                "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
            ]),
            new_metadata_filepath,
            "Per Genome Counts (new) (split-" + str(i) + ")"
        ) \
            .with_pair_strategy("paired_subtract_sex_balanced") \
            .with_normalization(Normalization.DEFAULT) \
            .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"]))
        randsets.append(new_fact)

    # return new_fact
    # return MultiFactory([old_fact, new_fact])
    return MultiFactory(randsets)


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    SerialRunner().run(configure())

