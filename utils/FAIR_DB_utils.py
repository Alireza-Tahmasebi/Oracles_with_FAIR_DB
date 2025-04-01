import pandas as pd
import numpy as np


def countOccur(elem, dataset):

    '''
    Returns a tuple (countX, countY, countXY), where:
      - countX = number of rows satisfying LHS
      - countY = number of rows satisfying RHS
      - countXY = number of rows satisfying both LHS and RHS
    '''


    # we build a boolean mask for the LHS
    lhs_mask = np.ones(len(dataset), dtype=bool)
    for key, value in elem['lhs'].items():
        # Convert to string & compare
        lhs_mask &= (dataset[key].astype(str) == str(value))


    # boolean mask for the RHS
    rhs_mask = np.ones(len(dataset), dtype=bool)
    for key, value in elem['rhs'].items():
        rhs_mask &= (dataset[key].astype(str) == str(value))



    # Summations of True in each mask
    countX = lhs_mask.sum()
    countY = rhs_mask.sum()
    countXY = (lhs_mask & rhs_mask).sum()

    return (countX, countY, countXY)


def computeConfidenceNoProtectedAttr(elem, dataset, protected_attr, target):

    '''
    Computes confidence by ignoring protected attributes and the target in the LHS.
    Confidence = support(LHS + RHS) / support(LHS), if LHS is not empty.
    '''

    # Filter out protected attributes and the target from LHS. RHS remains the same!
    filtered_rule = {
        'lhs': {k: v for k, v in elem['lhs'].items() if k not in protected_attr and k != target},
        'rhs': elem['rhs']
    }



    countX, countY, countXY = countOccur(filtered_rule, dataset)

    # Computes ratio!
    if countX != 0:
        return countXY / countX
    return 0.0


def computeConfidenceForProtectedAttr(elem, protAttr, dataset):

   
    #Computes confidence by removing just one protected attribute (protAttr) from the LHS.
 

    filtered_rule = {
        'lhs': {k: v for k, v in elem['lhs'].items() if k != protAttr},
        'rhs': elem['rhs']
    }



    countX, countY, countXY = countOccur(filtered_rule, dataset)


    if countX != 0:
        return countXY / countX
    return 0.0


def computePDifference(rule, conf, attribute, dataset, protected_attr):

    '''
    If 'attribute' is a protected attribute in rule['lhs'],
    compute difference between overall_conf and the confidence 
    after removing 'attribute' from LHS.
    '''

    if attribute in protected_attr:
         if(attribute in protected_attr):
            diffp = 0
            if(attribute in rule['lhs'].keys()):
                RHSConfidence = computeConfidenceForProtectedAttr(rule, attribute, dataset)
                diffp = conf - RHSConfidence
            return diffp
    return None


def equalRules(rule1,rule2):

    flagR = True
    flagL = True


    for keyL in rule1['lhs'].keys():
        if(keyL in rule2['lhs'].keys()):
            if(rule1['lhs'][keyL]!=rule2['lhs'][keyL]):
                flagL = False
        else:
            flagL = False



    for keyR in rule1['rhs'].keys():
        if(keyR in rule2['rhs'].keys()):
            if(rule1['rhs'][keyR]!=rule2['rhs'][keyR]):
                flagR = False
        else:
            flagR = False


    if(flagL==True and flagR == True):
        return True
    else:
        return False


def removeDuplicates(df):
    dfColumns = df.columns
    k=0
    dfClean= pd.DataFrame(columns = dfColumns)
    for i, row in df.iterrows():
        flag = True
        rule1 = df.loc[i, 'Rule']
        j=k-1
        while(j>=0):
            rule2 = dfClean.loc[j, 'Rule']
            if(equalRules(rule1,rule2)==True):
                flag = False
            j=j-1
        if(flag == True):
            dfClean.loc[k] = df.loc[i]
            k=k+1

    return dfClean




#----------------------------------------CHECK AND TRY TO improve the createTable()----------------------------
#maybe replace .loc with a list that is more efficient and then at the end convert it to a dataframe! check it later!
def createTable(parsedRules, dataset, protected_attr, target_attr):
    rows = []

    for parsedRule in parsedRules:
        
        count = countOccur(parsedRule, dataset)
        support = tuple(c /  len(dataset) for c in count)



        # Checks if the rule involves protected attributes
        involves_protected = any(attr in protected_attr for attr in parsedRule['lhs']) or \
                             any(attr in protected_attr for attr in parsedRule['rhs'])


        # Checks support[0] and support[1] are not zero and The rule involves at least one protected attribute!
        if all(support[:2]) and involves_protected:  
            conf = count[2] / count[0]
            conf_no_protected = computeConfidenceNoProtectedAttr(parsedRule, dataset, protected_attr, target_attr)
            diff = conf - conf_no_protected




            row = {
                'Rule': parsedRule,
                'Support': support[2],
                'Confidence': conf,
                'Diff': diff
            }


           
            for attr in protected_attr:
                if attr in parsedRule['lhs']:
                    diffp = computePDifference(parsedRule, conf, attr, dataset, protected_attr)
                    row[f"{attr}Diff"] = diffp

            rows.append(row)

    return pd.DataFrame(rows)
