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
            overlays = [ self.overlays.default ];
          };
          developmentPkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.development ];
          };
        in {
          devShells.default = developmentPkgs.callPackage nix/devShell.nix { };
          packages = {
            default = pkgs.python3.pkgs.arbeitszeitapp;
            inherit (pkgs) python3;
            arbeitszeitapp-docker-image = pkgs.arbeitszeitapp-docker-image;
          };
          checks = {
            arbeitszeit-python39 = pkgs.python39.pkgs.arbeitszeitapp;
            arbeitszeit-python310 = pkgs.python310.pkgs.arbeitszeitapp;
          };
        });
      systemIndependent = {
        overlays = {
          default = final: prev:
            let
              overridePython = python:
                python.override {
                  packageOverrides = import nix/pythonPackages.nix;
                };
            in {
              python39 = overridePython prev.python39;
              python310 = overridePython prev.python310;
              arbeitszeitapp-docker-image =
                final.callPackage nix/docker.nix { python = final.python3; };
            };
          development = final: prev:
            let
              overridePython = python:
                python.override {
                  packageOverrides = with nixpkgs.lib;
                    composeExtensions (import nix/developmentOverrides.nix)
                    (import nix/pythonPackages.nix);
                };
            in {
              python39 = overridePython prev.python39;
              python310 = overridePython prev.python310;
            };
        };
      };
    in systemDependent // systemIndependent;
}
