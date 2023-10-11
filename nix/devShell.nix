{ mkShell, python3, nixfmt, sqlite }:
mkShell {
  packages = (with python3.pkgs; [
    black
    build
    coverage
    flake8
    gunicorn
    isort
    mypy
    pip
    psycopg2
    types-dateutil
    types-pytz
    types-setuptools
  ]) ++ [ nixfmt sqlite ]
    ++ python3.pkgs.arbeitszeitapp.optional-dependencies.profiling;
  inputsFrom = [ python3.pkgs.arbeitszeitapp ];
}
