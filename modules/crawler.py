import pandas as pd
import numpy as np
import re
import requests
from typing import List, Tuple

def getProductSearch(keyword: str):
    """
    Hàm này dùng để lấy urls theo keyword

    Args:
        keyword (str): keyword của nhóm mặt hàng cần lấy
    Returns:
        (str): chuổi url của các keyword
    """
    
    url = "https://shopee.vn/api/v2/search_items/?by=relevancy&keyword={}&limit=100&newest=0&order=desc&page_type=search".format(
        keyword_search
    )

    r = requests.get(url, headers=headers).json()
    df = pd.DataFrame(r["items"])
    df.to_csv('abc.csv', index=False)
    #return 
    
class Review:
    def __init__(self, pcomment: str, prating: int):
        """
        Constructor
        
        Args:
            pcomment (str): comment
            prating (int): rating nằm trong khoảng [1, 5]
        """
        self.icomment = pcomment
        self.irating = prating       

def getProductReviewsAPI(pproductURL: str) -> (List[Review]):
    """
    Hàm này dùng để crawl data bằng cách sử dụng API.

    Args:
        pproductURL (str): là URL đến với trang riêng của sản phẫm.
    """
    def collect_comment(ppage: int, pproductID: str, pshopID: str):
        """
        Một hàm bổ trợ dùng để crawl data trên một trang nhất định (navigation)

        Args:
            ppage (int): trang số mấy ta muốn lấy, bắt đầu từ 0
            pproductID (str): mã id của sản phẩm
            pshopID (str): mã id của người bán sản phẩm

        Returns:
            List[Review]:
        """
        
        ''' Các tham số cần truyền vào API để crawl data '''
        params = (
            ('filter', '0'),
            ('flag', '1'),
            ('itemid', pproductID),
            ('limit', '6'), # số 6 ở đây là nếu đếm số comment trong một navigation thì một trang có tối đa là 6 comment
            ('offset', ppage),
            ('shopid', pshopID),
            ('type', '0'))

        ''' Gửi một request đến API và nhận về response '''
        response = requests.get('https://shopee.vn/api/v2/item/get_ratings', params=params)
        return response.json().get('data').get('ratings')
    
    def parse_comment(presponse) -> (Tuple[int, str]):
        """
        Hàm này dùng để parse một response từ API thành hai phần là comment và rating

        Args:
            presponse ([type]): response trả về vừ API

        Returns:
            Tuple[int, str]: lần lượt là rating và comment của review
        """
        ratting = []
        comment = []
        for elem in presponse:
            ratting.append(elem.get('rating_star'))
            comment.append(elem.get('comment'))
        return ratting, comment
        
    
    '''
      Mỗi một URL sản phẩm nếu bạn chú ý sẽ có một thành phần là `i.0284272429.2342427424` như thế này,
    nó dùng để định danh cho sản phẩm này và mã code đầu tiên là id của người bán sản phẩm và mã code
    thứ hai chính là id của sản phẩm. Dưới đây ta dủng regex của python đê lấy hai mã code này.
    '''
    identifier: str  = re.search("i\.\d+.\d+", pproductURL).group(0)
    _, shop_id, product_id = identifier.split('.')
    product_reviews = []

    no_reviews = 0 # đây là trang navigation cần lấy, bắt đầu từ 0

    for no_reviews in range(10):#lấy 10 page vmt đầu tiên
        res = collect_comment(no_reviews*6, product_id, shop_id) # trả về response
        if not res:
          break# nếu như comment trả về toàn là empty thì đã hết data để crawl và API đang trả về rác
        rattings, comments = parse_comment(res) # parse nó thành comment và rating

        for comment, ratting in zip(comments, rattings): # bỏ vào kết quả tra về
            if not comment: continue # đụng đến comment rỗng thì ngừng
            product_reviews.append(Review(comment, ratting))
            
    return product_reviews



def writeToCsv(pfilePath: str, previews: list):
    """
    Hàm dùng để ghi các review object của một sản phẩm vào file csv

    Args:
        pfilePath (str): nơi lưu tập tin
        previews (list): list các review object của sản phẩm
    """
    if previews == []: return
    reviews = []

    for row in previews:
        try:
            '''Nếu comment rỗng hoặc nội dung bị admin ban thì ignore nó'''
            comment = row.icomment.strip()
            if comment == "" or comment == "****** Đánh giá đã bị ẩn do nội dung không phù hợp. ******": continue

            reviews.append((comment, row.irating))
        except:
            continue

    '''Tạo datafram và ghi ra file'''
    df = pd.DataFrame(reviews, columns=['comment', 'rating'])
    df.to_csv(pfilePath, index=False, header=True)
