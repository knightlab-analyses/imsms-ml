import pandas as pd

from imsms_analysis.common.analysis_config import AnalysisConfig
from imsms_analysis.common.feature_filter import ZebraFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.common.train_test import Passthrough, SplitByMetadata, \
    PairedSplit, UnpairedSplit
from imsms_analysis.dataset.sample_sets.fixed_training_set import retrieve_training_set
from imsms_analysis.events.analysis_callbacks import AnalysisCallbacks
from imsms_analysis.preprocessing import id_parsing, sample_filtering, \
    sample_aggregation, \
    normalization, classifier_target, train_test_split, column_transformation, \
    visualization, downsampling, column_filtering
from imsms_analysis.preprocessing.column_transformation import build_column_filter, build_feature_set_transform, sum_columns
from imsms_analysis.preprocessing.train_test_split import TrainTest, \
    passthrough
from imsms_analysis.state.pipeline_state import PipelineState

BAD_SAMPLE_PREFIXES = [
    'NA.',
    'UCSF.',
    'COLUMN.',
    'Column.',
    'Q.DOD',
    'Zymo.',
    'Mag.Bead.Zymo.',
    '11326.BLANK',
    '11326.Q.FMT'
]

BAD_SAMPLE_IDS = ["71601-0158", "71602-0158"]


def process(analysis_config: AnalysisConfig,
            state: PipelineState,
            callbacks: AnalysisCallbacks,
            restricted_feature_set: list = None,
            training_set_index: int = 0,
            verbose=False,
            pair_strategy="household_concat",
            metadata_filter=None,
            feature_filter=None,
            dim_reduction=None,
            normalization=Normalization.DEFAULT,
            feature_transform=None,
            meta_encoder=None,
            downsample_count=None,
            train_test=None):
    filtered = _filter_samples(analysis_config, state, callbacks, verbose)
    train, test = _split_test_set(train_test,
                                  filtered,
                                  training_set_index,
                                  verbose)
    return _apply_transforms(analysis_config,
                             train,
                             test,
                             callbacks,
                             restricted_feature_set,
                             verbose,
                             pair_strategy=pair_strategy,
                             metadata_filter=metadata_filter,
                             feature_filter=feature_filter,
                             dim_reduction=dim_reduction,
                             normalization_strategy=normalization,
                             feature_transform=feature_transform,
                             meta_encoder=meta_encoder,
                             downsample_count=downsample_count
                             )


# Run all steps required before we can split out the test set.  This must be
# restricted to operations that can be done at the level of individual samples
# (or technically paired samples of households), so as to avoid any interaction
# between test data and training data.
def _filter_samples(analysis_config: AnalysisConfig,
                    state: PipelineState,
                    callbacks: AnalysisCallbacks,
                    verbose=False):
    # noinspection PyListCreation
    steps = []

    if isinstance(analysis_config.table_info, BiomTable):
        # Filter out the bad samples (sample prefixes are based on pre-parsed
        # values. do not reorder below id_parsing)
        steps.append(sample_filtering.build_prefix_filter(BAD_SAMPLE_PREFIXES))
        # Parse the IDs and rename to match metadata
        steps.append(id_parsing.build(analysis_config.id_parse_func))
    # Run some aggregation function when multiple ids map to the same
    # sample ID, (due to technical replicates)
    steps.append(sample_aggregation.build("sum"))
    # Filter to rows shared between samples and metadata
    steps.append(sample_filtering.build_shared_filter())
    # Manually remove samples that have no household matched pair
    steps.append(sample_filtering.build_exact_filter(BAD_SAMPLE_IDS))
    # Filter out any samples that have row sum zero, these will be impossible
    # to normalize later.
    steps.append(sample_filtering.build_filter_out_empty_samples())

    return _run_pipeline(analysis_config, state, callbacks, steps, verbose, mode='filter')


# The test set must be split out at the level of household pairs.  This should
# be done as early in the processing as possible to avoid accidental leakage
# of test set data into the processing.  It is not acceptable to learn
# parameters from the test set, so any type of learned feature (Like PCA)
# must store its settings (ie, what column vectors to use) based on training
# set data, then reuse those transformations on the test set.
def _split_test_set(train_test: TrainTest,
                    state: PipelineState,
                    training_set_index=0,
                    verbose=False) -> TrainTest:

    if isinstance(train_test, Passthrough):
        return passthrough(state)
    elif isinstance(train_test, PairedSplit):
        return train_test_split.split(state,
                                      .5,
                                      verbose)
    elif isinstance(train_test, SplitByMetadata):
        return train_test_split.split_by_meta(state, train_test.meta_col, train_test.train_meta)
    elif isinstance(train_test, UnpairedSplit):
        raise NotImplemented("Unpaired split is not implemented in iMSMS")

    # Something something fixed training sets?
    # train_set_households = retrieve_training_set(training_set_index)
    # return train_test_split.split_fixed_set(state,
    #                                         train_set_households,
    #                                         verbose)
    # TODO Pass this through analysis config


