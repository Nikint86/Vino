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
    try:
        df = pd.read_excel('wine2.xlsx', sheet_name='Лист1')

        products = defaultdict(list)

        for index, row in df.iterrows():
            product = {
                'name': row['Название'],
                'grape': row['Сорт'] if pd.notna(row['Сорт']) else '',
                'price': str(int(row['Цена'])) if pd.notna(row['Цена']) else '',
                'image': row['Картинка'] if pd.notna(row['Картинка']) else ''
            }

            products[row['Категория']].append(product)

        for category, items in products.items():
            print(f"   {category}: {len(items)}")

        return dict(products)

    except FileNotFoundError:
        print("wine2.xlsx не найден, используем тестовые данные")
        return {
            "Белые вина": [
                {"name": "Кокур", "grape": "Кокур", "price": "450", "image": "kokur.png"}
            ],
            "Красные вина": [
                {"name": "Черный лекарь", "grape": "Качич", "price": "399", "image": "chernyi_lekar.png"},
                {"name": "Киндзмараули", "grape": "Саперави", "price": "550", "image": "kindzmarauli.png"}
            ],
            "Напитки": [
                {"name": "Коньяк классический", "grape": "", "price": "350", "image": "konyak_klassicheskyi.png"},
                {"name": "Чача", "grape": "", "price": "299", "image": "chacha.png"},
                {"name": "Коньяк кизиловый", "grape": "", "price": "350", "image": "konyak_kizilovyi.png"}
            ]
        }


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            try:
                current_year = datetime.now().year
                foundation_year = 1920
                age = current_year - foundation_year

                year_word = get_year_word(age)

                products = load_products()

                with open('template.html', 'r', encoding='utf-8') as f:
                    template_content = f.read()

                template = Template(template_content)
                rendered_html = template.render(
                    age=age,
                    year_word=year_word,
                    products=products
                )

                # Отправляем ответ
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(rendered_html.encode('utf-8'))

                return

            except FileNotFoundError:
                print("template.html не найден")
                self.send_error(404, "template.html not found")
                return

        super().do_GET()


server = HTTPServer(('0.0.0.0', 8000), CustomHandler)
server.serve_forever()