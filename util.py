import pandas as pd


def fix_input(input: pd.DataFrame):
    df = _filter_by_sample_id(input)
    df = df.rename(mapper=_parse_sample_id)
    # print("With Dups")
    # print(df)
    df = df.groupby(lambda x: x).sum()
    # print("Dups Removed")
    # print(df)
    return df


def _filter_by_sample_id(df: pd.DataFrame) -> pd.DataFrame:
    bad_rows = \
        df.index.str.startswith('NA.') | \
        df.index.str.startswith('UCSF.') | \
        df.index.str.startswith('COLUMN.') | \
        df.index.str.startswith('Column.') | \
        df.index.str.startswith('Q.DOD') | \
        df.index.str.startswith("Zymo.") | \
        df.index.str.startswith("Mag.Bead.Zymo.")
    return df[~bad_rows]


def _parse_sample_id(index: str):
    # print(index)
    # Input of form Q.71401.0009.2016.02.23
    # Output of form 71401-0009
    ss = index.split('.')
    if len(ss) < 3:
        # print("BAD: ", index)
        return index

    sample_id = ss[1] + "-" + ss[2]
    # print("GOOD: ", index, "->", sample_id)
    return sample_id
