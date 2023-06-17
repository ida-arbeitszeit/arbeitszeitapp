import json
import logging
import re
import subprocess
import urllib.request
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)


def main() -> None:
    update_python_package("nix/pythonPackages/flask-restx.json", "flask-restx")
    update_python_package("nix/pythonPackages/is-safe-url.json", "is_safe_url")


def update_python_package(path: str, package: str) -> None:
    version = detect_latest_package_version(package)
    logger.info("Detected version %s as latest for %s", version, package)
    sha256_sum = detect_sha256_sum_for_version(package, version)
    logger.info("Tarball sha256 sum is %s", sha256_sum)
    write_source_json(
        path=path,
        package=package,
        version=version,
        sha256_sum=sha256_sum,
    )


def detect_latest_package_version(package: str) -> str:
    with urllib.request.urlopen(
        f"https://pypi.org/pypi/{quote(package)}/json"
    ) as response:
        encoding = response.info().get_content_charset("utf-8")
        content_data = response.read()
    content_json = json.loads(content_data.decode(encoding))
    version = content_json["info"]["version"]
    assert isinstance(version, str)
    return version


def detect_sha256_sum_for_version(package: str, version: str) -> str:
    completed_process = subprocess.run(
        [
            "nix-build",
            "-E",
            source_expression(package, version),
            "--no-out-link",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    for line in completed_process.stderr.splitlines():
        if match := re.search(r"got:\s+(?P<hash>.*)", line):
            return match["hash"].strip()
    else:
        raise Exception(f"Could not detect sha256 hash for {package} tarball")


def write_source_json(path: str, package: str, version: str, sha256_sum: str) -> None:
    with open(path, "w") as json_output_file:
        json.dump(
            {
                "pname": package,
                "version": version,
                "sha256": sha256_sum,
            },
            json_output_file,
        )


def source_expression(package: str, version: str) -> str:
    return f"""
    let pkgs = import <nixpkgs> {{}};
    in pkgs.python3.pkgs.fetchPypi {{
      pname = "{package}";
      version = "{version}";
      sha256 = "";
    }}
    """


if __name__ == "__main__":
    main()
