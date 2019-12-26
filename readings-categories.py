import psycopg2
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import re



def build_connection():
    connection = psycopg2.connect(user="books_admin", password="saqib123",
                                  host="127.0.0.1", port="5432", database="books")
    print("Database connected")
    return connection


def close_connection(connection, cursor):
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


def get_all_record(table_name, cursor):
    postgreSQL_select_Query = "select * from " + table_name

    cursor.execute(postgreSQL_select_Query)
    records = cursor.fetchall()

    # print("Print each row and it's columns values")
    # for row in records:
    #     print("Id = ", row[0], "\n")
    #     print("name = ", row[1], "\n")
    #     print("url  = ", row[2], "\n")
    #     print("total_books  = ", row[3], "\n\n")

    return records


def insert_category_record(cat_id, name, url, total_books, cursor):
    postgres_insert_query = """ INSERT INTO category (id, name, url, total_books) VALUES (%s,%s,%s,%s)"""
    record_to_insert = (cat_id, name, url, total_books)
    cursor.execute(postgres_insert_query, record_to_insert)


def delete_category_record(cat_id, cursor):
    sql_delete_query = """Delete from category where id = %s"""
    cursor.execute(sql_delete_query, cat_id)


def insert_book_record(name, url, price, availability, publisher, cover, pages, isbn, author, cursor):
    postgres_insert_query = """ INSERT INTO book_details (name, url, price, available, publisher,
                                cover, pages, isbn, author) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    record_to_insert = (name, url, price, availability, publisher, cover, pages, isbn, author)
    cursor.execute(postgres_insert_query, record_to_insert)


def break_string(temp_str, deli):
    data = temp_str.split(deli, 1)
    return data


def scrap_all_categories(url, cursor, connection):
    page = urlopen(url).read()
    _div = soup(page, 'html.parser').find('div', {'class': 'categories_listings'})
    ul = _div.find('ul')
    li = ul.find_all('li')
    index = 1
    for a in li:
        temp = break_string(a.get_text(), '[')
        print(index, temp[0], url + a.find('a').get('href', ''), temp[1][:-1])
        # insert_category_record(index, temp[0], url + a.find('a').get('href', ''), temp[1][:-1], cursor)
        index += 1
    connection.commit()


def get_each_book_on_page(url, site_url, cursor, connection):
    availability = False
    page = urlopen(url).read()
    table = soup(page, 'html.parser').findChild('table', {'id': 'ContentPlaceHolder1_DL_Books'})
    for row in table:
        td = row.find('td')
        if td != -1:
            if td.find('div', {'class': 'book_availability'}):
                availability = True
            else:
                availability = False
            price_info = td.find('div', {'class': 'our_price'})
            price_ = price_info.get_text().rsplit('.', 1)
            price = price_[1]
            print('Price:   ', price)
            if price == "":
                price = '-'

            div1 = td.find('div', {'class': 'product_detail_page_left_colum_author_name'})
            h5 = div1.find('h5')
            data = break_string(h5.get_text(), '[')

            name = data[0]
            print('Name:    ', name, '\n')
            if name == "":
                name = '-'

            url_book = site_url + '/' + h5.find('a').get('href', '')
            print('URL:     ', url_book, '\n')
            if url_book == "":
                url_book = '-'

            cover = data[1]
            print('Cover:   ', cover.strip()[:-1], '\n')
            if cover == "":
                cover = '-'

            author = div1.find('h6').get_text()
            print('Author:  ', author.strip())
            if author == "":
                author = '-'

            div2 = td.find('div', {'class': 'books_publisher'})
            h6 = div2.find('h6')
            publisher = h6.find('a').get_text().strip()
            print('Publisher:   ', publisher)
            if publisher == "":
                publisher = '-'

            m = re.search('ISBN:\s+(.+?)\s+|\s+Pages:\s(.+?)', h6.get_text())
            isbn = m.group(1)
            print('ISBN:    ', isbn)
            if isbn == "":
                isbn = '-'

            span = div2.find('span', {'class': 'pages'})
            print('No. of Pages:    ', span.get_text())
            pages = span.get_text()
            if pages == "":
                pages = '-'
            insert_book_record(name.strip(), url_book.strip(), price.strip(), availability, publisher.strip(),
                               cover.strip(), pages.strip(), isbn.strip(), author.strip(), cursor)
            connection.commit()
            print('================')


def scrap_all_books(categories, site_url, cursor, connection):
    for category in categories:
        page = urlopen(category[2]).read()
        if int(category[3]) > 10:
            li_last_page = soup(page, 'html.parser').find('li', {'class': 'pagination_last'})
            a_last_page = li_last_page.find('a')
            if a_last_page.get_text() == 'Last':
                # print('href last page: ', a_last_page.get('href', ''))
                last_page_url = a_last_page.get('href', '')
                last_page = last_page_url.rsplit('=', 1)
                x = 1
                while x <= int(last_page[1]):
                    print("LOOP", x)
                    # print(category[2] + '&Page=' + str(x))'
                    print(category[2] + '&Page=' + str(x))
                    #get_each_book_on_page(category[2] + '&Page=' + str(x), site_url, cursor, connection)
                    x += 1

            else:  # For categories having less then 11 books.
                print("")
                #get_each_book_on_page(category[2], site_url, cursor, connection)


def main():
    connection = build_connection()
    cursor = connection.cursor()
    url = 'https://www.readings.com.pk'
    '''Already added the categories in database. running again might cause crash.'''
    #scrap_all_categories(url, cursor, connection)

    categories = get_all_record('category', cursor)
    scrap_all_books(categories, url, cursor, connection)

    close_connection(connection, cursor)


if __name__ == "__main__":
    main()
