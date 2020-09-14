from os import path
from typing import Union

from imsms_analysis.common.analysis_config import AnalysisConfig
from imsms_analysis.common.dimensionality_reduction import DimensionalityReduction
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization


class AnalysisFactory:
    def __init__(self,
                 biom_type: Union[list, str],
                 metadata_filepath: str,
                 analysis_name: str = None):
        self.biom_type = biom_type
        if type(biom_type) is str:
            self.biom_type = [biom_type]
        self.metadata_filepath = metadata_filepath
        self.analysis_name = analysis_name

        self.feature_set = None
        self.training_set = None
        self.pair_strategy = None
        self.metadata_filter = None
        self.n_random_seeds = None
        self.dimensionality_reduction = None
        self.normalization = None
        self.mlab_algorithm = None

    def with_feature_set(self, feature_set):
        if type(feature_set) == FeatureSet:
            feature_set = [feature_set]
        self.feature_set = feature_set
        return self

    def with_num_training_sets(self, n):
        self.training_set = range(n)
        return self

    def with_num_seeds(self, n):
        self.n_random_seeds = [n]
        return self

    def with_pair_strategy(self, pair_strategy):
        if type(pair_strategy) is str:
            pair_strategy = [pair_strategy]
        self.pair_strategy = pair_strategy
        return self

    def with_metadata_filter(self, metadata_filter):
        if type(metadata_filter) == MetadataFilter:
            metadata_filter = [metadata_filter]
        self.metadata_filter = metadata_filter
        return self

    def with_pca(self, num_components):
        if self.dimensionality_reduction is not None:
            raise Exception("Can't set multiple dimensionality reductions")
        if type(num_components) == int:
            num_components = [num_components]
        self.dimensionality_reduction = \
            [DimensionalityReduction("PCA" + str(x), "pca", num_components=x)
             for x in num_components]
        return self

    def with_umap(self):
        if self.dimensionality_reduction is not None:
            raise Exception("Can't set multiple dimensionality reductions")
        self.dimensionality_reduction = \
            [DimensionalityReduction("UMAP", "umap")]
        return self

    def with_normalization(self, normalization_method):
        if type(normalization_method) == Normalization:
            normalization_method = [normalization_method]
        self.normalization = normalization_method
        return self

    def with_algorithm(self, algorithm):
        if type(algorithm) == str:
            algorithm = [algorithm]
        self.mlab_algorithm = algorithm
        return self

    @staticmethod
    def _build_biom_file_path(biom_type: str) -> str:
        return "./dataset/biom/combined-" + biom_type + ".biom"

    def _analysis_name_gen(self,
                           all_params,
                           chosen_tuple):
        parameters = []
        if self.analysis_name is not None:
            parameters.append(self.analysis_name)

        for i in range(len(all_params)):
            if len(all_params[i]) > 1:
                parameters.append(str(chosen_tuple[i]))
        return "-".join(parameters)

    def validate(self):
        # Check that metadata file exists
        if not path.exists(self.metadata_filepath):
            raise FileNotFoundError("No Metadata File:" + self.metadata_filepath)

        # Check that biom files exist
        for biom_type in self.biom_type:
            biom_path = self._build_biom_file_path(biom_type)
            if not path.exists(biom_path):
                raise FileNotFoundError("No Biom Table: " + biom_path)

    def gen_configurations(self):
        all_params = [self.biom_type,
                      self.feature_set,
                      self.training_set,
                      self.pair_strategy,
                      self.metadata_filter,
                      self.n_random_seeds,
                      self.dimensionality_reduction,
                      self.normalization,
                      self.mlab_algorithm]

        for i in range(len(all_params)):
            if all_params[i] is None:
                all_params[i] = [None]

        def _iterate(all_params, index, chosen):
            if index == len(all_params) - 1:
                for val in all_params[index]:
                    yield chosen + [val]
            else:
                for val in all_params[index]:
                    for result in _iterate(all_params, index + 1, chosen + [val]):
                        yield result

        for chosen in _iterate(all_params, 0, []):
            bt, fs, ts, ps, mf, num_seeds, dr, norm, algo = chosen
            yield AnalysisConfig(
                self._analysis_name_gen(all_params, chosen),
                self._build_biom_file_path(bt),
                self.metadata_filepath,
                fs,
                ts,
                ps,
                mf,
                num_seeds,
                dr,
                norm,
                algo
            )


class MultiFactory:
    def __init__(self, factories):
        self.factories = factories

    def validate(self):
        for fact in self.factories:
            fact.validate()

    def gen_configurations(self):
        for fact in self.factories:
            for config in fact.gen_configurations():
                yield config
