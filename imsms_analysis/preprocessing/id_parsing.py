from typing import Callable

from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState


def build(id_parse_func: Callable):
    return NamedFunctor("Fix Sample IDs",
                        lambda state, mode: fix_sample_ids(state, id_parse_func))


def fix_sample_ids(state: PipelineState, id_parse_func) -> PipelineState:
    return state.update_df(state.df.rename(mapper=id_parse_func))


def parse_finrisk_id(index: str):
    return index


def parse_FR02_id(index: str):
    ss = index.split(".")
    new_index = "S" + ss[1] + "-" + ss[2]
    return new_index


def parse_sol_id(index: str):
    return index


def parse_imsms_id(index: str):
    # Input of form Q.71401.0009.2016.02.23
    # Output of form 71401-0009
    ss = index.split('.')
    if len(ss) < 3:
        print("BAD: ", index)
        raise ValueError("Can't convert sample id:", index)

    sample_id = ss[1] + "-" + ss[2]
    return sample_id
