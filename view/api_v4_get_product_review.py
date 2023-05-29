import os
import datetime
import requests
import pandas as pd

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
    product_quality: int
    seller_service: int
    delivery_service: int

class ProductDetailCrawler:
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
                        product_quality=item["detailed_rating"]["product_quality"],
                        seller_service=item["detailed_rating"]["product_quality"],
                        delivery_service=item["detailed_rating"]["product_quality"]
                    )
                    self.items_list.append(item_info.dict())

        def get_item_detail(cookies, query_url):

            r2 = requests.get(query_url,cookies=cookies)
            parser_shop_html(r2.json()["data"]["ratings"])

        def main(crawler_itme_urls):

            r1 = requests.get('https://shopee.vn')
            [
                get_item_detail(r1.cookies, query_url)
                for query_url in crawler_itme_urls
                ]
                

        df_header = pd.DataFrame(
            columns=[field.name for field in ItemParams.__fields__.values()]
        )
        df_header.to_csv(self.basepath + "/csv/pdp_comment_raw.csv", index=False)

        for row in shop_detail.itertuples():
            crawler_itme_urls = []

            shop_id = row.shopid
            item_id = row.itemid
            cmt_product_count = row.cmt_count
            num = 0
            while num < cmt_product_count:
                crawler_itme_urls.append(
                    f"{self.search_item_api}?filter=0&flag=1&itemid={item_id}&limit=2&offset={str(num)}&shopid={shop_id}&type=0"
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
    crawler_product_review = ProductDetailCrawler()
    result_product_review = crawler_product_review(pdp_detail)