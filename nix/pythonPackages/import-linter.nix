{
  lib,
  buildPythonPackage,
  fetchPypi,

  hatchling,
  click,
  grimp,
  typing-extensions,
}:
let
  pypiSource = (builtins.fromJSON (builtins.readFile ./import-linter.json));
in
buildPythonPackage rec {
  pname = pypiSource.pname;
  version = pypiSource.version;
  format = "pyproject";
  src = fetchPypi pypiSource;
  nativeBuildInputs = [
    hatchling
  ];
  propagatedBuildInputs = [
    click
    grimp
    typing-extensions
  ];
}
