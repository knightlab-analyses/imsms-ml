import pandas as pd
from common.named_functor import NamedFunctor


def build(method):
    if method == 'sum':
        return NamedFunctor("Sum Replicates", aggregate_sum)
    if method == 'mean':
        return NamedFunctor("Average Replicates", aggregate_mean)
    if method == 'pick':
        return NamedFunctor("Pick High Count Replicate", aggregate_pick_high_count)


# Aggregates samples with the same index, sums over all columns
# This is probably the closest we can get to concatenating fastq files of
# technical replicates without actually concatenating those files
def aggregate_sum(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(lambda x: x).sum()


# Aggregates samples with the same index, computes mean over all columns
# There is substantial worry that this is not compositionally coherent
# (IE: If there is any bias between sample replicates, using mean will break)
# (Given that it's sum divided by n, suspect either both are or neither are)
def aggregate_mean(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(lambda x: x).mean()


# Groups samples with the same index, computes the number of reads in each
# sample, picks the sample with the highest read count in each group.
def aggregate_pick_high_count(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(lambda x: x)
    print(grouped)
    return grouped
