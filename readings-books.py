# import psycopg2
# from bs4 import BeautifulSoup as soup
# from urllib.request import urlopen
# import re
# import time
# import csv
# import logging
#
#
# def build_connection(logger):
#     try:
#         connection = psycopg2.connect(user="", password="",
#                                       host="127.0.0.1", port="", database="")
#         print("Database connected")
#         logger.info('Database connected')
#     except:
#         logger.critical('Database not connected')
#         print("Database not connected")
#     return connection
#
#
# def close_connection(connection, cursor):
#     if connection:
#         cursor.close()
#         connection.close()
#         print("PostgreSQL connection is closed")
#
#
# def get_all_record(table_name, cursor):
#     postgreSQL_select_Query = "select * from " + table_name
#
#     cursor.execute(postgreSQL_select_Query)
#     records = cursor.fetchall()
#     return records
#
#
# def insert_category_record(cat_id, name, url, total_books, cursor, logger):
#     postgres_insert_query = """ INSERT INTO category (id, name, url, total_books) VALUES (%s,%s,%s,%s)"""
#     try:
#         record_to_insert = (cat_id, name, url, total_books)
#         cursor.execute(postgres_insert_query, record_to_insert)
#     except:
#         logger.warning('Category already exist: ', name, '\n')
#         print('This category already exist: ', name, '\n')
#
#
# def delete_category_record(cat_id, cursor):
#     sql_delete_query = """Delete from category where id = %s"""
#     cursor.execute(sql_delete_query, cat_id)
#
#
# def insert_book_record(name, url, price, availability, publisher, cover, pages, isbn, author, cursor, logger):
#     postgres_insert_query = """ INSERT INTO book_details (name, url, price, available, publisher,
#                                 cover, pages, isbn, author) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
#     try:
#         record_to_insert = (name, url, price, availability, publisher, cover, pages, isbn, author, '0')
#         cursor.execute(postgres_insert_query, record_to_insert)
#     except:
#         logger.warning('Book already exist: ', name, url, isbn, '\n')
#         print('This book already exist: ', name, url, price, availability, publisher, cover, pages, isbn, author, '\n')
#
#
# def break_string(temp_str, deli):
#     data = temp_str.split(deli, 1)
#     return data
#
#
# def scrap_all_categories(url, cursor, connection, logger):
#     page = urlopen(url).read()
#     _div = soup(page, 'html.parser').find('div', {'class': 'categories_listings'})
#     ul = _div.find('ul')
#     li = ul.find_all('li')
#     index = 1
#     for a in li:
#         temp = break_string(a.get_text(), '[')
#         insert_category_record(index, temp[0], url + a.find('a').get('href', ''), temp[1][:-1], cursor, logger)
#         index += 1
#     connection.commit()
#
#
# def get_each_book_on_page(url, site_url, cursor, connection, logger):
#     availability = False
#     page = urlopen(url).read()
#     table = soup(page, 'html.parser').findChild('table', {'id': 'ContentPlaceHolder1_DL_Books'})
#     for row in table:
#         td = row.find('td')
#         if td != -1:
#             if td.find('div', {'class': 'book_availability'}):
#                 availability = True
#             else:
#                 availability = False
#             price_info = td.find('div', {'class': 'our_price'})
#             price_ = price_info.get_text().rsplit('.', 1)
#             price = price_[1]
#             if price == "":
#                 price = '-'
#
#             div1 = td.find('div', {'class': 'product_detail_page_left_colum_author_name'})
#             h5 = div1.find('h5')
#             data = break_string(h5.get_text(), '[')
#
#             name = data[0]
#             if name == "":
#                 name = '-'
#
#             url_book = site_url + '/' + h5.find('a').get('href', '')
#             if url_book == "":
#                 url_book = '-'
#
#             cover = data[1]
#             if cover == "":
#                 cover = '-'
#
#             author = div1.find('h6').get_text()
#             if author == "":
#                 author = '-'
#
#             div2 = td.find('div', {'class': 'books_publisher'})
#             h6 = div2.find('h6')
#             publisher = h6.find('a').get_text().strip()
#             if publisher == "":
#                 publisher = '-'
#
#             m = re.search('ISBN:\s+(.+?)\s+|\s+Pages:\s(.+?)', h6.get_text())
#             isbn = m.group(1)
#             if isbn == "":
#                 isbn = '-'
#
#             span = div2.find('span', {'class': 'pages'})
#             pages = span.get_text()
#             if pages == "":
#                 pages = '-'
#             insert_book_record(name.strip(), url_book.strip(), price.strip(), availability, publisher.strip(),
#                                cover.strip(), pages.strip(), isbn.strip(), author.strip(), cursor, logger)
#             connection.commit()
#
#
# def scrap_all_page_urls(categories, site_url, cursor, connection):
#     count = 0
#     with open('page_urls.csv', mode='w') as page_url_file:
#         page_urls = csv.writer(page_url_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         for category in categories:
#             page = urlopen(category[2]).read()
#             cat_num = re.match('^.+Category=(\d+).+$', category[2])
#             category_no = cat_num.group(1)
#             if int(category[3]) > 10:
#                 li_last_page = soup(page, 'html.parser').find('li', {'class': 'pagination_last'})
#                 a_last_page = li_last_page.find('a')
#
#                 if a_last_page.get_text() == 'Last':
#                     last_page_url = a_last_page.get('href', '')
#                     last_page = last_page_url.rsplit('=', 1)
#                     x = 1
#                     while x <= int(last_page[1]):
#                         page_urls.writerow([category[2] + '&Page=' + str(x), '', '0', x, category_no])
#                         count += 1
#                         x += 1
#
#             else:  # For categories having less then 11 books.
#                 page_urls.writerow([category[2] + '&Page=' + str(x), '', '0', -1, category_no])
#
#     print("Total number of links: ", count)
#
#
# def get_page_urls_for_books(url, cursor, connection, logger):
#     with open('page_urls.csv', mode='r') as page_url_file:
#         rows = csv.reader(page_url_file, delimiter=',')
#         for row in rows:
#             if len(row) > 0:
#                 print(row[0], '\n')
#
#                 if row[3] != '-1':
#                     url_page = 'https://www.readings.com.pk/pages/category.aspx?Category=' + row[4] + \
#                                '&Level=Level1&BookType=N&Page=' + row[3]
#                 else:
#                     url_page = 'https://www.readings.com.pk/pages/category.aspx?Category=' + row[4] + \
#                                '&Level=Level1&BookType=N'
#
#                 get_each_book_on_page(url_page, url, cursor, connection, logger)
#
#
# def main():
#     logging.basicConfig(filename='readings.log',
#                         format='%(asctime)s %(message)s',
#                         filemode='w')
#
#     logger = logging.getLogger()
#
#     logger.setLevel(logging.INFO)
#
#     # logger.error("Database connected")
#
#     connection = build_connection(logger)
#     cursor = connection.cursor()
#     # url = 'https://www.readings.com.pk'
#     '''Already added the categories in database. running again might cause crash.'''
#     start_time = time.time()
#     '''Getting all categories from readings.com.pk and inserting into database.'''
#     # scrap_all_categories(url, cursor, connection)
#
#     '''Getting all categories from database.'''
#     # categories = get_all_record('category', cursor)
#
#     '''Getting all pages and categories urls and adding them in page_urls.csv.'''
#     # scrap_all_page_urls(categories, url, cursor, connection)
#
#     '''Getting all books on each page url(page_urls.csv) from reading.com.pk and adding it to database.'''
#     # get_page_urls_for_books(url, cursor, connection, logger)
#
#     end_time = time.time()
#
#     logger.info((end_time - start_time) / 60)
#     close_connection(connection, cursor)
#
#
# if __name__ == "__main__":
#     main()
