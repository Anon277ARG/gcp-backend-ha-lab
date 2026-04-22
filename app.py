from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

hostname = socket.gethostname()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = f"""
<html>
<body style="text-align:center; font-family:sans-serif;">
    <h1>Pipi esta enojado perdio el tete</h1>
    <h1>{hostname}</h1>
    <p>Backend activo</p>
    <img src="/foto" width="400">
</body>
</html>
"""
            self.wfile.write(html.encode())

        elif self.path == "/foto":
            with open("enojado.jpeg", "rb") as f:
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()
                self.wfile.write(f.read())

server = HTTPServer(("0.0.0.0", 5000), Handler)
server.serve_forever()
