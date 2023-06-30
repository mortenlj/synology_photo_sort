#!/usr/bin/env python
import logging

from fiaas_logging import init_logging

from ibidem.synology_photo_sort.settings import Settings

LOG = logging.getLogger(__name__)


def _init_logging():
    init_logging(debug=True)


def main():
    _init_logging()
    settings = Settings()
    LOG.info("Starting sort process with %s", settings)


if __name__ == '__main__':
    main()
