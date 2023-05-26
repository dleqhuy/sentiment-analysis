import modules.utils as Utils
import modules.processor as Processor
import numpy as np
import pandas as pd
import enchant
import random

from  underthesea  import  word_tokenize 
from sklearn.utils import shuffle

reviews = pd.read_csv('/content/drive/MyDrive/shopee/product_reviews.csv') 

print("Tập dữ liệu có {} bình luận.".format(reviews.shape[0]))

# Tiến hành label cho `reviews` với các giá `rating` $< 4$ sẽ thuộc nhóm negative còn lại là nhóm positive.

reviews['label'] = reviews['rating'].apply(lambda rt: 1 if rt >= 4 else 0)
reviews = reviews.drop(columns=['rating'])
reviews['normalize_comment'] = reviews['comment'].apply(lambda cmt: Processor.normalizeComment(cmt))
