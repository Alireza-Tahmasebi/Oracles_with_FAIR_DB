import json
import subprocess

def load_raw_cfds(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def run_cfd_discovery(config_path, input_csv, output_txt):
    with open(config_path, 'r') as f:
        config = json.load(f)

    cfd_cfg = config.get("CFDDiscovery", {})
    exe_path = cfd_cfg.get("executable_path")
    support = cfd_cfg.get("support_count", 900)
    confidence = cfd_cfg.get("confidence", 0.9)
    max_size = cfd_cfg.get("max_condition_size", 3)
    

    cmd = [exe_path, input_csv, str(support), str(confidence), str(max_size)]



    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        with open(output_txt, 'w') as f:
            f.write(result.stdout)
        print(f"CFD discovery algorithm completed successfully! Output saved to {output_txt}")
    except subprocess.CalledProcessError as e:
        print("CFD discovery failed!")
        print("stderr:", e.stderr)
    except Exception as ex:
        print("An unexpected error occurred:", ex)


def filter_by_target_value(lines, config, print_summary=True):

    '''
    Filters a list of raw CFD lines and keeps only those that contain
    the target attribute (for example 'income=') as defined in config.
    '''

    #Extracting target attribute from config.
    target_attr = config.get("target_attribute", "income=")

    kept_lines = []
    removed_count = 0

    for line in lines:
        if not (line.startswith('Mined ') or line == '') :   #Because CFDDiscovery algorithm, returns a message like "Mined 317 cfds in 363 milliseconds" at the end of .txt file!
            if target_attr in line:
                kept_lines.append(line)
            else:
                removed_count += 1



    if print_summary:
        print(f"\nBased on Target attribute: {target_attr}")
        print(f"Kept {len(kept_lines)} lines (containing target attribute).")
        print(f"Removed {removed_count} lines (missing target attribute).")

    return kept_lines


def replace_incomparable_symbols(lines):
    #convert    '<=' to '<'     and     '>=' to '>' 
    return [
        line.replace("<=", "<").replace(">=", ">")
        for line in lines
    ]


def remove_parentheses(lines):
    #delete the paranthesis
    return [
        line.replace("(", "").replace(")", "")
        for line in lines
    ]


def remove_lines_without_arrow(lines, config_CFD):


    #Removes lines that do not contain the implication direction " => " by default, but it also checks config!
    
    arrow_str = config_CFD.get("arrow_string", " => ")
    filtered = []
    for line in lines:
        if arrow_str in line:
            filtered.append(line)
        
    return filtered


def parseCFD(rule, config_CFD):
    ##Function to select only ACFDs from all rules (removes AFDs)!
    arrow_str = config_CFD.get("arrow_string", " => ")
    lhs_sep   = config_CFD.get("lhs_separator", ", ")

    # Splits the rule into LHS and RHS
    rawLHS, rawRHS = rule.split(arrow_str)

    # Splits each side into attribute-value pairs
    lhs_parts = rawLHS.split(lhs_sep)
    rhs_parts = rawRHS.split(lhs_sep)

    # Check for empty values on LHS
    for part in lhs_parts:
        if '=' in part:
            attr, val = part.split('=', 1)
            if not val.strip():
                # For empty or whitespace-only value, we discard the entire rule
                return None
        else:
            # I assumed that CFDDiscovery algorithm produces ACDs for example in this "workplace=" format
            # and we don't have cases like "workplace". but if I observed I will take care of it here later!
            return None



    # Check for empty values on RHS
    for part in rhs_parts:
        if '=' in part:
            attr, val = part.split('=', 1)
            if not val.strip():
                return None
        else:
            return None


    return [lhs_parts, rhs_parts]


def parseCFDWithCond(rule, config_CFD, condlhs, condrhs):

    arrow_str = config_CFD.get("arrow_string", " => ")
    lhs_sep   = config_CFD.get("lhs_separator", ", ")

    # Splits the rule into LHS and RHS
    rawLHS, rawRHS = rule.split(arrow_str)

    # Splits each side into attribute-value pairs
    lhs_parts = rawLHS.split(lhs_sep)
    rhs_parts = rawRHS.split(lhs_sep)


    # Check for empty values on LHS
    for part in lhs_parts:
        if '=' in part:
            attr, val = part.split('=', 1)
            if not val.strip():
                # For empty or whitespace-only value, we discard the entire rule
                return None
        else:
            # I assumed that CFDDiscovery algorithm produces ACDs for example in this "workplace=" format
            # and we don't have cases like "workplace". but if I observed I will take care of it here later!
            return None


    # Check for empty values on RHS
    for part in rhs_parts:
        if '=' in part:
            attr, val = part.split('=', 1)
            if not val.strip():
                return None
        else:
            return None
        

    # Check for any condition specified in condlhs on the left-hand side.
    # If any condition from condlhs is found in lhs_parts, discard the rule.
    for condition in condlhs:
        for part in lhs_parts:
            if condition in lhs_parts:
                return None

    # Check for conditions specified in condrhs on the right-hand side.
    for condition in condrhs:
        for part in rhs_parts:
            if condition in rhs_parts:
                return None

    return [lhs_parts, rhs_parts]


def filterRules(splitted_cfds, config_CFD, condlhs=None, condrhs=None, print_summary= True):
    #Removes AFDs and keeps ACFDs!
    # Also specified conditions on the lhs and rhs can be removed! like [["income=<50K"], ["workclass=private"]] or ["workclass=private"]
    if condlhs is None:
        condlhs = []
    if condrhs is None:
        condrhs = []


    o3 = []
    if not condlhs and not condrhs:
        # No conditions => just parseCFD
        for i in splitted_cfds: #splitted_cfds is a list.
            x = parseCFD(i, config_CFD) #parseCFD takes string as input!
            if x is not None:
                o3.append(x)
    else:
        # parseCFDWithCond
        for i in splitted_cfds:
            x = parseCFDWithCond(i, config_CFD, condlhs, condrhs)
            if x is not None:
                o3.append(x)


    if print_summary: 
        print("Total number of dependencies remained:", len(o3))
        for rule in o3:
            print(rule)

    return o3


def parse_rules_to_dict(o3, print_summary=True):
    
    '''
    This function takes a list of rules (o3), and transforms each rule into a dictionary
    with 'lhs' and 'rhs' keys. Each side is by itself a dictionary maping 'attribute' to 'value'.
    It also discards entire rules if the LHS or RHS ends up with no valid tokens.
    Also, it skips tokens with empty attribute or empty value (e.g. 'workclass=').
    It might not be the case in this "adult.csv" data set, but it's here to guarantee nothing bad happens in general!
    '''

    
    # Step 1) we want to only keep tokens that contain '=' and both sides are non-empty.
    def splitElem(l1):
        '''
        l1 is a list of strings like ['income>50k', 'workclass=']
        We skip any token that doesn't have '=', or those with empty attr or empty value.
        '''
        splitted = []
        for token in l1:
            if '=' in token:
                # Split into maximum 2 parts.
                # Similar to what we did in parseCFD(), but more complete checks!
                attr, val = token.split('=', 1)
                attr, val = attr.strip(), val.strip()
                # Keep only if both attribute and value are non-empty.
                if attr and val:
                    splitted.append([attr, val])
        return splitted


    # Step 2) Convert each rule into [LHS, RHS]; discard rule if LHS or RHS is empty
    def createSplitting(elem):
        # elem is something like [['income>50k', 'workclass='], ['race=White']]
        lhs_tokens, rhs_tokens = elem[0], elem[1]
        
        # Split each side (only keep valid tokens)
        splitted_lhs = splitElem(lhs_tokens)
        splitted_rhs = splitElem(rhs_tokens)
        
        # If either side has no valid tokens, we discard the entire rule
        if not splitted_lhs or not splitted_rhs:
            return None
        
        return [splitted_lhs, splitted_rhs]



    # Step 3) Build {attr: val}, replacing '<' with '<=' in the values
    def createDictionaryElem(side):
        """
        side might be something like [['income>50k'], ['sex','Male']]
        but after filtering, it's guaranteed each item has [attr, val].
        """
        result = {}
        for pair in side:
            attr, val = pair
            # Replace '<' with '<=' in the value
            val = val.replace('<', '<=')
            result[attr] = val
        return result



    # 1) Transform each rule in o3 into splitted tokens
    splitted_rules = []
    for rule in o3:    #rule is like [['education_degree=Elementary'], ['income=<50K']] or [['income>50k', 'workclass='], ['race=White']]
        splitted = createSplitting(rule)
        if splitted is not None:
            splitted_rules.append(splitted)

    # 2) Build the final dictionary of parsed rules
    parsedRules = []
    for lhs_side, rhs_side in splitted_rules:
        parsedRules.append({
            'lhs': createDictionaryElem(lhs_side),
            'rhs': createDictionaryElem(rhs_side)
        })
    
    # 3) Print summary if the flag is set to True!
    if print_summary:
        print("Total number of dependencies in the dictionary:", len(parsedRules))
        max_show = min(50, len(parsedRules))
        print(f"The first {max_show} dependencies:\n")
        for i in range(max_show):
            print(f"{i+1}) {parsedRules[i]}")
    
    return parsedRules


