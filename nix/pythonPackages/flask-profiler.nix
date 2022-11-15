{ buildPythonPackage, fetchFromGitHub, simplejson, flask-httpauth, flask
, sqlalchemy, flask-testing }:
buildPythonPackage rec {
  pname = "flask_profiler";
  version = "master";
  src = fetchFromGitHub
    (builtins.fromJSON (builtins.readFile ./flask-profiler.json));
  propagatedBuildInputs = [ simplejson flask-httpauth flask ];
  checkInputs = [ sqlalchemy flask-testing ];
}
