import argparse
from pathlib import Path
from typing import Tuple, Any, Dict

from pydantic import BaseSettings, HttpUrl, SecretStr
from pydantic.env_settings import SettingsSourceCallable


def cli_settings(_: BaseSettings) -> Dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("album", help="Name of the album to sort")
    parser.add_argument("path", help="The location on disk where the files in this album is located")
    options = parser.parse_args()
    return options.__dict__


class Settings(BaseSettings):
    dsm_user: str
    dsm_pass: SecretStr
    dsm_url: HttpUrl
    album: str
    path: Path

    class Config:
        @classmethod
        def customise_sources(
                cls,
                init_settings: SettingsSourceCallable,
                env_settings: SettingsSourceCallable,
                file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return cli_settings, env_settings, init_settings, file_secret_settings
