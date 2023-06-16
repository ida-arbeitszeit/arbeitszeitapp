{
  description = "Arbeitszeitapp";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixos-22-11.url = "github:NixOS/nixpkgs/nixos-22.11";
    nixos-23-05.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
    flask-profiler.url = "github:seppeljordan/flask-profiler";
  };

  outputs =
    { self, nixpkgs, flake-utils, flask-profiler, nixos-22-11, nixos-23-05 }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" ];
      systemDependent = flake-utils.lib.eachSystem supportedSystems (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
          pkgs-22-11 = import nixos-22-11 {
            inherit system;
            overlays = [ self.overlays.default ];
          };
          pkgs-23-05 = import nixos-23-05 {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in {
          devShells = {
            default = pkgs.callPackage nix/devShell.nix { };
            nixos-22-11 = pkgs-22-11.callPackage nix/devShell.nix { };
            nixos-23-05 = pkgs-23-05.callPackage nix/devShell.nix { };
          };
          packages = {
            default = pkgs.python3.pkgs.arbeitszeitapp;
            inherit (pkgs) python3;
          };
          checks = {
            arbeitszeit-python311 = pkgs.python311.pkgs.arbeitszeitapp;
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
