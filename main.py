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
        raise FileNotFoundError("Файл wine3.xlsx не найден")

    df = pd.read_excel('wine3.xlsx', sheet_name='Лист1')

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

    print(f"Загружено товаров: {sum(len(v) for v in products.values())}")
    for category, items in products.items():
        sale_count = sum(1 for item in items if item['sale'])
        print(f"   {category}: {len(items)} (акций: {sale_count})")

    return dict(products)


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

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(rendered_html.encode('utf-8'))

                print(f"✅ Страница обновлена: {age} {year_word}")

            except FileNotFoundError as e:
                print(f"Ошибка: {e}")
                self.send_error(404, f"Файл не найден: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")
                self.send_error(500, f"Внутренняя ошибка сервера: {e}")

            return

        super().do_GET()


if __name__ == '__main__':
    server_address = ('0.0.0.0', 8000)
    httpd = HTTPServer(server_address, CustomHandler)


    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Сервер остановлен")