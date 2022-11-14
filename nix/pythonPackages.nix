self: super: {
  arbeitszeitapp = self.callPackage pythonPackages/arbeitszeitapp.nix { };
  flask_profiler = self.callPackage pythonPackages/flask-profiler.nix { };
  is_safe_url = self.callPackage pythonPackages/is_safe_url.nix { };
}
