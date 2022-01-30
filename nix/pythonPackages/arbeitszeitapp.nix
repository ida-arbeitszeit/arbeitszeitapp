{ buildPythonPackage, pytestCheckHook

, injector, hypothesis, flask, flask-talisman, flask_wtf, flask-babel
, flask_login, flask_mail, flask_migrate, email_validator, is_safe_url }:
buildPythonPackage {
  pname = "arbeitszeitapp";
  version = "develop";
  src = ../..;
  buildInputs = [ pytestCheckHook ];
  checkInputs = [ hypothesis ];
  propagatedBuildInputs = [
    injector
    flask
    flask-talisman
    flask_wtf
    flask-babel
    flask_login
    flask_mail
    flask_migrate
    email_validator
    is_safe_url
  ];
}
