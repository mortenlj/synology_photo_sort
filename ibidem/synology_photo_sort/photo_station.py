import logging
from pprint import pformat

# TODO: Replace this with own implementation :(
from photostation.service import PhotoStationPhoto

from ibidem.synology_photo_sort.api import Synology, Api

LOG = logging.getLogger(__name__)


class Photo(object):
    def __init__(self, psphoto: PhotoStationPhoto):
        self._psphoto = psphoto

    def __repr__(self):
        return repr(self._psphoto)


class Album(object):
    def __init__(self, data):
        self._data = data

    def list_children(self) -> list["Album"]:
        pass

    def list_photos(self) -> list[Photo]:
        pass

    def __repr__(self):
        return repr(self._data)


def album_id(album):
    if album:
        hex_id = album.encode("utf-8").hex()
        return f"album_{hex_id}"
    return ""


class PhotoStation(object):
    def __init__(self, url, user, password):
        self._user = user
        self._api = Synology(url, user, password)

    def get_album(self, album: str) -> Album:
        data = self._api.query(Api.Album, {
            "method": "getinfo",
            "id": album_id(album),
        })
        LOG.debug("Album data: %s", pformat(data))
        return Album(data)
