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

"""This module contains custom errors."""


class EneError(Exception):
    """Base error class for ene."""


class APIError(EneError):
    """Class for API errors."""


class APIHTTPError(APIError):
    """Class for HTTP errors from API calls."""

    def __init__(self, status, message=None):
        self.stauts = status
        self.message = message
        super().__init__()

    def __repr__(self):
        return f'APIHTTPError(status={self.stauts}, message={self.message})'


class AuthError(EneError):
    """Class for auth errors."""
    pass
