{ lib, buildPythonPackage, fetchPypi, flask, aniso8601, jsonschema, pytz
, werkzeug }:

buildPythonPackage rec {
  pname = "flask-restx";
  version = "1.1.0";
  format = "setuptools";

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-Yra2yd5l5ZYM9PizXhvT7KaZiDigGy9x4qnUwUpMzRQ=";
  };

  propagatedBuildInputs = [ flask aniso8601 jsonschema pytz werkzeug ];

  doCheck = false;

}
