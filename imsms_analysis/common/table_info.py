from biom import load_table
from qiime2 import Artifact, Metadata
import pandas as pd


class TableInfo:
    def load_dataframe(self):
        pass


class BiomTable(TableInfo):
    def __init__(self, biom_type):
        self.biom_type = biom_type
        self.biom_filepath = "./dataset/biom/combined-" + biom_type + ".biom"

    def load_dataframe(self):
        biom_table = load_table(self.biom_filepath)
        table = Artifact.import_data("FeatureTable[Frequency]", biom_table)
        df = table.view(pd.DataFrame)
        return df

    def read_biom_metadata(self):
        biom_table = load_table(self.biom_filepath)
        genera = biom_table.metadata_to_dataframe(axis="observation")
        # print(genera)
        return genera

    def __str__(self):
        return self.biom_type


class CSVTable(TableInfo):
    def __init__(self, csv_filepath, **read_kwargs):
        self.csv_filepath = csv_filepath
        self.read_kwargs = read_kwargs

    def load_dataframe(self):
        csv_table = pd.read_csv(self.filepath, **self.read_kwargs)
        return csv_table

    def __str__(self):
        return self.csv_filepath


class MergeTable(TableInfo):
    def __init__(self, table_list, col_suffix_list, table_name="Merged"):
        self.table_list = table_list
        self.col_suffix_list = col_suffix_list
        self.table_name = table_name

    def load_dataframe(self):
        df = self.table_list[0].load_dataframe()
        df = df.add_suffix(self.col_suffix_list[0])
        for i in range(1, len(self.table_list)):
            df = df.join(self.table_list[i].load_dataframe(),
                         how="outer",
                         rsuffix=self.col_prefix_list[i])
        print(df)
        return df

    def __str__(self):
        return self.table_name
