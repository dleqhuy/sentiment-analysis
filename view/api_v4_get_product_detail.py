import os
import datetime
import requests
import pandas as pd
from tqdm import tqdm 
from pydantic import BaseModel


class ItemParams(BaseModel):
    itemid: str
    shopid: int
    name: str
    currency: str
    stock: int
    status: int
    ctime: int
    t_ctime: str
    sold: int
    historical_sold: int
    liked_count: int
    brand: str
    cmt_count: int
    item_status: str
    price: int
    price_min: int
    price_max: int
    price_before_discount: int
    show_discount: int
    raw_discount: int
    tier_variations_option: str
    rating_star_avg: int
    rating_star_1: int
    rating_star_2: int
    rating_star_3: int
    rating_star_4: int
    rating_star_5: int
    item_type: int
    is_adult: bool
    has_lowest_price_guarantee: bool
    is_official_shop: bool
    is_cc_installment_payment_eligible: bool
    is_non_cc_installment_payment_eligible: bool
    is_preferred_plus_seller: bool
    is_mart: bool
    is_on_flash_sale: bool
    is_service_by_shopee: bool
    shopee_verified: bool
    show_official_shop_label: bool
    show_shopee_verified_label: bool
    show_official_shop_label_in_title: bool
    show_free_shipping: bool
    insert_date: str

    class Config:
        allow_extra = False


class ProductDetailCrawler:
    def __init__(self):
        self.basepath = os.path.abspath(os.path.dirname(__file__))

        self.search_item_api = "https://shopee.vn/api/v4/shop/search_items"
        self.items_list = []

        today = datetime.datetime.now()
        self.today_date = today.strftime("%Y-%m-%d %H:%M:%S")

    def __call__(self, shop_detail):
        def parser_shop_html(info):

            if info["total_count"] != 0:

                for item in info["items"]:
                    item = item["item_basic"]

                    dateArray = datetime.datetime.utcfromtimestamp(item["ctime"])
                    transfor_time = dateArray.strftime("%Y-%m-%d %H:%M:%S")

                    item_info = ItemParams(
                        **item,
                        t_ctime=transfor_time,
                        insert_date=self.today_date,
                        rating_star_avg=item["item_rating"]["rating_star"],
                        rating_star_1=item["item_rating"]["rating_count"][1],
                        rating_star_2=item["item_rating"]["rating_count"][2],
                        rating_star_3=item["item_rating"]["rating_count"][3],
                        rating_star_4=item["item_rating"]["rating_count"][4],
                        rating_star_5=item["item_rating"]["rating_count"][5],
                        tier_variations_option=",".join(
                            item["tier_variations"][0]["options"]
                        )
                        if item.get("tier_variations")
                        else "",
                    )
                    self.items_list.append(item_info.dict())

        def get_item_detail(cookies, query_url):
            r2 = requests.get(query_url,cookies=cookies)
            parser_shop_html(r2.json())

        def main(crawler_itme_urls):
            r1 = requests.get('https://shopee.vn')
            [
                get_item_detail(r1.cookies, query_url)
                for query_url in tqdm(crawler_itme_urls)
                ]
                

        df_header = pd.DataFrame(
            columns=[field.name for field in ItemParams.__fields__.values()]
        )
        df_header.to_csv(self.basepath + "/csv/pdp_detail.csv", index=False)
        
        crawler_itme_urls = []
        for row in shop_detail.itertuples():
            
            shop_id = row.shopid
            shop_product_count = row.item_count
            num = 0
            while num < shop_product_count:
                crawler_itme_urls.append(
                    f"{self.search_item_api}?offset={str(num)}&limit=100&order=desc&filter_sold_out=3&use_case=1&sort_by=sales&order=sales&shopid={shop_id}"
                )
                num += 100
                
        main(crawler_itme_urls)

        df = pd.DataFrame(self.items_list)
        df.to_csv(
            self.basepath + "/csv/pdp_detail.csv",
            index=False,
            mode="a",
            header=False,
        )
        return df


if __name__ == "__main__":
    """
    # api example
    # https://shopee.vn/api/v4/shop/search_items?filter_sold_out=1&limit=100&offset=1&order=desc&shopid=57040335&sort_by=pop&use_case=1

    params use_case:
    1: Top Product
    2: ?
    3: ?
    4: Sold out items

    params filter_sold_out:
    1: = sold_out
    2: != sold_out
    3: both

    """

    basepath = os.path.abspath(os.path.dirname(__file__))
    shop_detail = pd.read_csv(basepath + "/csv/shop_detail.csv")
    crawler_product_detail = ProductDetailCrawler()
    result_product_detail = crawler_product_detail(shop_detail)