{ lib, buildPythonPackage, fetchPypi, flask, aniso8601, jsonschema, pytz
, werkzeug }:

buildPythonPackage rec {
  pname = "flask-restx";
  version = "1.1.0";
  format = "setuptools";

  src = fetchPypi (builtins.fromJSON (builtins.readFile ./flask-restx.json));

  propagatedBuildInputs = [ flask aniso8601 jsonschema pytz werkzeug ];

  doCheck = false;

}