def _apply_transforms(analysis_config: AnalysisConfig,
                      train_state: PipelineState,
                      test_state: PipelineState,
                      callbacks: AnalysisCallbacks,
                      restricted_feature_set: list = None,
                      verbose=False,
                      pair_strategy="paired_concat",
                      metadata_filter=None,
                      feature_filter=None,
                      dim_reduction=None,
                      normalization_strategy=Normalization.DEFAULT,
                      feature_transform=None,
                      meta_encoder=None,
                      downsample_count=None
                      ):

    # noinspection PyListCreation
    steps = []

    # Subset to household pairs whose individual samples are within particular
    # metadata values.  Can use these to determine if your model is detecting
    # microbes correlating with confounding variables.
    if metadata_filter is not None:
        steps.append(sample_filtering.build_whitelist_metadata_value(
            metadata_filter.column_name,
            metadata_filter.acceptable_values
        ))

    # Apply some normalization strategy to deal with compositionality of
    # the data, stemming from various sources - whether biological effects
    # and sample coverage/amount or from aggregation of varying numbers of
    # technical replicates.
    steps.append(normalization.build(normalization_strategy.method,
                                     **normalization_strategy.kwargs))

    # Is it okay for all column filtering to occur prior to normalization?
    # Zebra filter at least should only remove very small counts
    # so is probably okay...  Let's try after as well
    if feature_filter is not None:
        if isinstance(feature_filter, ZebraFilter):
            steps.append(column_filtering.build_zebra(feature_filter.cov_thresh, feature_filter.cov_file))

    if restricted_feature_set is not None:
        steps.append(build_column_filter(restricted_feature_set))

    if meta_encoder is not None:
        steps.append(column_transformation.build_meta_encoder(
            meta_encoder.col_name,
            meta_encoder.encoder)
        )

    # Show correlation matrix heatmap for debugging
    # steps.append(visualization.plot_correlation_matrix())

    # Run any feature transformations
    if feature_transform is not None:
        steps.append(build_feature_set_transform(feature_transform))
        # Try a summed univariate feature set (not so good with RF)
        # steps.append(sum_columns())

    # Build target series

    steps.append(
        classifier_target.build(
            "disease",
            {"MS"},
            pair_strategy=pair_strategy
        )
    )

    # Run PCA - This is a bit wonky in the simplex space,
    # and even more wonky in the household concatted rows space.
    # Give this more thought
    # Further, the PCA must be learned on the training set
    # (With a separate learned feature per cross validation index!)
    # and applied on the test set (no learning PCA on the test data!)
    # So keep this disabled until we can rethink how to structure this.
    if dim_reduction is not None:
        if dim_reduction.transform == "pca":
            steps.append(column_transformation.build_pca(**dim_reduction.kwargs))  # TODO: 20 might actually be too few!
        elif dim_reduction.transform == "lda":
            steps.append(column_transformation.build_lda(
                **dim_reduction.kwargs))
        elif dim_reduction.transform == "umap":
            steps.append(column_transformation.build_umap(**dim_reduction.kwargs))
        else:
            raise Exception("Unknown Transform:" + dim_reduction.transform)
        # steps.append(visualization.plot_scatter())
        # steps.append(visualization.plot_category())

    # Downsample the training set
    if downsample_count is not None:
        steps.append(downsampling.build(downsample_count))

    train, test = (
        _run_pipeline(analysis_config, train_state, callbacks, steps, verbose, mode='train'),
        _run_pipeline(analysis_config, test_state, callbacks, steps, verbose, mode='test')
    )
    return train, test


def _run_pipeline(analysis_config, state, callbacks, steps, verbose=False, mode='train'):
    if verbose:
        print("Input: ", mode)
        print(state)

    for s in steps:
        if verbose:
            print("Begin Step:", s)
        callbacks.before_preprocess_step(analysis_config, s, state, mode)
        state = s(state, mode)
        if verbose:
            print("Result After:", s)
            print(state)
        callbacks.after_preprocess_step(analysis_config, s, state, mode)
    return state
