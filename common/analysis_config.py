from typing import Optional

from common.dimensionality_reduction import DimensionalityReduction
from common.feature_set import FeatureSet
from common.metadata_filter import MetadataFilter


class AnalysisConfig:
    def __init__(self,
                 analysis_name: str,
                 biom_filepath: str,
                 metadata_filepath: str,
                 feature_set_index: Optional[FeatureSet],
                 training_set_index: Optional[int],
                 pair_strategy=Optional[str],
                 metadata_filter=Optional[MetadataFilter],
                 n_random_seeds=Optional[int],
                 dimensionality_reduction=Optional[DimensionalityReduction]):
        self.analysis_name = analysis_name
        self.biom_filepath = biom_filepath
        self.metadata_filepath = metadata_filepath
        self.feature_set_index = feature_set_index
        self.training_set_index = training_set_index
        self.pair_strategy = pair_strategy
        self.metadata_filter = metadata_filter
        self.n_random_seeds = n_random_seeds
        self.dimensionality_reduction = dimensionality_reduction
