{ dockerTools, python }:
let
  gunicornServer =
    python.withPackages (pkgs: with pkgs; [ arbeitszeitapp gunicorn ]);
  configurationFile =
    "${gunicornServer}/${gunicornServer.sitePackages}/arbeitszeit_flask/production_settings.py";
in dockerTools.buildImage {
  name = "arbeitszeitapp";
  tag = "latest";

  contents = gunicornServer;
  config = {
    Cmd = [ "/bin/gunicorn" "arbeitszeit_flask.wsgi:app" ];
    Env = [ "ARBEITSZEITAPP_CONFIGURATION_PATH=${configurationFile}" ];
  };
}
