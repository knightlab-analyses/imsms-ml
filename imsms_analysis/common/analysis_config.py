from typing import Optional

from imsms_analysis.common.dimensionality_reduction import DimensionalityReduction
from imsms_analysis.common.feature_filter import FeatureFilter
from imsms_analysis.common.feature_set import FeatureSet
from imsms_analysis.common.meta_encoder import MetaEncoder
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import TableInfo
from imsms_analysis.common.target_set import TargetSet
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    FeatureTransformer


class AnalysisConfig:
    def __init__(self,
                 analysis_name: str,
                 table_info: TableInfo,
                 metadata_filepath: str,
                 feature_set_index: Optional[FeatureSet],
                 training_set_index: Optional[int],
                 pair_strategy: Optional[str],
                 metadata_filter: Optional[MetadataFilter],
                 feature_filter: Optional[FeatureFilter],
                 n_random_seeds: Optional[int],
                 dimensionality_reduction: Optional[DimensionalityReduction],
                 normalization: Optional[Normalization],
                 mlab_algorithm: Optional[str],
                 feature_transform: Optional[FeatureTransformer],
                 allele_info: Optional[str],
                 meta_encoder: Optional[MetaEncoder],
                 downsample_count: Optional[int],
                 target_set: Optional[TargetSet]):
        self.analysis_name = analysis_name
        self.table_info = table_info
        self.metadata_filepath = metadata_filepath
        self.feature_set_index = feature_set_index
        self.training_set_index = training_set_index
        self.pair_strategy = pair_strategy
        self.metadata_filter = metadata_filter
        self.feature_filter = feature_filter
        self.n_random_seeds = n_random_seeds
        self.dimensionality_reduction = dimensionality_reduction
        self.normalization = normalization
        self.mlab_algorithm = mlab_algorithm
        self.feature_transform = feature_transform
        self.allele_info = allele_info
        self.meta_encoder = meta_encoder
        self.downsample_count = downsample_count
        self.target_set = target_set
