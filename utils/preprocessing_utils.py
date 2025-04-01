import pandas as pd
import numpy as np
from utils.logger_utils import get_logger
logger = get_logger(__name__)

#Converting missing values to Nan
#The function has as default values, the most common types of missing value but you can specify a rare type of missing value
#to be considered along with the default missing value symbols.
def standardize_missing_values(df, config=None, print_summary=True):
    
    df_clean = df.copy()

    # First we try to load missing value patterns from config
    default_missing_values = []
    custom_missing_values = []



    if config:
        mv_config = config.get("MissingValueHandling", {})
        default_missing_values = mv_config.get("default", {}).get("missing_values", [])
        custom_missing_values = mv_config.get("custom", {}).get("missing_values", [])

    all_missing_values = list(dict.fromkeys(default_missing_values + custom_missing_values))



    # Column by column replacement!
    replacements = {}

    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':  # Apply only to object/string columns
            col_replacements = {}
            for val in all_missing_values:
                match_count = (df_clean[col] == val).sum()
                if match_count > 0:
                    df_clean[col] = df_clean[col].replace(val, np.nan)
                    col_replacements[val] = int(match_count)

            if col_replacements:
                replacements[col] = col_replacements




    # if print_summary flag is set to True.
    if print_summary:
        if replacements:
            logger.info("Missing value replacements by column:")
            for col, vals in replacements.items():
                    logger.info(f"   Column: {col}")
                    for val, count in vals.items():
                        logger.info(f"     '{val}' → NaN: {count} occurrence found.")
                    else:
                        logger.info("No matching missing value placeholders found.")
            else:
                logger.debug("Missing value replacements processed successfully.")

    return df_clean



def check_and_strip_spaces(df, fix=False, print_summary=True):
   
    #Checks for leading or trailing spaces in string (object) columns.
    
    df_clean = df.copy()
    flagged_columns = []

    for col in df.columns:
        if df[col].dtype == 'object':
            has_spaces = df[col].astype(str).apply(lambda x: x != x.strip())
            if has_spaces.any():
                flagged_columns.append(col)
                if print_summary:
                    print(f" Column '{col}' has {has_spaces.sum()} values with leading/trailing spaces.")
                if fix:
                    df_clean[col] = df[col].astype(str).str.strip()




    if not flagged_columns and print_summary:
        logger.info("No leading/trailing spaces found in that object columns.")

    return df_clean



def convert_numeric_objects(df, apply_changes=True, print_summary=True):
    
    #Finds object columns that contain numeric-looking values and converts them to numeric dtype.
    
    df_clean = df.copy()
    converted_columns = []

    for col in df.columns:
        if df[col].dtype == 'object':
            cleaned = df[col].astype(str).str.replace(",", "").str.strip()
            numeric = pd.to_numeric(cleaned, errors='coerce')



            if not numeric.isna().all():
                if apply_changes:
                    df_clean[col] = numeric
                converted_columns.append(col)


    if print_summary:
        if converted_columns:
            logger.info(f" Converted to numeric: {converted_columns}")
        else:
            logger.info(" No numeric-looking object columns found.")

    return df_clean



def remove_duplicates(df, normalize_text=True, print_summary=True):

    #Removing duplicated rows, considering that "Canada" and "canada" are the same!
    #First normalizes text columns (lowercase & strip), then removes exact duplicated rows.

    df_clean = df.copy()

    if normalize_text:
        for col in df_clean.select_dtypes(include='object').columns:
            df_clean[col] = df_clean[col].str.strip().str.lower()



    n_before = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    n_after = len(df_clean)




    removed = n_before - n_after
    if print_summary:
        logger.info(f"Removed {removed} duplicated rows.")

    return df_clean



def drop_irrelevant_features(df, config, print_summary=True):
    #Feature selection: we drop the columns that are not too relevant for our study purpose
    #also we drop 

    # Gets irrelevant features from config
    config_columns = config.get("irrelevant_features", [])

    # Normalizes config feature names (strip + lowercase)
    normalized_config = {col.strip().lower(): col for col in config_columns}

    # Normalize DataFrame columns (strip + lowercase)
    normalized_df_columns = {col.strip().lower(): col for col in df.columns}

    # Finds overlapping columns
    to_drop_normalized = set(normalized_config.keys()) & set(normalized_df_columns.keys())

    # Gets actual column names from the DataFrame
    to_drop_actual = [normalized_df_columns[col] for col in to_drop_normalized]

    # Drop the columns
    df_clean = df.drop(columns=to_drop_actual)


    if print_summary:
        if to_drop_actual:
            logger.info(f" Dropped irrelevant features: {to_drop_actual}")
        else:
            logger.info(" No irrelevant features matched and dropped.")

    return df_clean



def discretize_from_config(df, config, print_summary=True, drop_original=True):
   
    #Discretizes multiple columns based on 'discretization' in config.

    df_clean = df.copy()
    discretization_cfg = config.get("discretization", {})

    for col_name, settings in discretization_cfg.items():
        bins = settings["bins"]
        labels = settings["labels"]
        new_col = f"{col_name}_range"

        if col_name not in df_clean.columns:
            logger.debug(f" Column '{col_name}' not found in dataset. Skipping.")
            continue


        # Binning
        df_clean[new_col] = pd.cut(
            df_clean[col_name],
            bins=bins,
            labels=labels,
            include_lowest=True,
            right=True
        )

        # Drop original column
        if drop_original:
            df_clean.drop(columns=[col_name], inplace=True)


        # Print summary if flag is set!
        if print_summary:
            logger.info(f"\n Distribution for {new_col}:")
            logger.info("\n" + df_clean[new_col].value_counts().to_string()) #value_counts() returns a series! so we need to log it in this way!

    return df_clean



#-------------------------------FOR NOW, I don't use missing_values_percentage(). check it later to decide for removal-------------------
def missing_values_percentage(df):
    
    #Calculate the percentage of missing values for each column and also in overall.

    # Calculate the percentage of missing values per column
    missing_percentage_by_column = df.isnull().mean() * 100
    
    #Calculate the overall missing percentage.
    total_missing = df.isnull().sum().sum()
    total_cells = df.shape[0] * df.shape[1]
    overall_missing_percentage = (total_missing / total_cells) * 100
    
    return missing_percentage_by_column, overall_missing_percentage