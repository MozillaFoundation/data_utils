from pandas import DataFrame, notnull, isnull
from numpy import nan

def compare_values(x, y):
    if isnull(x) or isnull(y):
        if isnull(x) and notnull(y):
            return False
        elif notnull(x) and isnull(y):
            return False
        else:
            return True
    else:
        if x == y:
            return True
        else:
            return False

def parity_check(df, exclusions, id_cols, suffix_list):
    if isinstance(df, DataFrame):
        df = df.copy()
        if len(suffix_list) == 2:
            
            cols = list(set([c.replace(suffix_list[0], '').replace(suffix_list[1], '')
                     for c in df.columns if c not in exclusions]))

            compares = {c + '_compare': (c + suffix_list[0], c + suffix_list[1]) for c in cols}

            df.fillna(nan, inplace = True)

            for k,v in compares.items():
                df[k] = df.apply(lambda x: compare_values(x[v[0]], x[v[1]]), axis = 1)

            diffs = {c: (df[df[c] == False][[c] +list(id_cols) + list(compares.get(c))]
                     .copy()
                     .drop_duplicates())
                     for c in list(compares.keys())}

            for k,v in diffs.items():
                col_print = k.replace('_compare', '')
                
                print('There are {} differences ({}%) between the input dataframes for the {} column'.format(len(v)
                                                                                                              ,round(len(v)/len(df) * 100, 2)
                                                                                                              ,col_print))
                
            return diffs

        else:
            raise Exception('suffix_list must have a length of 2!')

    else:
        raise TypeError('df must be a pandas dataframe!')
    

    
