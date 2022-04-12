{ buildPythonPackage, pytestCheckHook

# python packages
, email_validator, flask, flask-babel, flask-talisman, flask_login, flask_mail
, flask_migrate, flask_wtf, hypothesis, injector, is_safe_url, matplotlib }:
buildPythonPackage {
  pname = "arbeitszeitapp";
  version = "develop";
  src = ../..;
  buildInputs = [ pytestCheckHook ];
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
}
