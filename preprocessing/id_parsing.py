import pandas as pd
from common.named_functor import NamedFunctor
from state.pipeline_state import PipelineState


def build():
    return NamedFunctor("Fix Sample IDs", fix_sample_ids)


def fix_sample_ids(state: PipelineState) -> PipelineState:
    return state.update_df(state.df.rename(mapper=_parse_sample_id))


def _parse_sample_id(index: str):
    # print(index)
    # Input of form Q.71401.0009.2016.02.23
    # Output of form 71401-0009
    ss = index.split('.')
    if len(ss) < 3:
        print("BAD: ", index)
        raise ValueError("Can't convert sample id:", index)

    sample_id = ss[1] + "-" + ss[2]
    # print("GOOD: ", index, "->", sample_id)
    return sample_id
