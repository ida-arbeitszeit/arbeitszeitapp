{ lib, buildPythonPackage, fetchPypi, flask, aniso8601, jsonschema, pytz
, werkzeug, importlib-resources }:
let pypiSource = (builtins.fromJSON (builtins.readFile ./flask-restx.json));
in buildPythonPackage rec {
  pname = pypiSource.pname;
  version = pypiSource.version;
  format = "setuptools";
  src = fetchPypi pypiSource;
  propagatedBuildInputs =
    [ flask aniso8601 jsonschema pytz werkzeug importlib-resources ];
  doCheck = false;
}
