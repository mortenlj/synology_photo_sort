import logging

from ibidem.synology_photo_sort.api import Synology, Api

LOG = logging.getLogger(__name__)


class Item(object):
    def __init__(self, api, data):
        self._api = api
        self._data = data

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError as e:
            raise AttributeError(item)

    def __repr__(self):
        parts = []
        for key, value in self._data.items():
            parts.append(f"{key}={value}")
        return f"{self.__class__.__name__}({', '.join(parts)})"


class Photo(Item):
    pass


class Album(Item):
    def _list_items(self, type):
        params = {
            "method": "list",
            "limit": 100,
            "offset": 0,
            "type": type,
            "id": self.id,
            "additional": "photo_exif",
        }
        total = -1
        offset = 0
        while total != offset:
            params["offset"] = offset
            data = self._api.query(Api.Album, params)
            total, offset = data["total"], data["offset"]
            LOG.debug(f"total {total} vs offset {offset}")
            yield from data["items"]

    def list_children(self) -> list["Album"]:
        for item in self._list_items("album"):
            yield Album(self._api, item)

    def list_photos(self) -> list[Photo]:
        for item in self._list_items("photo"):
            yield Photo(self._api, item)


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
        return Album(self._api, data["items"][0])
