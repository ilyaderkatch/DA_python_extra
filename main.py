import urllib.request
from bs4 import BeautifulSoup
import sqlite3


def generate_data(page):
    response = urllib.request.urlopen(f'https://www.anekdot.ru/release/anekdot/year/2023/{page}')
    html = response.read()
    html = html.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('div', {'class': "topicbox"})
    data = []
    for item in paragraphs:
        if item.get('id') is not None:
            id_start_rate = str(item.find('div', {'class': "rates"})).find('data-r') + 8
            str_rate = str(item.find('div', {'class': "rates"}))[id_start_rate:]
            id_end_rate = str_rate.find(';')

            id_start_com = str(item.find('div', {'class': "btn2"})).find("data-com") + 10
            str_com = str(item.find('div', {'class': "btn2"}))[id_start_com:]
            id_end_com = str_com.find('"')

            text = item.find('div', {'class': "text"}).text

            data.append((int(item.get('id')), str(text), int(str_rate[:id_end_rate]), int(str_com[:id_end_com]), len(text.split(" "))))
    return data


class DataBase:

    def __init__(self, jokes_number=0):
        self.jokes_number = jokes_number
        self.conn = sqlite3.connect("example.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('PRAGMA encoding="UTF-8";')
        self.create_table()
        page = 1
        i = 0
        while i != self.jokes_number:
            page_data = generate_data(page)
            j = 0
            while j != len(page_data) and i != self.jokes_number:
                try:
                    self.add_sequence(i, page_data[j])
                    i += 1
                    j += 1
                except:
                    j += 1
                    pass
            page += 1

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jokes (
                id_local INTEGER,
                id_page INTEGER,
                joke TEXT,
                rating INTEGER,
                num_comments INTEGER,
                num_words INTEGER
            )''')
        self.conn.commit()

    def add_sequence(self, i, seq):
        query = '''
                INSERT INTO jokes (id_local, id_page, joke, rating, num_comments, num_words) VALUES 
                    ("{}", "{}", "{}", "{}", "{}", "{}");'''
        query = query.format(i, seq[0], seq[1], seq[2], seq[3], seq[4])
        self.cursor.execute(query)

    def select_all_sequences(self):
        query = '''SELECT *
                   FROM jokes'''
        self.cursor.execute(query)

        for row in self.cursor:
            print(row)

    def delete_all_history(self):
        query = '''DROP TABLE IF EXISTS jokes'''
        self.cursor.execute(query)


if __name__ == '__main__':
    n = int(input())
    d = DataBase(n)
    d.select_all_sequences()
    d.delete_all_history()


