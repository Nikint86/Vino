from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Template
from datetime import datetime
from collections import defaultdict
import pandas as pd
import os


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


def load_products():
    if not os.path.exists('wine3.xlsx'):
        print("wine3.xlsx не найден, использую тестовые данные")
        return get_test_data()

    try:
        df = pd.read_excel('wine3.xlsx', sheet_name='Лист1')
    except FileNotFoundError:
        print("wine3.xlsx не найден при чтении, использую тестовые данные")
        return get_test_data()
    except Exception as e:
        print(f"Ошибка при чтении Excel файла: {e}")
        return get_test_data()

    products = defaultdict(list)

    for index, row in df.iterrows():
        product = {
            'name': row['Название'],
            'grape': row['Сорт'] if pd.notna(row['Сорт']) else '',
            'price': str(int(row['Цена'])) if pd.notna(row['Цена']) else '',
            'image': row['Картинка'] if pd.notna(row['Картинка']) else '',
            'sale': row['Акция'] if pd.notna(row['Акция']) else ''
        }

        products[row['Категория']].append(product)

    print(f"✅ Загружено товаров: {sum(len(v) for v in products.values())}")
    for category, items in products.items():
        sale_count = sum(1 for item in items if item['sale'])
        print(f"   {category}: {len(items)} (акций: {sale_count})")

    return dict(products)


def get_test_data():
    return {
        "Белые вина": [
            {"name": "Кокур", "grape": "Кокур", "price": "450", "image": "kokur.png", "sale": ""},
            {"name": "Ркацители", "grape": "Ркацители", "price": "499", "image": "rkaciteli.png", "sale": ""},
            {"name": "Белая леди", "grape": "Дамский пальчик", "price": "399", "image": "belaya_ledi.png",
             "sale": "Выгодное предложение"}
        ],
        "Красные вина": [
            {"name": "Черный лекарь", "grape": "Качич", "price": "399", "image": "chernyi_lekar.png", "sale": ""},
            {"name": "Киндзмараули", "grape": "Саперави", "price": "550", "image": "kindzmarauli.png", "sale": ""},
            {"name": "Хванчкара", "grape": "Александраули", "price": "550", "image": "hvanchkara.png", "sale": ""}
        ],
        "Напитки": [
            {"name": "Коньяк классический", "grape": "", "price": "350", "image": "konyak_klassicheskyi.png",
             "sale": ""},
            {"name": "Чача", "grape": "", "price": "299", "image": "chacha.png", "sale": "Выгодное предложение"},
            {"name": "Коньяк кизиловый", "grape": "", "price": "350", "image": "konyak_kizilovyi.png", "sale": ""}
        ]
    }


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            current_year = datetime.now().year
            foundation_year = 1920
            age = current_year - foundation_year

            year_word = get_year_word(age)

            products = load_products()

            try:
                with open('template.html', 'r', encoding='utf-8') as f:
                    template_content = f.read()
            except FileNotFoundError:
                print("template.html не найден")
                self.send_error(404, "template.html not found")
                return

            template = Template(template_content)
            rendered_html = template.render(
                age=age,
                year_word=year_word,
                products=products
            )

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(rendered_html.encode('utf-8'))

            return

        super().do_GET()


if __name__ == '__main__':
    server_address = ('0.0.0.0', 8000)
    httpd = HTTPServer(server_address, CustomHandler)


    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Сервер остановлен")