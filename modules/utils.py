import os
import re
import pandas as pd
import unicodedata
import glob
from os.path import isfile, join
from typing import List, Dict


def readCSVfromfolder(pdirectoryPath: List[str]):
    """
    Dùng để đọc tất cả các file csv
    
    Args:
        pdirectoryPath (List[str]): đường dẫn của folder chứa các file csv

    Returns:
        [Dataframe]: pandas dataframe 
    """
    # Lấy tất cả các directory path của các lần ta tiến hành crawl data
    all_files = glob.glob(os.path.join(pdirectoryPath, "*.csv"))

    # Đọc toàn bộ các file csv
    df_from_each_file = (pd.read_csv(f) for f in all_files)
    df_data  = pd.concat(df_from_each_file, ignore_index=True)

    return df_data.dropna().reset_index(drop=True)
            
