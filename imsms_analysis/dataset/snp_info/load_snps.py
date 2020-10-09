import pandas as pd
from imsms_analysis.preprocessing.id_parsing import _parse_household_id


def parse_disease_state(sample_id: str):
    return sample_id[4] == '1'


df = pd.read_csv("HLA_alleles_iMSMS_samples.txt", sep='\t')
df = df.sort_index()
# print(df)
# print(df.columns.tolist())
df["household"] = df.index.map(_parse_household_id)
df["MS"] = df.index.map(parse_disease_state)
print(df[["household", "MS", "DRB1:15:01"]])
print(df["DRB1:15:01"].sum())
print(df.groupby("MS")["DRB1:15:01"].sum())

# 87 people have the DRB1:15:01 allele
# 33 of those people are control group
# 54 of those people are MS group

# Examine 54 households where MS case has this allele.
# Note: cuts our N by a factor of 10,
# we may not be able to differentiate signal.

households = df[df["MS"] & df["DRB1:15:01"] == 1]["household"]
print(households.values)