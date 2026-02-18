from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Template
from datetime import datetime
from collections import defaultdict
import pandas as pd
import os
import sys
import argparse

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

def load_products():
    if not os.path.exists('wine3.xlsx'):
        raise FileNotFoundError("Файл wine3.xlsx не найден")

    df = pd.read_excel('wine3.xlsx', sheet_name='Лист1')

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
    with open('template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()

    template = Template(template_content)
    return template.render(
        age=age,
        year_word=year_word,
        products=products
    )


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


HTML_CONTENT = None
DATA_FILE = None

def update_html_cache():
    global HTML_CONTENT

    current_year = datetime.now().year
    foundation_year = 1920
    age = current_year - foundation_year

    year_word = get_year_word(age)
    products = load_products()
    HTML_CONTENT = render_website(products, age, year_word)


def start_server(port=8000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CustomHandler)


    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Сервер остановлен")
        sys.exit(0)


def main():
    global DATA_FILE


    args = parse_arguments()
    DATA_FILE = args.data_file

    try:
        update_html_cache()
    except FileNotFoundError as e:
        print(f"Критическая ошибка: {e}")
        print("Убедитесь, что файл существует в папке с проектом")
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка в данных: {e}")
        print("   Проверьте структуру Excel файла")
        sys.exit(1)
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        sys.exit(1)

    try:
        start_server()
    except Exception as e:
        print(f"Ошибка при запуске сервера: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()