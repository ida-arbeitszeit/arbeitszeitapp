import json
import logging
import re
import subprocess
import urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name="update_flask_restx")


def main() -> None:
    version = detect_latest_package_version()
    logger.info("Detected version %s as latest", version)
    sha256_sum = detect_sha256_sum_for_version(version)
    logger.info("Tarball sha256 sum is %s", sha256_sum)
    write_restx_source_json(version, sha256_sum)


def detect_latest_package_version() -> str:
    with urllib.request.urlopen("https://pypi.org/pypi/flask-restx/json") as response:
        encoding = response.info().get_content_charset("utf-8")
        content_data = response.read()
    content_json = json.loads(content_data.decode(encoding))
    version = content_json["info"]["version"]
    assert isinstance(version, str)
    return version


def detect_sha256_sum_for_version(version: str) -> str:
    completed_process = subprocess.run(
        [
            "nix-build",
            "-E",
            restx_source_expression_for_version(version),
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
        raise Exception("Could not detect sha256 hash for flask-restx tarball")


def write_restx_source_json(version: str, sha256_sum: str) -> None:
    with open("nix/pythonPackages/flask-restx.json", "w") as json_output_file:
        json.dump(
            {
                "pname": "flask-restx",
                "version": version,
                "sha256": sha256_sum,
            },
            json_output_file,
        )


def restx_source_expression_for_version(version: str) -> str:
    return f"""
    let pkgs = import <nixpkgs> {{}};
    in pkgs.python3.pkgs.fetchPypi {{
      pname = "flask-restx";
      version = "{version}";
      sha256 = "";
    }}
    """


if __name__ == "__main__":
    main()
