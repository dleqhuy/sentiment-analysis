from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import time
import re
import requests
from selenium.webdriver.chrome.options import Options
from typing import List, Tuple
def waitPageLoaded(pdriver):
    '''
    Vì các trang product landing page dc thiết kế dưới dạng dynamic site (tức
    data dc load lên dựa vào các javascript event khi người dùng có sự tương
    tác), và các comment chỉ hiển thị khi user lăn chuột đến phần comment, nên
    hàm này giúp giả lập làm điều này.
    '''
    '''Trong 5s, đợi logo shopee hiện lên'''
    time.sleep(5)

    '''Chiều cao cũ của trang'''    
    old_height = 0

    '''Chiều cao mà trang có thể lăn đến ở thời điểm hiện tại'''
    total_height = int(pdriver.execute_script("return document.body.scrollHeight"))
    '''Scroll đến chiều cao mà trang đã load dc'''
    for i in range(1, total_height, 100):
      pdriver.execute_script("window.scrollTo(0, {});".format(i))

def find_number(text:str):
    """
    Hàm này dùng để lấy số lượng bán

    Args:
        text (str): số lượng bán của mặt hàng VD:28k
    Returns:
        num: số lượng bán của mặt hàng chuyển thành số VD 28000
    """
    if text=='':
      sell_number=np.nan
    else:
      text=text.split()
      sell_number=text[2]
      if "k" in sell_number:
        sell_number=sell_number.replace('k','000')
        sell_number=sell_number.replace(',','')
      sell_number=int(sell_number)
    return sell_number
def getURLsSearch(keyword: str):
    """
    Hàm này dùng để lấy urls theo keyword

    Args:
        keyword (str): keyword của nhóm mặt hàng cần lấy
    Returns:
        (str): chuổi url của các keyword
    """
    keyword=keyword.strip().lower().replace(" ", "%20")
    keyword_url= 'https://shopee.vn/search?keyword='+ str(keyword)+'&page='
    return keyword_url
    

def getProductURLs(purl: str, prange: tuple, pcssSelector: str):
    """
    Hàm này dùng để lấy tất cả các product's urls thỏa pcssSelector

    Args:
        purl (str): trang chính của nhóm mặt hàng cần lấy
        prange (tuple): một tuple (a, b) là số trang chứa các gallary product của shopee
        pcssSelector (str): CSS selector

    Returns:
        (list[str]): chuổi các url và số lượng bán của các product
    """
    '''Chọn driver để crawl data là Firefox'''
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/bin/chromedriver',options = chrome_options)    
    '''Dùng để lưu các hyperlink đến các product's page'''
    product_info = []
    '''Đi từ trang 0 đến 99 (UI là 1 đến 100)'''
    for i in range(prange[0], prange[1]):
        url = f"{purl}{i}" # access vào trang thứ i
        driver.get(url) # mở Firefox để access vào `url`
        
        '''đi đến cuối trang '''
        waitPageLoaded(driver)
        '''Lấy các href values từ tất cả thẻ anchor thỏa `pcssSelector`'''
        items = driver.find_elements(by=By.CLASS_NAME, value=pcssSelector)
        for it in (items):
          try:
            sell_number_product = it.find_element(By.CSS_SELECTOR,'[class="r6HknA"]').text
            sell_number_product = find_number(sell_number_product)
            new_product_urls = it.find_element(by=By.CSS_SELECTOR,value='a').get_attribute("href")
            
          except:
            sell_number_product = np.nan
            new_product_urls = np.nan

          product_info.append((new_product_urls,sell_number_product)) # thêm vào kết quả trả về
          
    '''Đóng Firefox'''
    driver.close()
    driver.quit()
    
    return product_info
            
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
            ('limit', '20'),
            ('offset', ppage),
            ('shopid', pshopID),
            ('type', '0'))

        ''' Gửi một request đến API và nhận về response '''
        response = requests.get('https://shopee.vn/api/v2/item/get_ratings', params=params)
        return response.json().get('data').get('ratings')
    
    
    '''
      Mỗi một URL sản phẩm nếu bạn chú ý sẽ có một thành phần là `i.0284272429.2342427424` như thế này,
    nó dùng để định danh cho sản phẩm này và mã code đầu tiên là id của người bán sản phẩm và mã code
    thứ hai chính là id của sản phẩm. Dưới đây ta dủng regex của python đê lấy hai mã code này.
    '''
    identifier: str  = re.search("i\.\d+.\d+", pproductURL).group(0)
    _, shop_id, product_id = identifier.split('.')
    product_reviews = []
    rattings =  []
    comments =  []

    no_reviews = 0 # đây là trang navigation cần lấy, bắt đầu từ 0

    while True:
        res = collect_comment(no_reviews, product_id, shop_id) # trả về response
        i = 1
        for i, rating in enumerate(res, 1):
          rattings.append(rating["rating_star"])
          comments.append(rating["comment"])
        
        if i % 20:
            break
            
        no_reviews += 20
        
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
