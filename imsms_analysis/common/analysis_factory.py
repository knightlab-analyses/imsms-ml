from os import path
from typing import Union

from imsms_analysis.common.analysis_config import AnalysisConfig
from imsms_analysis.common.dimensionality_reduction import DimensionalityReduction
from imsms_analysis.common.feature_filter import FeatureFilter
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.meta_encoder import MetaEncoder
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import TableInfo, BiomTable
from imsms_analysis.common.target_set import TargetSet
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    FeatureTransformer


class AnalysisFactory:
    def __init__(self,
                 table_info: Union[list, TableInfo],
                 metadata_filepath: str,
                 analysis_name: str = None):
        self.table_info = table_info
        if isinstance(table_info, TableInfo):
            self.table_info = [table_info]
        self.metadata_filepath = metadata_filepath
        self.analysis_name = analysis_name

        self.feature_set = None
        self.training_set = None
        self.pair_strategy = None
        self.metadata_filter = None
        self.feature_filter = None
        self.n_random_seeds = None
        self.dimensionality_reduction = None
        self.normalization = None
        self.mlab_algorithm = None
        self.feature_transform = None
        self.allele_info = None
        self.meta_encoder = None
        self.downsample_count = None

    def with_feature_set(self, feature_set):
        if type(feature_set) == FeatureSet:
            feature_set = [feature_set]
        self.feature_set = feature_set
        return self

    def with_num_training_sets(self, n):
        self.training_set = range(n)
        return self

    def with_training_set(self, i):
        self.training_set = [i]
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

    def with_feature_filter(self, feature_filter):
        if isinstance(feature_filter, FeatureFilter):
            feature_filter = [feature_filter]
        self.feature_filter = feature_filter
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

    def with_lda(self, num_components):
        if self.dimensionality_reduction is not None:
            raise Exception("Can't set multiple dimensionality reductions")
        if type(num_components) == int:
            num_components = [num_components]
        self.dimensionality_reduction = \
            [DimensionalityReduction("LDA" + str(x), "lda", num_components=x)
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

    def with_feature_transform(self, feature_transform):
        if type(feature_transform) == FeatureTransformer:
            feature_transform = [feature_transform]
        self.feature_transform = feature_transform
        return self

    def with_allele_info(self, allele_info):
        if type(allele_info) == str:
            allele_info = [allele_info]
        self.allele_info = allele_info
        return self

    def with_meta_encoders(self, meta_encoder):
        if type(meta_encoder) == MetaEncoder:
            meta_encoder = [meta_encoder]
        self.meta_encoder = meta_encoder
        return self

    def with_downsampling(self, downsample_count):
        if type(downsample_count) == int:
            downsample_count = [downsample_count]
        self.downsample_count = downsample_count
        return self

    def with_target_set(self, target_set):
        if type(target_set) == TargetSet:
            target_set = [target_set]
        self.target_set = target_set
        return self

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

    def gen_configurations(self):
        all_params = [self.table_info,
                      self.feature_set,
                      self.training_set,
                      self.pair_strategy,
                      self.metadata_filter,
                      self.feature_filter,
                      self.n_random_seeds,
                      self.dimensionality_reduction,
                      self.normalization,
                      self.mlab_algorithm,
                      self.feature_transform,
                      self.allele_info,
                      self.meta_encoder,
                      self.downsample_count,
                      self.target_set]

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
            bt, fs, ts, ps, mf, ff, num_seeds, dr, norm, algo, ft, ai, me, dc, targ = chosen
            yield AnalysisConfig(
                self._analysis_name_gen(all_params, chosen),
                bt,
                self.metadata_filepath,
                fs,
                ts,
                ps,
                mf,
                ff,
                num_seeds,
                dr,
                norm,
                algo,
                ft,
                ai,
                me,
                dc,
                targ
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
