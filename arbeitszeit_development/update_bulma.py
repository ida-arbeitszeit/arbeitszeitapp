from __future__ import annotations

import json
import logging
import tempfile
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator, List
from urllib.request import urlopen

logger = logging.getLogger(name=__name__)


def main() -> None:
    zip_factory = ZipFactory()
    github_api = GithubApi()
    updater = BulmaUpdater(
        github_api=github_api,
        logger=logger,
        zip_factory=zip_factory,
    )
    updater.update_bulma()


@dataclass
class BulmaUpdater:
    github_api: GithubApi
    logger: logging.Logger
    zip_factory: ZipFactory

    def update_bulma(self) -> None:
        self.logger.info("Detecting latest bulma release")
        release = self.get_latest_bulma_release()
        self.logger.info(f"Found bulma release {release.name}")
        target_path = self.get_target_path()
        source_path = "bulma/css/bulma.min.css"
        asset_name = self.get_asset_name(release)
        with release.download_asset(asset_name) as bulma_archive_path:
            bulma_archive = self.zip_factory.create_zip_archive(bulma_archive_path)
            bulma_archive.unpack_archive_member(
                source_path=source_path, target_path=target_path
            )

    def get_latest_bulma_release(self) -> GithubRelease:
        return self.github_api.get_latest_release(owner="jgthms", repo="bulma")

    def get_target_path(self) -> Path:
        module_path = Path(__file__)
        return module_path.parent.parent / "arbeitszeit_flask" / "static" / "bulma.css"

    def get_asset_name(self, release: GithubRelease) -> str:
        for asset in release.asset_names:
            if asset.startswith("bulma-") and asset.endswith(".zip"):
                return asset
        raise Exception(
            f"Could not find 'bulma-*.zip' asset in github release {release.release_json}"
        )


@dataclass
class GithubApi:
    def get_latest_release(self, owner: str, repo: str) -> GithubRelease:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        with urlopen(url) as response:
            encoding = response.info().get_content_charset("utf-8")
            content_data = response.read()
        content_json = json.loads(content_data.decode(encoding))
        return GithubRelease(release_json=content_json)


@dataclass
class GithubRelease:
    release_json: Any

    @property
    def asset_names(self) -> List[str]:
        return [asset["name"] for asset in self.release_json["assets"]]

    @property
    def name(self) -> str:
        return self.release_json["name"]

    @contextmanager
    def download_asset(self, name: str) -> Generator[Path, None, None]:
        logger.info(f"Downloading release asset {name}")
        download_url = self.get_zip_download_url(name)
        with tempfile.TemporaryDirectory() as directory:
            zip_file = Path(directory) / f"asset-{name}.zip"
            with urlopen(download_url) as response:
                with open(zip_file, "wb") as write_handle:
                    write_handle.write(response.read())
            yield zip_file

    def get_zip_download_url(self, name: str) -> str:
        for asset in self.release_json["assets"]:
            name = asset.get("name", "")
            if asset.get("name") != name:
                continue
            return asset["browser_download_url"]
        raise Exception(
            f"Github release did not contain asset named '{name}', relase metadata was {self.release_json}"
        )


@dataclass
class ZipFactory:
    def create_zip_archive(self, path: Path) -> ZipArchive:
        return ZipArchive(path=path)


@dataclass
class ZipArchive:
    path: Path

    def unpack_archive_member(self, source_path: str, target_path: Path) -> None:
        logger.info(f"Unpacking {source_path} to {target_path}")
        with zipfile.ZipFile(self.path) as zip_handle:
            with open(target_path, "wb") as write_handle:
                write_handle.write(zip_handle.read(source_path))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
