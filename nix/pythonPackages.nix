self: super: {
  arbeitszeitapp = self.callPackage pythonPackages/arbeitszeitapp.nix { };
  is_safe_url = self.callPackage pythonPackages/is_safe_url.nix { };
  werkzeug = super.werkzeug.overrideAttrs (old: {
    postPatch = ''
      substituteInPlace src/werkzeug/_reloader.py \
        --replace "rv = [sys.executable]" "return sys.argv"
    '';
  });
}
