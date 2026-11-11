import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# Hàm lấy danh sách các đường dẫn sách từ một trang danh mục
def get_book_links(page_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(page_url, headers=headers)
    response.encoding='utf-8'
    
    # TODO: Kiểm tra status code của response, nếu không phải 200 thì return list rỗng
    if response.status_code!=200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    book_links = []
    
    # TODO: Sử dụng BeautifulSoup để tìm tất cả các thẻ chứa đường dẫn đến trang chi tiết sách
    # Gợi ý: Các cuốn sách thường nằm trong thẻ <article class="product_pod"> -> <h3> -> <a>
    articles=soup.find_all('article', class_='product_pod')
    
    # TODO: Nối đường dẫn tương đối (ví dụ: 'a-light-in-the-attic_1000/index.html') 
    # với domain gốc ('http://books.toscrape.com/catalogue/') để tạo URL hoàn chỉnh và thêm vào book_links
    for article in articles:
        h3=article.find('h3')
        if h3 and h3.find('a'):
            rel_url=h3.find('a').get('href', '').replace('../', '')
            if rel_url.startswith('catalogue/'):
                full_url=f"http://books.toscrape.com/{rel_url}"
            else:
                full_url=f"http://books.toscrape.com/catalogue/{rel_url}"
            book_links.append(full_url)
    
    return book_links

# Hàm trích xuất thông tin chi tiết của 1 cuốn sách
def get_book_details(book_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(book_url, headers=headers)
    response.encoding='utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Khởi tạo dictionary chứa dữ liệu mặc định
    book_data = {
        'URL': book_url,
        'Title': None,
        'Price': None,
        'Availability': None,
        'Description': None,
        'UPC': None,
        'Product_Type': None
    }
    
    try:
        # TODO: Trích xuất Tiêu đề sách (Thẻ <h1>)
        book_data['Title']=soup.find('h1').text.strip() if soup.find('h1') else ""
        
        # TODO: Trích xuất Giá bán (Thẻ <p class="price_color">)
        book_data['Price']=soup.find('p', class_='price_color').text.strip() if soup.find('p', class_='price_color') else ""
        
        # TODO: Trích xuất Tình trạng kho (Thẻ <p class="instock availability">)
        book_data['Availability']=" ".join(soup.find('p', class_='instock availability').text.split()) if soup.find('p', class_='instock availability') else ""
        
        # TODO: Trích xuất Mô tả sản phẩm
        # Gợi ý: Thẻ <p> nằm ngay sau thẻ <div id="product_description">
        desc_elem=soup.find('div', id='product_description')
        book_data['Description']=desc_elem.find_next_sibling('p').text.strip() if desc_elem and desc_elem.find_next_sibling('p') else ""
        
        # TODO: Trích xuất các thông tin trong bảng Product Information (UPC, Product Type,...)
        # Gợi ý: Tìm thẻ <table> -> duyệt qua các thẻ <tr> -> kiểm tra <th> để lấy <td> tương ứng
        table=soup.find('table', class_='table-striped')
        if not table:
            table=soup.find('table')
        if table:
            for row in table.find_all('tr'):
                th=row.find('th')
                td=row.find('td')
                if th and td:
                    header=th.text.strip()
                    val=td.text.strip()
                    if header=='UPC':
                        book_data['UPC']=val
                    elif header=='Product Type':
                        book_data['Product_Type']=val
                    elif header=='Price (excl. tax)':
                        book_data['Price (excl. tax)']=val
                    elif header=='Price (incl. tax)':
                        book_data['Price (incl. tax)']=val
                    elif header=='Tax':
                        book_data['Tax']=val
                    elif header=='Availability' and not book_data['Availability']:
                        book_data['Availability']=" ".join(val.split())
                    elif header=='Number of reviews':
                        book_data['Number of reviews']=val
        
    except Exception as e:
        print(f"Lỗi khi cào dữ liệu tại {book_url}: {e}")
        
    return book_data

# Hàm main điều phối toàn bộ chương trình
def main():
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    all_books_data = []
    
    # Duyệt qua các trang từ 1 đến 50
    # TODO: Thay đổi range từ 1 đến 3 để test trước khi chạy thật 50 trang
    for page_num in range(1, 51):
        print(f"Đang thu thập đường dẫn tại trang {page_num}...")
        page_url = base_url.format(page_num)
        
        links = get_book_links(page_url)
        
        for link in links:
            print(f"  -> Đang bóc tách chi tiết: {link}")
            details = get_book_details(link)
            all_books_data.append(details)
            
            # Tạm nghỉ ngẫu nhiên từ 1 đến 2 giây để tránh bị chặn
            time.sleep(random.uniform(1, 2))
            
    # Chuyển đổi list dictionary sang DataFrame
    df = pd.DataFrame(all_books_data)
    
    # TODO: Lưu DataFrame ra file CSV với tên 'books_data.csv' (nhớ thiết lập index=False, encoding='utf-8')
    df.to_csv('books_data.csv', index=False, encoding='utf-8')
    
    print("Hoàn thành! Đã lưu dữ liệu ra file books_data.csv")

if __name__ == "__main__":
    main()
