from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState


def build():
    return NamedFunctor("Fix Sample IDs",
                        lambda state, mode: fix_sample_ids(state))


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


def _parse_household_id(sample_id: str):
    # Input of form Q.71401.0009.2016.02.23
    # Output of form 71401-0009
    return sample_id[0:3] + sample_id[5:]
