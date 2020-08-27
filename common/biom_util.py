from biom import load_table
from qiime2 import Artifact, Metadata


def read_biom_metadata(biom_filepath):
    biom_table = load_table(biom_filepath)
    # table = Artifact.import_data("FeatureTable[Frequency]", biom_table)
    # df = table.view(pd.DataFrame)
    # print(df)

    genera = biom_table.metadata_to_dataframe(axis="observation")
    print(genera)
    return genera
