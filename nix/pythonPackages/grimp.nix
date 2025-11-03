{
  lib,
  buildPythonPackage,
  fetchPypi,
  rustPlatform,
  typing-extensions,
}:
let
  pypiSource = (builtins.fromJSON (builtins.readFile ./grimp.json));
in
buildPythonPackage rec {
  pname = pypiSource.pname;
  version = pypiSource.version;
  pyproject = true;

  src = fetchPypi pypiSource;

  cargoRoot = "rust";

  cargoDeps = rustPlatform.fetchCargoVendor {
    inherit pname version src;
    sourceRoot = "grimp-${version}/${cargoRoot}";
    hash = "sha256-85MKqQ77mjUdjDZP6pvAN7HQvzaEIukDl7Pl+YS1HSM=";
  };

  nativeBuildInputs = with rustPlatform; [
    cargoSetupHook
    maturinBuildHook
  ];
  propagatedBuildInputs = [
    typing-extensions
  ];
}
