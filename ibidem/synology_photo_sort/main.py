#!/usr/bin/env python
import logging

from fiaas_logging import init_logging

from ibidem.synology_photo_sort.photo_station import PhotoStation
from ibidem.synology_photo_sort.settings import Settings

LOG = logging.getLogger(__name__)


def _init_logging():
    init_logging(debug=True)


def place_photo(photo, album):
    """Figure out appropriate year for `photo`, and move it to correct child of `album`"""
    LOG.debug("TODO: Placing photo")


def sort_album(album):
    for child in album.list_children():
        sort_album(child)
    for photo in album.list_photos():
        place_photo(photo, album)


def main():
    _init_logging()
    settings = Settings()
    LOG.info("Starting sort process with %s", settings)

    photo_station = PhotoStation(settings.dsm_url, settings.dsm_user, settings.dsm_pass.get_secret_value())
    LOG.info("Authentication status: %r", photo_station._api.authenticated())
    album = photo_station.get_album(settings.album)
    LOG.info("Listing children in album %s", album)
    for child in album.list_children():
        LOG.info(child)
    LOG.info("Listing photos in album %s", album)
    for photo in album.list_photos():
        LOG.info(photo)
    # sort_album(album)


if __name__ == '__main__':
    main()
