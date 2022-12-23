self: super: {
  arbeitszeitapp = self.callPackage pythonPackages/arbeitszeitapp.nix { };
  is_safe_url = self.callPackage pythonPackages/is_safe_url.nix { };
  flask-restx = self.callPackage pythonPackages/flask-restx.nix { };
}
