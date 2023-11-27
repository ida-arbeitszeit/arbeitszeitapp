{
  description = "Arbeitszeitapp";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixos-23-05.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
    flask-profiler.url = "github:seppeljordan/flask-profiler";
  };

  outputs = { self, nixpkgs, flake-utils, flask-profiler, nixos-23-05 }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" ];
      systemDependent = flake-utils.lib.eachSystem supportedSystems (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
          pkgs-23-05 = import nixos-23-05 {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in {
          devShells = rec {
            default = nixos-unstable;
            nixos-23-05 = pkgs-23-05.callPackage nix/devShell.nix { };
            nixos-unstable = pkgs.callPackage nix/devShell.nix { };
            python310 =
              pkgs.callPackage nix/devShell.nix { python3 = pkgs.python310; };
            python311 =
              pkgs.callPackage nix/devShell.nix { python3 = pkgs.python311; };
          };
          packages = {
            default = pkgs.python3.pkgs.arbeitszeitapp;
            inherit (pkgs) python3;
          };
          checks = {
            # It is okay to have identical versions of python in this
            # list since nix is smart enough to notice and reuse build
            # artifacts. This is why we can test for the system
            # python3 interpreter and also explicitly list all
            # versions we want to support.
            arbeitszeit-python3 = pkgs.python3.pkgs.arbeitszeitapp;
            arbeitszeit-python311 = pkgs.python311.pkgs.arbeitszeitapp;
            arbeitszeit-python310 = pkgs.python310.pkgs.arbeitszeitapp;
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
