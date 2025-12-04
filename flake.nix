{
  description = "Arbeitszeitapp";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixos-25-11.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
    flask-profiler.url = "github:seppeljordan/flask-profiler";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      flask-profiler,
      nixos-25-11,
    }:
    let
      supportedSystems = [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      systemDependent = flake-utils.lib.eachSystem supportedSystems (
        system:
        let
          isMacOs = !builtins.isNull (builtins.match ".*-darwin" system);
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
          pkgs-25-11 = import nixos-25-11 {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in
        {
          devShells = rec {
            default = nixos-unstable;
            nixos-25-11 = pkgs-25-11.callPackage nix/devShell.nix { includeGlibcLocales = !isMacOs; };
            nixos-unstable = pkgs.callPackage nix/devShell.nix {
              includeGlibcLocales = !isMacOs;
              nixfmt = pkgs.nixfmt-rfc-style;
            };
            python312 = pkgs.callPackage nix/devShell.nix {
              python3 = pkgs.python312;
              includeGlibcLocales = !isMacOs;
            };
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
            arbeitszeit-python3-nixpkgs-unstable = pkgs.python3.pkgs.arbeitszeitapp;
            arbeitszeit-python312-nixpkgs-unstable = pkgs.python312.pkgs.arbeitszeitapp;
            arbeitszeit-python3-nixpkgs-stable = pkgs-25-11.python3.pkgs.arbeitszeitapp;
            arbeitszeit-python312-nixpkgs-stable = pkgs-25-11.python312.pkgs.arbeitszeitapp;
          };
        }
      );
      systemIndependent = {
        overlays = {
          default =
            let
              ourOverlay = final: prev: {
                pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [ (import nix/pythonPackages.nix) ];
              };
            in
            nixpkgs.lib.composeExtensions ourOverlay flask-profiler.overlays.default;
        };
      };
    in
    systemDependent // systemIndependent;
}
