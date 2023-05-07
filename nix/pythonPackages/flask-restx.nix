{ lib, buildPythonPackage, fetchPypi, flask, aniso8601, jsonschema, pytz
, werkzeug }:

buildPythonPackage rec {
  pname = "flask-restx";
  version = "1.0.5";
  format = "setuptools";

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-4j3E/ySGnJL6pxm3pYvhID7XQSdf8yyfA9CrVu0BVGw=";
  };

  propagatedBuildInputs = [ flask aniso8601 jsonschema pytz werkzeug ];

  doCheck = false;

}
