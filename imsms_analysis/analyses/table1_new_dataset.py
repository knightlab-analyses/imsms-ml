from imsms_analysis.common.table_info import BiomTable, CSVTable
import os
import pandas as pd
import numpy as np

from imsms_analysis.preprocessing.id_parsing import _parse_sample_id


def main():
    df = BiomTable("none", biom_filepath=[
        "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
        "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
        "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
    ]).load_dataframe()

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

    print(df.shape)
    df = df[~bad_rows]
    print(df.shape)

    df = df.rename(mapper=_parse_sample_id)
    df = df[~df.index.duplicated(keep='first')]
    print(df.shape)

    print("HELLO WORLD")
    meta_df = CSVTable("./dataset/metadata/qiita_metadata_filtered.tsv", sep="\t", index_col="sample_name").load_dataframe()
    print(meta_df.index)
    print(meta_df.shape)

    print("GOODBYE WORLD")
    meta_df_extended = CSVTable("./dataset/metadata/iMSMS_phenotypes_for_Knight_Lab_20221104.tsv", sep="\t", index_col="filtered_sample_name").load_dataframe()
    print(meta_df_extended.index)
    print(meta_df_extended.shape)

    print("OH NO")

    df = pd.DataFrame(index=df.index)
    df = df.join(meta_df)
    df = df.join(meta_df_extended)
    print(df.shape)

    print(df.columns)
    print(df["disease"].value_counts())
    print("Argh, at least 5 MS have no reported control")
    df = df[(df["disease"] == "MS") | (df["disease"] == "Control")]
    print(df.shape)

    print(df["sex"].value_counts())
    print(df.groupby("disease")["sex"].value_counts())

    print("HHC", "MS")
    print("Number")
    print(df["disease"].value_counts())
    print("Sex")
    print(df.groupby("disease")["sex"].value_counts())
    print("Age")
    df["host_age"] = pd.to_numeric(df["host_age"])
    print(df.groupby("disease")["host_age"].mean())
    print(np.percentile(df.groupby("disease")["host_age"].get_group("Control"), (25,75)))
    print(np.percentile(df.groupby("disease")["host_age"].get_group("MS"), (25,75)))

    print("BMI")
    df["host_body_mass_index"] = pd.to_numeric(df["host_body_mass_index"])
    print(df.groupby("disease")["host_body_mass_index"].mean())
    print(np.percentile(df.groupby("disease")["host_body_mass_index"].get_group("Control"), (25,75)))
    print(np.percentile(df.groupby("disease")["host_body_mass_index"].get_group("MS"), (25,75)))

    print("Disease Course")
    print(df["Disease_Course"].value_counts())

    def group_disease_course(s):
        if s in ["PPMS", "SPMS", "PRMS"]:
            return "PMS"
        elif s in ["RRMS", "CIS"]:
            return "RRMS"
    df["disease_course_grouped"] = df["Disease_Course"].apply(group_disease_course)
    print("Disease Course Grouped")
    print(df["disease_course_grouped"].value_counts())

    print("MSSS")
    df["MSSS"] = pd.to_numeric(df["MSSS"])
    print(df.groupby("disease")["MSSS"].mean())
    print(np.nanpercentile(df.groupby("disease")["MSSS"].get_group("MS"), (25,75)))

    print(df.groupby("disease_course_grouped")["MSSS"].mean())
    print(np.nanpercentile(df.groupby("disease_course_grouped")["MSSS"].get_group("RRMS"), (25,75)))
    print(np.nanpercentile(df.groupby("disease_course_grouped")["MSSS"].get_group("PMS"), (25,75)))
    print("???")

    print("Treatment Status")
    print(df["Treatment_Status"])
    print(df["Treatment_Status"].value_counts())
    print(df.groupby("disease")["Treatment_Type"].value_counts())
    print(df.groupby("disease_course_grouped")["Treatment_Status"].value_counts())
    print(df.groupby("disease_course_grouped")["Treatment_Type"].value_counts())

    print("Location location location")
    print(df.groupby("disease")["geo_loc_name"].value_counts())


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    os.chdir("..")
    print(106/300)
    print(205/305)

    print(86+65+61+36+27+16+9)
    print(90+64+62+38+27+16+8)

    main()

