#!/usr/bin/env python
import logging
import re

import arrow
from fiaas_logging import init_logging

from ibidem.synology_photo_sort.photo_station import PhotoStation
from ibidem.synology_photo_sort.settings import Settings

LOG = logging.getLogger(__name__)


class Patterns:
    ISO_DATE_NUM = re.compile(r"(20\d{2})[01]\d[0-3]\d\d{3}")
    DATE_NUM = re.compile(r"[0-3]\d[01]\d(20\d{2})\d{3}")


def _init_logging():
    init_logging(debug=True)


def place_photo(photo, album):
    """Figure out appropriate year for `photo`, and move it to correct child of `album`"""
    info = photo.info
    target = _extract_target_year(info)
    if target:
        # LOG.debug("Targetting %04d for %r", target, photo)
        return 1
    else:
        # LOG.error("Failed to extract year from %r", photo)
        return 0


def _extract_target_year(info):
    try:
        taken = arrow.get(info["takendate"])
        if taken > arrow.get("2000"):
            return taken.date().year
    except arrow.parser.ParserError:
        pass
    filename = info.get("title")
    if m := Patterns.ISO_DATE_NUM.match(filename):
        return int(m.group(1))
    if m := Patterns.DATE_NUM.match(filename):
        return int(m.group(1))
    try:
        created = arrow.get(info["createdate"])
        if created > arrow.get("2014"):
            return created.date().year
    except arrow.parser.ParserError:
        pass


def sort_album(album):
    success = 0
    for photo in album.list_photos():
        success += place_photo(photo, album)
    LOG.info("Placed %d photos", success)


def main():
    _init_logging()
    settings = Settings()
    LOG.info("Starting sort process with %s", settings)

    photo_station = PhotoStation(settings.dsm_url, settings.dsm_user, settings.dsm_pass.get_secret_value())
    album = photo_station.get_album(settings.album)
    sort_album(album)


if __name__ == '__main__':
    main()
