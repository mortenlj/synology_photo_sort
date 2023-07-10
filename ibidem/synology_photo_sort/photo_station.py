import logging

from ibidem.synology_photo_sort.api import Synology, Api

LOG = logging.getLogger(__name__)


class Item(object):
    def __init__(self, api, data, dry_run):
        self._api = api
        self._data = data
        self._dry_run = dry_run

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError as e:
            try:
                return self._data["info"][item]
            except KeyError as e:
                raise AttributeError(item)

    def __repr__(self):
        parts = []
        for key, value in self._data.items():
            parts.append(f"{key}={value}")
        return f"{self.__class__.__name__}({', '.join(parts)})"


class Photo(Item):
    def move(self, target_album):
        if self._dry_run:
            LOG.debug("Would move %r to %r", self, target_album)
        else:
            self._api.query(Api.Photo, {
                "method": "copy",
                "id": self.id,
                "sharepath": target_album.id,
                "mode": "move",
                "duplicate": "overwrite",
            })


class Album(Item):
    def __init__(self, api, data, dry_run):
        super().__init__(api, data, dry_run)
        self._name2id = {}

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
            LOG.debug("Received item %r", item)
            album = Album(self._api, item, self._dry_run)
            self._name2id[album.name] = album.id
            yield album

    def list_photos(self) -> list[Photo]:
        for item in self._list_items("photo"):
            yield Photo(self._api, item, self._dry_run)

    def list_videos(self) -> list[Photo]:
        for item in self._list_items("video"):
            yield Photo(self._api, item, self._dry_run)

    def get(self, name: str, create=True) -> "Album":
        if name in self._name2id:
            LOG.debug("Getting known album %s with id %s", name, self._name2id[name])
            data = self._api.query(Api.Album, {
                "method": "getinfo",
                "id": self._name2id[name]
            })
            return Album(self._api, data["items"][0], self._dry_run)
        else:
            LOG.debug("Searching through all children for album with name %s", name)
            for child in self.list_children():
                LOG.debug("Comparing %r with %r", child.name, name)
                if child.name == name:
                    LOG.debug("Found album with name %s: %r", name, child)
                    return child
        if create:
            if self._dry_run:
                LOG.debug("Would create new album named %s as child of %r", name, self)
            else:
                LOG.debug("Creating new album named %s as child of %r", name, self)
                self._api.query(Api.Album, {
                    "method": "create",
                    "name": name,
                    "id": self.id,
                    "title": name,
                    "type": "private",
                })
                return self.get(name, create=False)
        raise RuntimeError("Unable to find or create album %s", name)


def album_id(album):
    if album:
        hex_id = album.encode("utf-8").hex()
        return f"album_{hex_id}"
    return ""


class PhotoStation(object):
    def __init__(self, url, user, password, dry_run):
        self._user = user
        self._api = Synology(url, user, password)
        self._dry_run = dry_run

    def get_album(self, album: str) -> Album:
        data = self._api.query(Api.Album, {
            "method": "getinfo",
            "id": album_id(album),
        })
        return Album(self._api, data["items"][0], self._dry_run)
