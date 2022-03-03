{
  description = "Arbeitszeitapp";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

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
          devShell = pkgs.mkShell {
            packages = (with python.pkgs; [
              black
              flake8
              mypy
              isort
              types-dateutil
              psycopg2
            ]) ++ (with pkgs; [ nixfmt ]);
            inputsFrom = [ python.pkgs.arbeitszeitapp ];
          };
          defaultPackage = pkgs.python3.pkgs.arbeitszeitapp;
          packages = { inherit python; };
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
