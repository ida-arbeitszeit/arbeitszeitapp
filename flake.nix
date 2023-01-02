{
  description = "Arbeitszeitapp";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixos-stable.url = "github:NixOS/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
    flask-profiler.url = "github:seppeljordan/flask-profiler";
  };

  outputs = { self, nixpkgs, flake-utils, flask-profiler, nixos-stable }:
    let
      supportedSystems = [ "x86_64-linux" ];
      systemDependent = flake-utils.lib.eachSystem supportedSystems (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
          pkgsStable = import nixos-stable {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in {
          devShells = {
            default = pkgs.callPackage nix/devShell.nix { };
            stable = pkgsStable.callPackage nix/devShell.nix { };
          };
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
          default = let
            ourOverlay = final: prev: {
              pythonPackagesExtensions = prev.pythonPackagesExtensions
                ++ [ (import nix/pythonPackages.nix) ];
            };
          in nixpkgs.lib.composeExtensions ourOverlay
          flask-profiler.overlays.default;
        };
      };
    in systemDependent // systemIndependent;
}
