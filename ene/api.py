#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018 Peijun Ma, Justin Sedge
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.parse import parse_qsl, urlencode, urlparse

CLIENT_ID = '584'


class OAuth:
    TOKEN = None

    def __init__(self, client_id, addr, port):
        server_addr = (addr, port)
        self.httpd = HTTPServer(server_addr, RedirectHandler)
        self.auth_params = {
            'client_id': client_id,
            'response_type': 'token'
        }

    @classmethod
    def get_token(cls, client_id, addr, port):
        self = cls(client_id, addr, port)
        server_thread = Thread(target=self.httpd.serve_forever)
        server_thread.start()
        encode = urlencode(self.auth_params)
        webbrowser.open(f'https://anilist.co/api/v2/oauth/authorize?{encode}')
        while cls.TOKEN is None:
            pass
        self.httpd.shutdown()
        server_thread.join()
        return cls.TOKEN


class RedirectHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        index = """
<html>
    <script>
    let hash = window.location.hash;
    xhr = new XMLHttpRequest();
    xhr.onload = function () {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
              alert("Authentication Success! You may close this browser tab now.");
          }
        } else {
            alert("Authentication Failed!");
        }
    };
    xhr.open('POST', '/');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(hash);
    </script>
</html>
        """
        self._set_headers(200)
        self.wfile.write(index.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()

        try:
            access_token = parse_qsl(urlparse(post_data).fragment)[0][1]
        except IndexError:
            access_token = ''

        if access_token:
            self._set_headers(200)
        else:
            self._set_headers(400)

        OAuth.TOKEN = access_token


class API:
    def __init__(self):
        self.token = OAuth.get_token(CLIENT_ID, '127.0.0.1', 50000)
