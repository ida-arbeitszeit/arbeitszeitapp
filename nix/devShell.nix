{ mkShell, python3, nixfmt, sqlite }:
mkShell {
  packages = (with python3.pkgs; [
    black
    flake8
    mypy
    isort
    psycopg2
    gunicorn
    types-dateutil
    types-pytz
    coverage
    pip
  ]) ++ [ nixfmt sqlite ]
    ++ python3.pkgs.arbeitszeitapp.optional-dependencies.profiling;
  inputsFrom = [ python3.pkgs.arbeitszeitapp ];
}
