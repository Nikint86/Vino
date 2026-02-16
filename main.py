from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Template
from datetime import datetime
import os
import json


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


wines = [
    {
        "name": "Изабелла",
        "grape": "Изабелла",
        "price": "350",
        "image": "izabella.png"
    },
    {
        "name": "Гранатовый браслет",
        "grape": "Мускат розовый",
        "price": "350",
        "image": "granatovyi_braslet.png"
    },
    {
        "name": "Шардоне",
        "grape": "Шардоне",
        "price": "350",
        "image": "shardone.png"
    },
    {
        "name": "Белая леди",
        "grape": "Дамский пальчик",
        "price": "399",
        "image": "belaya_ledi.png"
    },
    {
        "name": "Ркацители",
        "grape": "Ркацители",
        "price": "499",
        "image": "rkaciteli.png"
    },
    {
        "name": "Хванчкара",
        "grape": "Александраули",
        "price": "550",
        "image": "hvanchkara.png"
    }
]


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            try:
                current_year = datetime.now().year
                foundation_year = 1920
                age = current_year - foundation_year

                year_word = get_year_word(age)

                with open('template.html', 'r', encoding='utf-8') as f:
                    template_content = f.read()

                template = Template(template_content)
                rendered_html = template.render(
                    age=age,
                    year_word=year_word,
                    wines=wines
                )

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