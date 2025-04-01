from CFDs.CFDs_pipeline import *
from utils.FAIR_DB_utils import *
from IPython.display import display



#---------------------maybe add a function to generate and save all bar charts to Plot folder-----------------------------------


def run_FAIR_DB(dict_cfds, cleaned_data_for_cfd, protected_attributes, target_attribute, min_diff):
   
    # Step 1) Building the FAIR evaluation table
    df_all = createTable(dict_cfds, cleaned_data_for_cfd, protected_attributes, target_attribute)

    # Step 2) Filter by minimum difference (To select the not ethical rules)
    df_filtered = df_all[df_all["Diff"] > min_diff]

    display(df_filtered.head(40))

    return df_filtered
