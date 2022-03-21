import pandas as pd

from imsms_analysis.common.named_functor import NamedFunctor


def build_zebra(cov_thresh, cov_file):
    if cov_file.endswith(".csv"):
        sep = ','
    elif cov_file.endswith(".tsv"):
        sep = "\t"

    zebra_df = pd.read_csv(cov_file, sep=sep)  # Finrisk coverage file is a tsv
    zebra_pass_df = zebra_df[zebra_df.coverage_ratio > cov_thresh]
    zebra_pass_list = zebra_pass_df['gotu'].to_list() # Finrisk coverage file calls them gotu instead of genome_id

    def wrapped(state, mode):
        state.df = state.df[state.df.columns.intersection(zebra_pass_list)]
        return state.update_df(state.df)

    return NamedFunctor("Zebra Filter:" + str(cov_thresh), wrapped)
