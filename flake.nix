{
  description = "Arbeitszeitapp";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      supportedSystems = [ "x86_64-linux" ];
      systemDependent = flake-utils.lib.eachSystem supportedSystems (system:
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
              psycopg2
              gunicorn
              types-dateutil
              sphinx
            ]) ++ (with pkgs; [ nixfmt ]);
            inputsFrom = [ python.pkgs.arbeitszeitapp ];
          };
          defaultPackage = pkgs.python3.pkgs.arbeitszeitapp;
          packages = {
            inherit python;
            arbeitszeitapp-docker-image = pkgs.arbeitszeitapp-docker-image;
          };
        });
      systemIndependent = {
        overlay = final: prev: {
          python3 = prev.python3.override {
            packageOverrides = import nix/pythonPackages.nix;
          };
          arbeitszeitapp-docker-image =
            prev.callPackage nix/docker.nix { python = final.python3; };
        };
      };
    in systemDependent // systemIndependent;
}
