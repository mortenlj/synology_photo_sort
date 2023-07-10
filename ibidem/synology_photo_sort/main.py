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
    DATE_STRING = re.compile(r"\d\d\._[a-z]+_(20\d\d)_\d{3}")


def _init_logging():
    init_logging(debug=True)


def place_media(media, album):
    """Figure out appropriate year for `media`, and move it to correct child of `album`"""
    info = media.info
    target = _extract_target_year(info)
    if target:
        LOG.debug("Targeting %04d for %r", target, media)
        sub_album = album.get(str(target))
        media.move(sub_album)
    else:
        LOG.info("Failed to find year for %r", media)


def _extract_target_year(info):
    try:
        taken = arrow.get(info["takendate"])
        if taken > arrow.get("2000"):
            return taken.date().year
    except arrow.parser.ParserError:
        pass
    title = info.get("title")
    if m := Patterns.ISO_DATE_NUM.match(title):
        return int(m.group(1))
    if m := Patterns.DATE_NUM.match(title):
        return int(m.group(1))
    if m := Patterns.DATE_STRING.match(title):
        return int(m.group(1))
    try:
        created = arrow.get(info["createdate"])
        if created > arrow.get("2014"):
            return created.date().year
    except arrow.parser.ParserError:
        pass


def sort_album(album):
    for media in album.list_media():
        place_media(media, album)


def main():
    _init_logging()
    settings = Settings()
    LOG.info("Starting sort process with %s", settings)

    photo_station = PhotoStation(settings.dsm_url, settings.dsm_user, settings.dsm_pass.get_secret_value(),
                                 settings.dry_run)
    album = photo_station.get_album(settings.album)
    sort_album(album)


if __name__ == '__main__':
    main()
