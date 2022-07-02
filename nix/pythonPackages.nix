self: super: {
  arbeitszeitapp = self.callPackage pythonPackages/arbeitszeitapp.nix { };
  is_safe_url = self.callPackage pythonPackages/is_safe_url.nix { };

  # flake8 4.0.1 requires mccabe <0.7.  nixpkgs provides 0.7. This is
  # why we use 0.6.1
  mccabe = super.mccabe.overrideAttrs (old: {
    src = self.fetchPypi {
      pname = "mccabe";
      version = "0.6.1";
      sha256 = "3Y0YIoWg/la6zn9FtefRpuvL9STo872H6w8SUnG4gx8=";
    };
    buildInputs = [ self.pytest-runner ];
  });

  # We undo the patch from nixpkgs since we are using the appropriate
  # version of mccabe.
  flake8 = super.flake8.overrideAttrs (old: { postPatch = ""; });
}
