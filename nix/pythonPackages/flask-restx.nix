{ lib, buildPythonPackage, fetchPypi, flask, aniso8601, jsonschema, pytz
, werkzeug }:

buildPythonPackage rec {
  pname = "flask-restx";
  version = "1.0.3";
  format = "setuptools";

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-X9rNIwMdJf9GQvFBpHp/qHfwfj4mEJnMxevE/CVN6Ew=";
  };

  propagatedBuildInputs = [ flask aniso8601 jsonschema pytz werkzeug ];

  doCheck = false;

}
