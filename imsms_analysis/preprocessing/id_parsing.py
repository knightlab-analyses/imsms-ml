from imsms_analysis.common.named_functor import NamedFunctor
from imsms_analysis.state.pipeline_state import PipelineState


def build(id_parse_func):
    return NamedFunctor("Fix Sample IDs",
                        lambda state, mode: fix_sample_ids(state, id_parse_func))


def fix_sample_ids(state: PipelineState, id_parse_func) -> PipelineState:
    return state.update_df(state.df.rename(mapper=id_parse_func))


def _parse_sample_id(index: str):
    if index.startswith("11326."):
        index = index[6:]
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


def _parse_disease_state(sample_id):
    ss = sample_id.split('-')
    # Input of form 71401-0009
    if len(ss) != 2:
        print("BAD", sample_id)
        raise ValueError("Can't convert sample id:", sample_id)
    if ss[0].endswith("1"):
        return "MS"
    elif ss[0].endswith("2"):
        return "Control"
    elif ss[0].endswith("3"):
        return "MS (Unpaired)"
    else:
        print("BAD")
        print(sample_id)
        return "Weirdly Marked"


def _parse_household_id(sample_id: str):
    # Input of form 71401-0009
    # Output of form 714-0009
    return sample_id[0:3] + sample_id[5:]
