import os
import pandas as pd
import json
from IPython.display import display
from utils.file_reader_utils import Reader
from utils.preprocessing_utils import *
from utils.logger_utils import get_logger
logger = get_logger(__name__)

#run_preprocessing() does the same thing as preprocessing.ipynb but without showing the plots!
def run_preprocessing(config):
   
    # Either we use the 'project_root' from config or default to current working directory
    project_root = config.get('project_root', os.getcwd())
    data_path = os.path.abspath(config['data_path'])

    # Reading the dataset!
    reader = Reader()
    df = reader.read(data_path)
    df_cleaned = df.copy()

    from utils.logger_utils import get_logger

    logger = get_logger(__name__)

    logger.info("Stripping leading/trailing spaces...")
    df_cleaned = check_and_strip_spaces(df_cleaned, fix=True, print_summary=True)

    logger.info("Standardizing missing value placeholders...")
    df_cleaned = standardize_missing_values(df_cleaned, config=config, print_summary=True)

    logger.info("Converting object columns with numeric-looking values...")
    df_cleaned = convert_numeric_objects(df_cleaned)

    logger.info("Removing duplicate rows...")
    df_cleaned = remove_duplicates(df_cleaned, normalize_text=True, print_summary=True)

    logger.info("Dropping irrelevant features based on config...")
    df_cleaned = drop_irrelevant_features(df_cleaned, config=config, print_summary=True)

    logger.info("Discretizing variables...")
    df_cleaned = discretize_from_config(df_cleaned, config=config, print_summary=True, drop_original=True)



#-------------------------------------------------------------------Organize them LATER!!!!---------------------------------
    # Defining the bins and corresponding labels
    bins = [1, 2, 5, 8, 10, 12, 14, 16, np.inf]
    labels = [
    'Preschool',      # it covers education_num = 1
    'Elementary',     # it covers education_num in [2..4]
    'MiddleSchool',   # it covers education_num in [5..7]
    'HS-College',     # it covers education_num in [8..9]
    'Assoc',          # it covers education_num in [10..11]
    'Bach',           # it covers education_num in [12..13]
    'Mast',           # it covers education_num in [14..15]
    'Postmaster'      # it covers education_num >= 16
]

# Creating a new categorical column named 'education_degree'
    df_cleaned['education-degree'] = pd.cut(  
    df_cleaned['education-num'],
    bins=bins,
    labels=labels,
    right=False  # left-closed, right-open intervals
    )

    df_cleaned.drop(columns=['education-num', 'education'], inplace=True)

#-------------------------------------------------------------------Organize them LATER!!!!---------------------------------


    # Our output path
    output_path = os.path.join(project_root, 'outputs', 'cleaned_data_for_cfd.csv')
    logger.info(f"Will save cleaned CSV to: {output_path}")

    # Saving the cleaned DataFrame
    df_cleaned.to_csv(output_path, index=False)
    logger.info(f"Cleaned CSV saved to: {output_path}")
    
    #optional! remove it later! or maybe not
    display(df_cleaned.head(10))

    return df_cleaned