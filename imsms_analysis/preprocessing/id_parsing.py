from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState


def build():
    return NamedFunctor("Fix Sample IDs",
                        lambda state, mode: fix_sample_ids(state))


def fix_sample_ids(state: PipelineState) -> PipelineState:
    return state.update_df(state.df.rename(mapper=_parse_sample_id))


def _parse_sample_id(index: str):
    # Finrisk sample ids match metadata ids in finrisk_metadata.tsv but must be converted
    # to match column "Barcode" in FR02.tsv
    ss = index.split(".")
    new_index = "S" + ss[1] + "-" + ss[2]
    return new_index
