from view.api_v4_get_shop_detail import ShopDetailCrawler
from view.api_v4_get_product_detail import ProductDetailCrawler
from view.api_v4_get_product_review import ProductReviewCrawler


import logging

logger = logging.getLogger(__name__)


class Crawler:
    def __init__(self, user_list):
        self.input_shop_names = user_list

    def __call__(self):


        # Step 1 > input shop_names > get shop_detail
        print(f"⌲ Step 1: Total shop detail fetchedd:")
        crawler_shop_detail = ShopDetailCrawler()
        result_shop_detail = crawler_shop_detail(self.input_shop_names)

        # Step 2 > input shop_detail > get product_id
        print(f"⌲ Step 2: Total pdp detail fetched:")
        crawler_product_detail = ProductDetailCrawler()
        result_product_detail = crawler_product_detail(result_shop_detail)

        # Step 2 > input shop_detail > get product_id
        print(f"⌲ Step 3: Total pdp review fetched:")
        crawler_product_review = ProductReviewCrawler()
        result_product_review = crawler_product_review(result_product_detail)

if __name__ == "__main__":

    # Insert your email and the shop names you want to crawl
    user_list = [
        "rosi_accessories"
        
    ]

    do = Crawler(user_list)
    do()