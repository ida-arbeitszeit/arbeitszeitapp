{ buildPythonPackage, pytestCheckHook

# python packages
, email_validator, flask, flask-babel, flask-talisman, flask_login, flask_mail
, flask_migrate, flask_wtf, hypothesis, injector, is_safe_url, matplotlib
, sphinx }:
buildPythonPackage {
  pname = "arbeitszeitapp";
  version = "develop";
  src = ../..;
  outputs = [ "out" "doc" ];
  postPhases = [ "buildDocsPhase" ];
  format = "pyproject";
  buildInputs = [ pytestCheckHook sphinx ];
  checkInputs = [ hypothesis ];
  propagatedBuildInputs = [
    email_validator
    flask
    flask-babel
    flask-talisman
    flask_login
    flask_mail
    flask_migrate
    flask_wtf
    injector
    is_safe_url
    matplotlib
  ];
  buildDocsPhase = ''
    mkdir -p $doc/share/doc/arbeitszeitapp
    python -m sphinx -a $src/docs $doc/share/doc/arbeitszeitapp
  '';
}
