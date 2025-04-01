from utils.cfd_utils import *

def run_full_cfd_discovery(config_path_CFD, input_csv, output_txt):
    run_cfd_discovery(config_path_CFD, input_csv, output_txt)
    raw_cfds = load_raw_cfds(output_txt)
    return raw_cfds



def filter_cfds(raw_cfds, config_CFD, condlhs, condrhs):
    lines = filter_by_target_value(raw_cfds, config_CFD, print_summary=False)
    lines = replace_incomparable_symbols(lines)  
    lines = remove_parentheses(lines)
    lines= remove_lines_without_arrow(lines, config_CFD) 
    final = filterRules(lines, config_CFD, condlhs, condrhs, print_summary= False)
    dict_cfds = parse_rules_to_dict(final, print_summary=True)
    
    return dict_cfds
