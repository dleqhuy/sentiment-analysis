import os
import datetime
import requests
import pandas as pd

from pydantic import BaseModel


class ShopParams(BaseModel):
    shop_created: str
    insert_date: str
    shopid: int
    name: str
    username: str
    follower_count: int
    has_decoration: bool
    item_count: int
    response_rate: int
    campaign_hot_deal_discount_min: int
    rating_star: float
    shop_rating_good: int
    shop_rating_bad: int
    shop_rating_normal: int
    # description: str

    class Config:
        allow_extra = False


class ShopDetailCrawler:
    def __init__(self):
        self.basepath = os.path.abspath(os.path.dirname(__file__))
        self.shop_detail_api = "https://shopee.vn/api/v4/shop/get_shop_base?entry_point=ShopByPDP&need_cancel_rate=true&request_source=shop_home_page&version=1&username="
        self.shop_detail = []

        today = datetime.datetime.now()
        self.today_date = today.strftime("%Y-%m-%d %H:%M:%S")

    def __call__(self, input_shop_names):
        def parser_shop_html(html):
            shop = html["data"]
            dateArray = datetime.datetime.utcfromtimestamp(shop["ctime"])
            transfor_time = dateArray.strftime("%Y-%m-%d %H:%M:%S")

            shop_info = ShopParams(
                **shop,
                username=shop["account"]["username"],
                shop_created=transfor_time,
                insert_date=self.today_date,
                shop_rating_good=shop["shop_rating"]["rating_good"],
                shop_rating_bad=shop["shop_rating"]["rating_bad"],
                shop_rating_normal=shop["shop_rating"]["rating_normal"],
            )
            self.shop_detail.append(shop_info.dict())

        def get_shop_detail(cookies, query_url):
            r2 = requests.get(query_url,cookies=cookies)
            parser_shop_html(r2.json())

        def main(crawler_shop_urls):
            
            r1 = requests.get('https://shopee.vn')
            [get_shop_detail(r1.cookies,query_url)
            for query_url in crawler_shop_urls
                ]

        crawler_shop_urls = []
        for num in range(len(input_shop_names)):
            crawler_shop_urls.append(self.shop_detail_api + str(input_shop_names[num]))
        main(crawler_shop_urls)

        df = pd.DataFrame(self.shop_detail)
        df.to_csv(self.basepath + "/csv/shop_detail.csv", index=False)
        return df


if __name__ == "__main__":
    """
    api example
    https://shopee.vn/api/v4/shop/get_shop_base?entry_point=ShopByPDP&need_cancel_rate=true&request_source=shop_home_page&version=1&username=rosi_accessories
    """
    input_shop_names = [
        "rosi_accessories",
    ]

    do = ShopDetailCrawler()
    result = do(input_shop_names)