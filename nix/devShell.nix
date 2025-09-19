{
  mkShell,
  python3,
  nixfmt,
  sqlite,
  glibcLocales,
  includeGlibcLocales,
  lib,
  git,
}:
mkShell (
  {
    packages =
      (with python3.pkgs; [
        black
        build
        coverage
        flake8
        gunicorn
        isort
        mypy
        pip
        psycopg2
        types-setuptools
      ])
      ++ [
        nixfmt
        sqlite
        git
      ]
      ++ python3.pkgs.arbeitszeitapp.optional-dependencies.profiling;
    inputsFrom = [ python3.pkgs.arbeitszeitapp ];
  }
  // lib.optionalAttrs includeGlibcLocales {
    LOCALE_ARCHIVE = "${glibcLocales}/lib/locale/locale-archive";
  }
)
