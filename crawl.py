import pandas as pd
from modules import crawler
from modules import utils

my_pham = {'chăm sóc da':
           {'sửa rửa mặt','lotion','kem duõng ẩm',
            'mặt nạ','toner','nước hoa hồng',
            'bông tẩy trang','nước tẩy trang','mụn',
            'trị mụn','kem trị mụn','thâm',
            'trị thâm','kem trị thâm','bỏng',
            'phỏng','sẹo','kem trị sẹo','vitamic c',
            'cấp ẩm','xịt khoáng','lột mụn','son dưỡng',}}


for pr in my_pham['chăm sóc da']:

  URLsSearch = crawler.getURLsSearch(pr)
  #crawl từ trang 1 đến 2
  product_info = (crawler.getProductURLs(URLsSearch,[0, 1], "shopee-search-item-result__item"))
  #tạo DataFrame
  product_info = pd.DataFrame(product_info,columns=['product_urls','sell_number'])
  #ghi ra csv
  product_info.to_csv(f"/content/drive/MyDrive/shopee/product_info/{pr}.csv",index=False)


infos = utils.readCSVfromfolder('/content/drive/MyDrive/shopee/product_info/')

for idx, product_url in enumerate(infos['product_urls']): # đi qua từng URL của sản phẩm
    new_reviews = crawler.getProductReviewsAPI(product_url) # lấy tất cả review của sản phẩm này
    crawler.writeToCsv(f"/content/drive/MyDrive/shopee/product_reviews/product_{idx}.csv", new_reviews) # ghi mọi review của sản phẩm này ra file

reviews = utils.readCSVfromfolder('/content/drive/MyDrive/shopee/product_reviews/')
