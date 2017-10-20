#!/usr/bin/python3

import http.server
import json
import os.path
import re
import sys
import urllib.request
import zipfile

PATH_REGEX = re.compile("^/verses/([^/]*)/([^/]*)/([^/])$")
FILENAME_PREFIX_REGEX = r"^en_ulb/\d\d-("
FILENAME_SUFFIX_REGEX = r")\.usfm$"

def main():

    # Download ULB if needed
    if os.path.isfile("ulb.zip") == False:
        print("Downloading ulb.zip...", end='', flush=True)
        with urllib.request.urlopen("https://cdn.door43.org/en/ulb/v10/ulb.zip") as infile:
            with open("ulb.zip", "wb") as outfile:
                for b in infile:
                    outfile.write(b)
        print("done.")

    # Start server
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
        data["error"] = "false"
        data["message"] = ""

        # Check path against expected pattern
        match = PATH_REGEX.match(self.path)
        if match:
            # Pattern looks good
            book = match.group(1)
            chapter = match.group(2)
            verse_num = match.group(3)
            data["book"] = book
            data["chapter"] = chapter
            data["verse_num"] = verse_num
            response = lookup_verse_from_ulb(book, chapter, verse_num)
            if response["error"]:
                self.send_response(404)
                data["error"] = "true"
                data["message"] = response["message"]
            else:
                data["verse"] = response["verse"]
                self.send_response(200)
        else:
            # Not sure what client is looking for
            self.send_response(404)
            data["error"] = "true"
            data["message"] = "Couldn't understand path '"+self.path+"', expecting e.g. /verses/gen/1/1"

        # Send data response
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(data), "utf8"))

def lookup_verse_from_ulb(book, chapter, verse_num):

    # Prepare response
    response = {}
    response["verse"] = ""
    response["error"] = False
    response["message"] = ""

    # Look in zip file for book
    zf = zipfile.ZipFile('ulb.zip')
    filename_match_regex = re.compile(FILENAME_PREFIX_REGEX + book.upper() + FILENAME_SUFFIX_REGEX)
    filenames = zf.namelist()
    for filename in filenames:
        match = filename_match_regex.match(filename)
        if match:
            # Found book, lookup chapter and verse
            with zf.open(filename) as usfm_stream:
                return lookup_verse_from_usfm(usfm_stream, chapter, verse_num)

    # Couldn't find match, return blank
    response["error"] = True
    response["message"] = "Couldn't find book named " + book
    return response

def lookup_verse_from_usfm(usfm_stream, chapter, verse_num):

    # Prepare response
    response = {}
    response["verse"] = ""
    response["error"] = False
    response["message"] = ""

    # Prepare chapter and verse matchers
    chapter_regex = re.compile(r"^\\c (\d+)$")
    verse_regex = re.compile(r"^\\v "+verse_num+" (.*)$")

    # Look for chapter and verse
    current_chapter = None
    for line_bytes in usfm_stream:
        line = line_bytes.decode("utf-8")
        chapter_match = chapter_regex.match(line)
        if chapter_match:
            current_chapter = chapter_match.group(1)
        if current_chapter == chapter:
            verse_match = verse_regex.match(line)
            if verse_match:
                response["verse"] = verse_match.group(1)
                return response

    # Not found
    response["error"] = True
    response["message"] = "Verse not found."
    return response


if __name__ == "__main__":
    main()
