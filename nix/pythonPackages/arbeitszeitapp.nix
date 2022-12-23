{ buildPythonPackage, pytestCheckHook

# python packages
, email_validator, flask, flask-babel, flask-talisman, flask_login, flask_mail
, flask_migrate, flask-restx, flask_wtf, injector, is_safe_url, matplotlib
, sphinx, flask-profiler }:
buildPythonPackage {
  pname = "arbeitszeitapp";
  version = "0.0.0";
  src = ../..;
  outputs = [ "out" "doc" ];
  postPhases = [ "buildDocsPhase" ];
  format = "pyproject";
  buildInputs = [ pytestCheckHook sphinx ];
  propagatedBuildInputs = [
    email_validator
    flask
    flask-babel
    flask-talisman
    flask_login
    flask_mail
    flask_migrate
    flask-restx
    flask_wtf
    injector
    is_safe_url
    matplotlib
  ];
  buildDocsPhase = ''
    mkdir -p $doc/share/doc/arbeitszeitapp
    python -m sphinx -a $src/docs $doc/share/doc/arbeitszeitapp
  '';
  passthru.optional-dependencies = { profiling = [ flask-profiler ]; };
}
