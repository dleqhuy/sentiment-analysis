import os
import datetime
import requests
import pandas as pd

from tqdm import tqdm 
from pydantic import BaseModel

class ItemParams(BaseModel):
    orderid: str
    itemid: str
    cmtid: str
    ctime: int
    t_ctime: str
    rating: int
    comment: str
    rating_star:int
    mtime: int
    t_mtime: str
    insert_date: str


class ProductReviewCrawler:
    def __init__(self):
        self.basepath = os.path.abspath(os.path.dirname(__file__))

        self.search_item_api = "https://shopee.vn/api/v4/item/get_ratings"
        self.items_list = []

        today = datetime.datetime.now()
        self.today_date = today.strftime("%Y-%m-%d %H:%M:%S")

    def __call__(self, shop_detail):
        def parser_shop_html(info):

            if info != None:
            
                for item in info:

                    ctime = datetime.datetime.utcfromtimestamp(item["ctime"])
                    mtime = datetime.datetime.utcfromtimestamp(item["mtime"])

                    transfor_ctime = ctime.strftime("%Y-%m-%d %H:%M:%S")
                    transfor_mtime = mtime.strftime("%Y-%m-%d %H:%M:%S")
                    item_info = ItemParams(
                        **item,
                        t_ctime=transfor_ctime,
                        t_mtime=transfor_mtime,
                        insert_date=self.today_date,

                    )
                    self.items_list.append(item_info.dict())

        def get_item_detail(cookies, query_url):

            r2 = requests.get(query_url,cookies=cookies)
            parser_shop_html(r2.json()["data"]["ratings"])

        def main(crawler_itme_urls):

            r1 = requests.get('https://shopee.vn')
            [
                get_item_detail(r1.cookies, query_url)
                for query_url in tqdm(crawler_itme_urls)
                ]
                

        df_header = pd.DataFrame(
            columns=[field.name for field in ItemParams.__fields__.values()]
        )
        df_header.to_csv(self.basepath + "/csv/pdp_comment_raw.csv", index=False)
        
        crawler_itme_urls = []

        for row in shop_detail.itertuples():

            shop_id = row.shopid
            item_id = row.itemid
            cmt_product_count = row.cmt_count
            num = 0
            while num < cmt_product_count:
                crawler_itme_urls.append(
                    f"{self.search_item_api}?filter=0&flag=1&itemid={item_id}&limit=50&offset={str(num)}&shopid={shop_id}&type=0"
                )
                num += 50
        main(crawler_itme_urls)

        df = pd.DataFrame(self.items_list)
        df.to_csv(
            self.basepath + "/csv/pdp_comment_raw.csv",
            index=False,
            mode="a",
            header=False,
        )
        return df


if __name__ == "__main__":
    """
    # api example
    # https://shopee.vn/api/v4/item/get_ratings?filter=0&flag=1&itemid=8675108155&limit=2&offset=50&shopid=57040335&type=0

    """

    basepath = os.path.abspath(os.path.dirname(__file__))
    pdp_detail = pd.read_csv(basepath + "/csv/pdp_detail.csv")
    pdp_detail = pdp_detail[pdp_detail['cmt_count'] > 0]
    crawler_product_review = ProductReviewCrawler()
    result_product_review = crawler_product_review(pdp_detail)