{ mkShell, python3, nixfmt }:
mkShell {
  packages = (with python3.pkgs; [
    black
    flake8
    mypy
    isort
    psycopg2
    gunicorn
    types-dateutil
    coverage
    flask-restx
  ]) ++ [ nixfmt ]
    ++ python3.pkgs.arbeitszeitapp.optional-dependencies.profiling;
  inputsFrom = [ python3.pkgs.arbeitszeitapp ];
}
