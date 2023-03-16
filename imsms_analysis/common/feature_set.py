import pandas as pd
from itertools import chain, combinations


class FeatureSet:
    def __init__(self, name, features, feature_names=None):
        self.name = name
        self.features = features
        self.feature_names = feature_names

    def create_univariate_sets(self, name_prefix=""):
        ret_val = []
        for i in range(len(self.features)):
            f = self.features[i]
            fn = ""
            if self.feature_names is not None:
                fn = self.feature_names[i]
            ret_val.append(FeatureSet(name_prefix + fn + str(f), [f], [fn]))
        return ret_val

    def create_all_combos(self, name_prefix=""):
        # See
        # https://stackoverflow.com/questions/1482308/how-to-get-all-subsets-of-a-set-powerset
        # or
        # https://docs.python.org/3/library/itertools.html#itertools-recipes

        def powerset(iterable, desired_range):
            """
            powerset([1,2,3], range(len(s) + 1)) -->
            () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
            """
            s = list(iterable)
            return chain.from_iterable(
                combinations(s, r) for r in desired_range)

        return [FeatureSet(name_prefix + str(f), list(f)) for f in
                powerset(self.features, range(1, len(self.features) + 1))]


    @classmethod
    def create_univariate_zebra(cls, zebra_file, zebra_thresh):
        z = pd.read_csv(zebra_file, index_col='genome_id')
        z = z[z['coverage_ratio'] > zebra_thresh]
        fs = FeatureSet("", z.index.tolist(), [""]*len(z.index))
        return fs.create_univariate_sets()

    @classmethod
    def build_feature_set(cls, name, filepath):
        feature_set = pd.read_csv(filepath,
                                  sep='\t',
                                  index_col='ID',
                                  dtype=str)
        # Dumb Panda ignores type
        feature_set.index = feature_set.index.astype(str)
        feature_set_index = feature_set.index.tolist()

        return FeatureSet(name, feature_set_index, feature_set["Name"].tolist())

    @classmethod
    def build_feature_sets(cls, filepath):
        feature_sets = pd.read_csv(filepath,
                                   sep=',',
                                   index_col='ID',
                                   dtype=str)
        feature_sets.index = feature_sets.index.astype(str)

        fs = []
        for column in feature_sets.columns:
            if column in {'ID', 'Name', "Occurence"}:
                continue
            fs.append(
                FeatureSet(
                    column,
                    feature_sets[feature_sets[column] == '1'].index.tolist()
                )
            )
        return fs

    def __str__(self):
        return self.name
