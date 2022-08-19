import os
import re
import pandas as pd
import unicodedata
import glob
from os.path import isfile, join
from typing import List, Dict


def readCSVfromfolder(pdirectoryPath):
    """
    Dùng để đọc tất cả các file csv
    
    Args:
        pdirectoryPath: đường dẫn của folder chứa các file csv

    Returns:
        [Dataframe]: pandas dataframe 
    """
    # Lấy tất cả các directory path của các lần ta tiến hành crawl data
    all_files = glob.glob(os.path.join(pdirectoryPath, "*.csv"))

    # Đọc toàn bộ các file csv
    df_from_each_file = (pd.read_csv(f) for f in all_files)
    df_data  = pd.concat(df_from_each_file, ignore_index=True)

    return df_data.dropna().reset_index(drop=True)
            
def buildDictionaryFromFile(ppath: str, psuffix: bool = False) -> (Dict[str, str]):
    """
    Dùng để xây dựng một từ điển tử filepath

    Args:
        ppath (str): đường dẫn file
        psuffix (bool): 

    Returns:
        [Dict[str, str]]: 
    """
    d = {}
    
    with open(ppath) as rows:
        if not psuffix:
            for row in rows:
                prefix, suffix = row.strip().split(',')
                prefix = unicodedata.normalize('NFD', prefix.strip())
                suffix = unicodedata.normalize('NFD', suffix.strip())
                d[prefix] = suffix
        else:
            for row in rows:
                prefix = unicodedata.normalize('NFD', row.strip())
                d[prefix] = True
                
    return d