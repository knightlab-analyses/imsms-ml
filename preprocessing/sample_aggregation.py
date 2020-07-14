import pandas as pd
from common.named_functor import NamedFunctor
from state.pipeline_state import PipelineState


def build(method_name):
    if method_name == 'sum':
        return NamedFunctor("Sum Replicates",
                            lambda state, mode: aggregate_sum(state))
    if method_name == 'mean':
        return NamedFunctor("Average Replicates",
                            lambda state, mode: aggregate_mean(state))
    if method_name == 'pick':
        return NamedFunctor("Pick High Count Replicate",
                            lambda state, mode:
                                aggregate_pick_high_count(state))


# Aggregates samples with the same index, sums over all columns
# This is probably the closest we can get to concatenating fastq files of
# technical replicates without actually concatenating those files
def aggregate_sum(state: PipelineState) -> PipelineState:
    return state.update_df(state.df.groupby(lambda x: x).sum())


# Aggregates samples with the same index, computes mean over all columns
# There is substantial worry that this is not compositionally coherent
# (IE: If there is any bias between sample replicates, using mean will break)
# (Given that it's sum divided by n, suspect either both are or neither are)
def aggregate_mean(state: PipelineState) -> PipelineState:
    return state.update_df(state.df.groupby(lambda x: x).mean())


# Groups samples with the same index, computes the number of reads in each
# sample, picks the sample with the highest read count in each group.
def aggregate_pick_high_count(state: PipelineState) -> PipelineState:
    state.df['read_count'] = state.df.sum(axis=1)
    state.df = state.df.sort_values('read_count', ascending=False)\
               .groupby(lambda x: x)\
               .first()
    state.df = state.df.drop(columns=['read_count'])
    return state
