from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Template
from datetime import datetime
from collections import defaultdict
import pandas as pd
import os
import sys
import argparse

HTML_CONTENT = None
DATA_FILE = None
FOUNDATION_YEAR = 1920
PORT = 8000
TEMPLATE_FILE = 'template.html'


def get_year_word(years):
    last_two = years % 100
    last_one = years % 10

    if 11 <= last_two <= 19:
        return "лет"

    if last_one == 1:
        return "год"
    elif 2 <= last_one <= 4:
        return "года"
    else:
        return "лет"


def parse_arguments():
    parser = argparse.ArgumentParser(description='Сервер винодельни Розы')
    parser.add_argument('data_file', nargs='?', default='wine3.xlsx',
                        help='Путь к Excel файлу с данными (по умолчанию wine3.xlsx)')
    return parser.parse_args()


def load_products(data_file):
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Файл '{data_file}' не найден")

    df = pd.read_excel(data_file, sheet_name='Лист1')

    required_columns = ['Категория', 'Название', 'Цена', 'Картинка']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"В файле отсутствует обязательная колонка: {col}")

    products = defaultdict(list)

    for index, row in df.iterrows():
        product = {
            'name': row['Название'],
            'grape': row['Сорт'] if pd.notna(row.get('Сорт')) else '',
            'price': str(int(row['Цена'])) if pd.notna(row['Цена']) else '',
            'image': row['Картинка'] if pd.notna(row['Картинка']) else '',
            'sale': row['Акция'] if pd.notna(row.get('Акция')) else ''
        }

        products[row['Категория']].append(product)

    return dict(products)


def render_website(products, age, year_word):
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(f"Файл шаблона '{TEMPLATE_FILE}' не найден")

    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template_content = f.read()

    template = Template(template_content)
    return template.render(
        age=age,
        year_word=year_word,
        products=products
    )


def update_html_cache(data_file):
    global HTML_CONTENT

    current_year = datetime.now().year
    age = current_year - FOUNDATION_YEAR

    year_word = get_year_word(age)
    products = load_products(data_file)
    HTML_CONTENT = render_website(products, age, year_word)


class CustomHandler(SimpleHTTPRequestHandler):
    def _is_main_page(self):
        return self.path == '/' or self.path == '/index.html'

    def _handle_main_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

    def _handle_static_file(self):
        super().do_GET()

    def do_GET(self):
        if self._is_main_page():
            self._handle_main_page()
        else:
            self._handle_static_file()


def start_server():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, CustomHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


def main():
    global DATA_FILE

    args = parse_arguments()
    DATA_FILE = args.data_file

    try:
        update_html_cache(DATA_FILE)
    except (FileNotFoundError, ValueError, Exception):
        sys.exit(1)

    try:
        start_server()
    except Exception:
        sys.exit(1)


if __name__ == '__main__':
    main()