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
    sphinx
  ]) ++ [ nixfmt ];
  inputsFrom = [ python3.pkgs.arbeitszeitapp ];
}
