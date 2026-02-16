from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Template
from datetime import datetime


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            try:
                current_year = datetime.now().year
                foundation_year = 1920
                age = current_year - foundation_year

                with open('template.html', 'r', encoding='utf-8') as f:
                    template_content = f.read()

                template = Template(template_content)
                rendered_html = template.render(age=age)

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(rendered_html.encode('utf-8'))

                print(f"Возраст винодельни: {age} лет")
                return

            except FileNotFoundError:
                print("template.html не найден")
                self.send_error(404, "template.html not found")
                return

        super().do_GET()


server = HTTPServer(('0.0.0.0', 8000), CustomHandler)
server.serve_forever()