import logging
from pprint import pformat

from photostation.session import SynologySession

LOG = logging.getLogger(__name__)


class Api(object):
    Album = "SYNO.PhotoStation.Album"
    Auth = "SYNO.PhotoStation.Auth"


class Synology(SynologySession):
    def __init__(self, url, username, password):
        self._username = username
        self._password = password
        super().__init__(url)
        self._login()
        LOG.debug("API info: \n%s", pformat(self.info))

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

    def authenticated(self):
        LOG.debug('check authentication status')
        check = self.query(Api.Auth, {'method': 'checkauth'})
        return check['permission']['manage']
