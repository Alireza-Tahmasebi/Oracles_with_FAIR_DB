import importlib.util
import subprocess
import sys
import os
import pandas as pd

# Dependency checks in case we are importing Excel or Parquet files.
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if importlib.util.find_spec("openpyxl") is None:
    print("openpyxl is not installed. Installing openpyxl...")
    install("openpyxl")

if importlib.util.find_spec("pyarrow") is None:
    print("pyarrow is not installed. Installing pyarrow...")
    install("pyarrow")

#------------------------------------- CHECK IT LATER!---------------------------------------------------------
#Reading class, so we can keep the state of multiple file! for future work!
#THERE IS NO NEED FOR THIS! write a reader function! 
class Reader:
    def __init__(self):
        self.excel_extensions = {"xls", "xlsx", "xlsm", "xlsb", "odf", "ods", "odt"}
        self.readers = {
            "csv": self._read_csv,
            "json": pd.read_json,
            "parquet": pd.read_parquet,
        }


    def read(self, file_path):
        if not isinstance(file_path, str):
            raise TypeError("file_path must be a string.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")


        # getting the file extension
        ext = file_path.split(".")[-1].lower()

        if ext in self.excel_extensions:
            df = self._read_excel(file_path)
        elif ext in self.readers:
            df = self.readers[ext](file_path)
        else:
            raise ValueError(
                f"Unsupported file format: .{ext}. Supported formats are: CSV, Excel, JSON, and Parquet!!!"
            )
        

        # drop columns with "Unnamed" in the header.
        return self._drop_unnamed(df) 

    def _read_csv(self, file_path):
        try:
            return pd.read_csv(file_path)
        except pd.errors.ParserError:
            return pd.read_csv(file_path, delimiter=";")


    def _read_excel(self, file_path):
        return pd.read_excel(file_path)

    def _drop_unnamed(self, df):
        return df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]
