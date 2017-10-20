#!/usr/bin/python3

import http.server
import json
import re
import sys
import zipfile

PATH_REGEX = re.compile("^/verses/([^/]*)/([^/]*)/([^/])$")
FILENAME_PREFIX_REGEX = r"^en_ulb/\d\d-("
FILENAME_SUFFIX_REGEX = r")\.usfm$"

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

            try: 
                data["verse"] = lookup_verse(book, chapter, verse_num)
                if data["verse"] != "":
                    self.send_response(200)
                else:
                    self.send_response(404)
                    data["message"] = "Couldn't find verse for '"+self.path+"', expecting e.g. /verses/gen/1/1"
            except:
                self.send_response(500)
                data["message"] = "Internal error"
                print("Error:", sys.exc_info()[0])

        else:

            # Not sure what client is looking for
            self.send_response(404)
            data["message"] = "Couldn't understand path '"+self.path+"', expecting e.g. /verses/gen/1/1"

        # Send data response
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(data), "utf8"))

def lookup_verse(book, chapter, verse_num):
    zf = zipfile.ZipFile('ulb.zip')
    filename_match_regex = re.compile(FILENAME_PREFIX_REGEX + book.upper() + FILENAME_SUFFIX_REGEX)
    filenames = zf.namelist()
    for filename in filenames:
        match = filename_match_regex.match(filename)
        if match:
            usfm = zf.read(filename)
            return lookup_verse_from_usfm(usfm, chapter, verse_num)

    # Couldn't find match, return blank
    return ""

def lookup_verse_from_usfm(usfm, chapter, verse_num):
    return "uh, yep!"


if __name__ == "__main__":
    main()
