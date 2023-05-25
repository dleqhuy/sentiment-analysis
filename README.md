# Phân tích sắc thái đánh giá các mặt hàng trên Shopee

Đánh giá và nhận xét do người mua cho một sản phẩm là một thông tin quan trọng đối với đối tác điện tử lớn như Shopee. Những đánh giá sản phẩm này giúp người bán hiểu nhu cầu của khách hàng và nhanh chóng điều chỉnh các dịch vụ của mình để mang lại trải nghiệm tốt hơn cho khách hàng trong đơn hàng tiếp theo. Nhận xét của người dùng cho một sản phẩm bao gồm các khía cạnh như dịch vụ giao hàng, đóng gói sản phẩm, chất lượng sản phẩm, thông số sản phẩm, phương thức thanh toán, v.v. Vì vậy một hệ thống chính xác để hiểu những đánh giá này có tác động lớn đến toàn bộ Shopee trải nghiệm người dùng.

## Mục tiêu 
Mục tiêu của repo này bao gồm  
1. Thu thập dữ liệu từ sàn thương mại điện tử Shopee 
2. Xử lí dữ liệu và gán nhãn
3. Huấn luyện mô hình phân tích sắc thái đánh giá sản phẩm trên Shopee bằng PhoBert 
4. Đánh giá độ chính xác dựa trên các metrics accuracy, precision, recall, và F1-score

## Tiền xử lý dữ liệu

Đối với dữ liệu thô, ta sẽ lần lượt làm sạch, chuẩn hoá và gán nhãn. Sau khi xoá bỏ dữ liệu trùng lắp, các dữ liệu hữu ích và chứa thông tin chỉ bao gồm hơn 8000 mẫu dữ liệu

Các bước bao gồm: Lowercasing comments >> Removing comments containing URL >> Removing special characters >> Removing non-Vietnamese >> Removing stop-words