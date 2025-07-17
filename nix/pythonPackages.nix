self: super: {
  arbeitszeitapp = self.callPackage pythonPackages/arbeitszeitapp.nix { };
  flask-restx = self.callPackage pythonPackages/flask-restx.nix { };
}
