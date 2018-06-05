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
from urllib.parse import urlencode

CLIENT_ID = '584'
REDIR_URI = 'http://127.0.0.1:50000'


class OAuth:
    TOKEN = None

    def __init__(self, client_id, redirect_uri, addr, port):
        server_addr = (addr, port)
        self.httpd = HTTPServer(server_addr, RedirectHandler)
        self.auth_params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code'
        }

    @classmethod
    def get_token(cls, client_id, redirect_uri, addr, port):
        self = cls(client_id, redirect_uri, addr, port)
        server_thread = Thread(target=self.httpd.serve_forever)
        server_thread.start()
        encode = urlencode(self.auth_params)
        webbrowser.open(f'https://anilist.co/api/v2/oauth/authorize?{encode}')
        while not cls.TOKEN:
            pass
        self.httpd.shutdown()
        server_thread.join()
        return cls.TOKEN if cls.TOKEN != -1 else None


class RedirectHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        token = self.path.replace('/?code=', '')
        if token:
            self.send_response(200)  # OK
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Success!')
            OAuth.TOKEN = token
        else:
            self.send_response(400)  # OK
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Fail!')
            OAuth.TOKEN = -1


class API:
    def __init__(self):
        self.token = OAuth.get_token(CLIENT_ID, REDIR_URI, '127.0.0.1', 50000)
