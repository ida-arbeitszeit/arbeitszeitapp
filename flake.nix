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
        });
      systemIndependent = {
        overlays = {
          default = final: prev: {
            python3 = prev.python3.override {
              packageOverrides = import nix/pythonPackages.nix;
            };
            arbeitszeitapp-docker-image =
              final.callPackage nix/docker.nix { python = final.python3; };
          };
          development = final: prev: {
            python3 = prev.python3.override {
              packageOverrides = with nixpkgs.lib;
                composeExtensions (import nix/developmentOverrides.nix)
                (import nix/pythonPackages.nix);
            };
          };
        };
      };
    in systemDependent // systemIndependent;
}
