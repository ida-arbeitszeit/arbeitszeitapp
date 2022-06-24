self: super: {
  werkzeug = super.werkzeug.overrideAttrs (old: {
    postPatch = ''
      substituteInPlace src/werkzeug/_reloader.py \
        --replace "rv = [sys.executable]" "return sys.argv"
    '';
  });
}
