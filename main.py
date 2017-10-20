#!/usr/bin/python3

import http.server

def main():
    print("Starting server...", end='', flush=True)
    server_address = ("0.0.0.0", 8000)
    httpd = http.server.HTTPServer(server_address, MyHTTPRequestHandler)
    print("done.")
    print("Server running.")
    httpd.serve_forever()

class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(bytes('{"verse":"hello"}', "utf8"))

if __name__ == "__main__":
    main()
