import logging
from pprint import pformat

from photostation.session import SynologySession

LOG = logging.getLogger(__name__)


class Api(object):
    Album = "SYNO.PhotoStation.Album"
    Auth = "SYNO.PhotoStation.Auth"
    Photo = "SYNO.PhotoStation.Photo"


class Synology(SynologySession):
    def __init__(self, url, username, password):
        self._username = username
        self._password = password
        super().__init__(url)
        self._login()

    def _login(self):
        LOG.debug("Logging in user %s", self._username)
        params = {
            'version': 1,
            'method': 'login',
            'username': self._username,
            'password': self._password,
            'remember_me': True
        }

        self.query(Api.Auth, params)
        if not self._authenticated():
            raise RuntimeError("Failed to get authenticated")

    def _authenticated(self):
        LOG.debug('check authentication status')
        check = self.query(Api.Auth, {'method': 'checkauth'})
        return check['permission']['manage']
