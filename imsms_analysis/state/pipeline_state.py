import pandas as pd


class PipelineState:
    def __init__(self,
                 df: pd.DataFrame,
                 meta_df: pd.DataFrame,
                 target: pd.Series):
        self.df = df
        self.meta_df = meta_df
        self.target = target

    def update_df(self, df: pd.DataFrame):
        self.df = df
        return self

    def update_meta_df(self, meta_df: pd.DataFrame):
        self.meta_df = meta_df
        return self

    def update_target(self, target: pd.Series):
        self.target = target
        return self

    def update(self, **kwargs):
        diff = kwargs.keys() - {'df', 'meta_df', 'target'}
        if len(diff) > 0:
            raise KeyError("Unknown Keys:" + str(diff))
        if 'df' in kwargs:
            self.df = kwargs['df']
        if 'meta_df' in kwargs:
            self.meta_df = kwargs['meta_df']
        if 'target' in kwargs:
            self.target = kwargs['target']
        return self

    def __str__(self):
        return "---------------\nDF:\n" + str(self.df) + \
               "\n\nMETA_DF:\n" + str(self.meta_df) + \
               "\n\nTARGET:\n" + str(self.target) + \
               "\n---------------"
