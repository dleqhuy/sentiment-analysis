import re
import unicodedata
import pandas as pd
import os
from underthesea import sentiment, text_normalize
from tqdm import tqdm

'''Pattern dùng để kiểm tra text có chứa url hay ko'''
URL = unicodedata.normalize('NFD', r'https?://\S+')


'''Các kí tự utf-8 upper'''
UTF8_UPPER =  unicodedata.normalize('NFD', r"[^A-ZÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]")


'''Các kí tự utf-8 lower'''
UTF8_LOWER = unicodedata.normalize('NFD', r"[^a-záàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ ]")


def containsURL(ptext: str) -> (int):
    """
    Dùng kiểm tra ptext có chứa url hay ko

    Args:
        ptext (str): comment

    Returns:
        [str]: comment đã loại bỏ url
    """

    return re.sub(URL,"", ptext)


def normalizeComment(ptext: str, plower: bool = True) -> (str):
    """
    Chuẩn hóa text bằng cách lower nó sau đó sử dụng phương pháp NFD để biểu diễn text
    Args:
        ptext (str): comment
        plower (bool): có lower ko
    Returns:
        [str]: comment đã lower và chuẩn hóa
    """
    ptext = ptext.lower() if plower else ptext
    return unicodedata.normalize('NFD', ptext)


def removeSpecialLetters(ptext: str) -> (str):
    """
    Dùng xóa các kí tự đặc biệt

    Args:
        ptext (str): comment

    Returns:
        [str]: comment without special characters
    """
    return re.sub("\s+", " ", re.sub(UTF8_LOWER, " ", ptext)).strip() 


def removeDuplicateLetters(ptext: str) -> (str):
    """
    Hàm dùng xóa các kí tự bị dupplucate, giả sử :
      * ptext = 'okkkkkkkkkkkkkkkkkkkkkk chờiiiiiiiiii ơiiiiiiii xinhhhhhhhhhhhh quá đẹppppppppp xỉuuuuuuu'
      * Sau khi dùng hàm này thì thành:
        ptext = 'ok chời ơi xinh quá đẹp xỉu'
      
    Args:
        ptext (str): comment

    Returns:
        [str]: comment that removing duplicated letters 
    """
    return re.sub(r'(.)\1+', r'\1', ptext)

class PredictSentiment():
    def __init__(self):
        self.basepath = os.path.abspath(os.path.dirname(__file__))


    def __call__(self, product_review):
        predict = []
        product_review = product_review.dropna(subset='comment').reset_index()
        product_review['normalize_comment'] = product_review['comment'].apply(lambda cmt: normalizeComment(cmt))
        product_review['normalize_comment'] = product_review['normalize_comment'].apply(lambda cmt: containsURL(cmt))
        product_review['normalize_comment'] = product_review['normalize_comment'].apply(lambda cmt: removeSpecialLetters(cmt))
        product_review['normalize_comment'] = product_review['normalize_comment'].apply(lambda cmt: removeDuplicateLetters(cmt))
        product_review['normalize_comment'] = product_review['normalize_comment'].apply(lambda cmt: text_normalize(cmt))

        review = product_review['normalize_comment']
        for i in tqdm(range(0,len(review))):

            predict.append(sentiment(review[i]))

        product_review['sentiment'] = predict
        product_review[['cmtid','sentiment']].dropna(subset=['sentiment']).to_csv(
            self.basepath + "/csv/predict_sentiment.csv",
            index=False,
            header=False,
        )
if __name__ == "__main__":

    basepath = os.path.abspath(os.path.dirname(__file__))
    product_review = pd.read_csv(basepath + "/csv/pdp_comment_raw.csv")
    predict = PredictSentiment()
    predict(product_review)
