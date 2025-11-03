self: super: {
  arbeitszeitapp = self.callPackage pythonPackages/arbeitszeitapp.nix { };
  flask-restx = self.callPackage pythonPackages/flask-restx.nix { };
  grimp = self.callPackage pythonPackages/grimp.nix { };
  import-linter = self.callPackage pythonPackages/import-linter.nix { };
}
