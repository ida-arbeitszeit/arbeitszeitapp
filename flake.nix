{
  description = "Arbeitszeitapp";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixos-23-11.url = "github:NixOS/nixpkgs/nixos-23.11";
    nixos-24-05.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    flask-profiler.url = "github:seppeljordan/flask-profiler";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      flask-profiler,
      nixos-23-11,
      nixos-24-05,
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
          pkgs-23-11 = import nixos-23-11 {
            inherit system;
            overlays = [ self.overlays.default ];
          };
          pkgs-24-05 = import nixos-24-05 {
            inherit system;
            overlays = [ self.overlays.default ];
          };
        in
        {
          devShells = rec {
            default = nixos-unstable;
            nixos-23-11 = pkgs-23-11.callPackage nix/devShell.nix { includeGlibcLocales = !isMacOs; };
            nixos-24-05 = pkgs-24-05.callPackage nix/devShell.nix { includeGlibcLocales = !isMacOs; };
            nixos-unstable = pkgs.callPackage nix/devShell.nix {
              includeGlibcLocales = !isMacOs;
              nixfmt = pkgs.nixfmt-rfc-style;
            };
            python311 = pkgs.callPackage nix/devShell.nix {
              python3 = pkgs.python311;
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
            arbeitszeit-python311-nixpkgs-unstable = pkgs.python311.pkgs.arbeitszeitapp;
            arbeitszeit-python3-nixpkgs-stable = pkgs-24-05.python3.pkgs.arbeitszeitapp;
            arbeitszeit-python311-nixpkgs-stable = pkgs-24-05.python311.pkgs.arbeitszeitapp;
            arbeitszeit-python3-nixpkgs-old-stable = pkgs-23-11.python3.pkgs.arbeitszeitapp;
            arbeitszeit-python311-nixpkgs-old-stable = pkgs-23-11.python311.pkgs.arbeitszeitapp;
          };
        }
      );
      systemIndependent = {
        overlays = {
          # The default overlay provides the arbeitszeitapp to
          # nixpkgs.
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
