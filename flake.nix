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
          developmentPkgs = pkgs.extend self.overlays.development;
        in {
          devShells.default = developmentPkgs.callPackage nix/devShell.nix { };
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
        overlays = let
          # Unfortunately python.override does not compose. That's why
          # we use overrideScope.  There is an open issue on github
          # about this topic:
          # https://github.com/NixOS/nixpkgs/issues/44426
          overridePython = pythonSelf: overrides:
            pythonSelf // {
              pkgs = pythonSelf.pkgs.overrideScope overrides;
            };
        in {
          # The default overlay provides the arbeitszeitapp to
          # nixpkgs.
          default = final: prev: {
            python310 =
              overridePython prev.python310 (import nix/pythonPackages.nix);
            python39 =
              overridePython prev.python39 (import nix/pythonPackages.nix);
          };
          # The development overrides provide adjustments to nixpkgs
          # that are only necessary for development.
          development = final: prev: {
            python310 = overridePython prev.python310
              (import nix/developmentOverrides.nix);
            python39 = overridePython prev.python39
              (import nix/developmentOverrides.nix);
          };
        };
      };
    in systemDependent // systemIndependent;
}
