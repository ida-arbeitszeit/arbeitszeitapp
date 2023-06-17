{ buildPythonPackage, fetchPypi }:
let pypiSource = (builtins.fromJSON (builtins.readFile ./is-safe-url.json));
in buildPythonPackage rec {
  pname = pypiSource.pname;
  version = pypiSource.version;
  src = fetchPypi pypiSource;
}
