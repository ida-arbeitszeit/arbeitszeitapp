import subprocess

from . import update_flask_restx


def main() -> None:
    update_flake()
    update_bulma()
    update_flask_restx.main()
    update_constraints()


def update_flake() -> None:
    subprocess.run(["nix", "flake", "update"], check=True)


def update_bulma() -> None:
    subprocess.run(
        ["python", "-m", "arbeitszeit_development.update_bulma"],
        check=True,
    )


def update_constraints() -> None:
    subprocess.run(
        [
            "nix",
            "develop",
            "-c",
            "python",
            "-m",
            "arbeitszeit_development.update_constraints",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
