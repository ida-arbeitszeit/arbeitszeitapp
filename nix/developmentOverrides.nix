self: super: {
  werkzeug = super.werkzeug.overrideAttrs (old: {
    postPatch = ''
      substituteInPlace src/werkzeug/_reloader.py \
        --replace "rv = [sys.executable]" "return sys.argv"
    '';
  });
  mccabe = super.mccabe.overrideAttrs( old: {
    src = super.fetchPypi {
      pname = "mccabe";
      version = "0.6.1";
      sha256 = "3Y0YIoWg/la6zn9FtefRpuvL9STo872H6w8SUnG4gx8=";
    };
    buildInputs = old.buildInputs ++ [self.pytest-runner];
  });
  flake8 = super.flake8.overrideAttrs( old: {
    postPatch = "";
  });
}
