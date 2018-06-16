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
from time import time
from urllib.parse import parse_qsl, urlencode, urlparse

from ene.constants import CONFIG_DIR
from ene.errors import AuthError


class OAuth:
    """
    Handles OAuth to Anilist API

    Listens on http://127.0.0.1:50000 for anilist redirect

    The token is sent via an uri fragment, thus it is forwarded to the
    server side with an AJAX POST

    See Also:
        https://anilist.gitbooks.io/anilist-apiv2-docs/oauth/implicit-grant.html
    """
    TOKEN = None
    TOKEN_FILE = CONFIG_DIR / 'token'

    class _RedirectHandler(BaseHTTPRequestHandler):
        """
        Handles GET and POST requests for the http server
        """

        def _set_headers(self, status: int):
            """
            """
            self.send_response(status)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            """
            Handle GET request to the http server

            Once the user has approved the client they will be redirected to the redirect URI,
            included in the URL fragment will be an access_token parameter that includes
            the JWT access token used to make requests on their behalf.

            Then the URI fragment is sent to the server via POST
            """
            index = """\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
    </head>
    <body>
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
    </body>
</html>"""

            self._set_headers(200)
            self.wfile.write(index.encode())

        def do_POST(self):
            """
            Handle POST request to the http server

            Processes the URI fragment sent via POST and parses
            the token
            """
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()

            for key, val in parse_qsl(urlparse(post_data).fragment):
                if key == 'access_token':
                    access_token = val
                    break
            else:
                access_token = ''

            if access_token:
                self._set_headers(200)
            else:
                self._set_headers(400)

            OAuth.TOKEN = access_token

    def __init__(self, client_id: int, addr: str, port: int):
        """
        Initialize the http server bind address and the client id for OAuth

        Args:
            client_id: The client ID for the application
            addr: The address for the http server to bind to
            port: The port to listen on
        """
        server_addr = (addr, port)
        self.httpd = HTTPServer(server_addr, self._RedirectHandler)
        self.auth_params = {
            'client_id': client_id,
            'response_type': 'token'
        }

    @classmethod
    def get_token(cls, client_id: int, addr: str, port: int, timeout: int = 300) -> str:
        """
        Get the Anilist API access token

        Args:
            client_id: The client ID for the application
            addr: The address for the http server to bind to
            port: The port to listen on
            timeout: Timeout in seconds for getting the auth token

        Returns:
            The Anilist access token

        Raises:
            APIAuthError if failed to get the token
        """
        try:
            token = cls.TOKEN_FILE.read_text()
        except OSError:
            pass
        else:
            if token:
                return token

        self = cls(client_id, addr, port)
        server_thread = Thread(target=self.httpd.serve_forever)
        server_thread.start()
        encode = urlencode(self.auth_params)
        webbrowser.open(f'https://anilist.co/api/v2/oauth/authorize?{encode}')

        start_time = time()
        while cls.TOKEN is None and time() - start_time < timeout:
            pass

        self.httpd.shutdown()
        server_thread.join()

        if not cls.TOKEN:
            raise AuthError()
        else:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            cls.TOKEN_FILE.touch()
            cls.TOKEN_FILE.write_text(cls.TOKEN)
            return cls.TOKEN
