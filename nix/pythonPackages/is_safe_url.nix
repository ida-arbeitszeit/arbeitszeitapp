{ buildPythonPackage, fetchPypi }:
buildPythonPackage rec {
  pname = "is_safe_url";
  version = "1.0";
  src = fetchPypi {
    inherit pname version;
    sha256 = "13YYb2h3IR2u/eahjaHfUg3phaWCspPnqiTqHfHNWrs=";
  };
}
