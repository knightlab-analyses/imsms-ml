import pandas as pd


class FeatureSet:
    def __init__(self, name, features):
        self.name = name
        self.features = features

    def create_univariate_sets(self, name_prefix=""):
        return [FeatureSet(name_prefix + str(f), [f]) for f in self.features]

    @classmethod
    def build_feature_set(cls, name, filepath):
        feature_set = pd.read_csv(filepath,
                                  sep='\t',
                                  index_col='ID',
                                  dtype=str)
        # Dumb Panda ignores type
        feature_set.index = feature_set.index.astype(str)
        feature_set_index = feature_set.index.tolist()

        return FeatureSet(name, feature_set_index)

    def __str__(self):
        return self.name
