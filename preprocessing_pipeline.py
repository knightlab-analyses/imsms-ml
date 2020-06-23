import pandas as pd
from preprocessing import id_parsing, sample_filtering, sample_aggregation

BAD_SAMPLE_PREFIXES = [
    'NA.',
    'UCSF.',
    'COLUMN.',
    'Column.',
    'Q.DOD',
    'Zymo.',
    'Mag.Bead.Zymo.'
]


def fix_input(df: pd.DataFrame, verbose=False):
    steps = [
        sample_filtering.build(BAD_SAMPLE_PREFIXES),
        id_parsing.build(),
        sample_aggregation.build("sum")
    ]

    if verbose:
        print("Input: ")
        print(df)

    for s in steps:
        if verbose:
            print("Begin step:", s)
        df = s(df)
        if verbose:
            print("Result After:", s)
            print(df)

    return df

