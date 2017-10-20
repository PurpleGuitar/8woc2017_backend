#!/usr/bin/python3

import http.server
import json
import re

PATH_REGEX = re.compile("^/verses/([^/]*)/([^/]*)/([^/])$")

def main():
    print("Starting server...", end='', flush=True)
    server_address = ("0.0.0.0", 8000)
    httpd = http.server.HTTPServer(server_address, MyHTTPRequestHandler)
    print("done.")
    print("Server running.")
    httpd.serve_forever()

class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):


    def do_GET(self):

        # Initialize response
        data = {}
        data["book"] = ""
        data["chapter"] = ""
        data["verse_num"] = ""
        data["verse"] = ""
        data["message"] = ""

        # Check path against expected pattern
        match = PATH_REGEX.match(self.path)
        if match:

            book = match.group(1)
            chapter = match.group(2)
            verse_num = match.group(3)
            data["book"] = book
            data["chapter"] = chapter
            data["verse_num"] = verse_num

            data["verse"] = "hello" # TODO

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

        else:

            # Not sure what client is looking for
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data["message"] = "Couldn't understand path '"+self.path+"'', expecting e.g. /verses/gen/1/1"

        # Send data response
        self.wfile.write(bytes(json.dumps(data), "utf8"))


if __name__ == "__main__":
    main()
