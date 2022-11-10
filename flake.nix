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
        in {
          devShells.default = pkgs.callPackage nix/devShell.nix { };
          packages = {
            default = pkgs.python3.pkgs.arbeitszeitapp;
            inherit (pkgs) python3;
          };
          checks = {
            arbeitszeit-python310 = pkgs.python310.pkgs.arbeitszeitapp;
            arbeitszeit-python39 = pkgs.python39.pkgs.arbeitszeitapp;
          };
        });
      systemIndependent = {
        overlays = {
          # The default overlay provides the arbeitszeitapp to
          # nixpkgs.
          default = final: prev: {
            pythonPackagesExtensions = prev.pythonPackagesExtensions
              ++ [ (import nix/pythonPackages.nix) ];
          };
        };
      };
    in systemDependent // systemIndependent;
}
