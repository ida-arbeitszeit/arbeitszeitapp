{
  description = "A very basic flake";

  outputs = { self, nixpkgs, flake-utils }:
    let
      systemDependent = flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlay ];
          };
          python = pkgs.python3;
        in {
          devShell = let
            pythonDeps = with python.pkgs.arbeitszeitapp;
              requiredPythonModules ++ nativeBuildInputs ++ buildInputs;
            pythonEnv =
              python.withPackages (p: with p; [ black isort flake8 mypy ]);
          in pkgs.mkShell { buildInputs = pythonDeps ++ [ pythonEnv ]; };
          defaultPackage = pkgs.python3.pkgs.arbeitszeitapp;
        });
      systemIndependent = {
        overlay = final: prev: {
          python3 = prev.python3.override {
            packageOverrides = import nix/pythonPackages.nix;
          };
        };
      };
    in systemDependent // systemIndependent;
}
