{
  description = "A very basic flake";

  outputs = { self, nixpkgs, flake-utils }:
    let
      systemDependent = flake-utils.lib.eachDefaultSystem (system:
        let pkgs = import nixpkgs { inherit system; };
        in {
          devShell = pkgs.mkShell {
            buildInputs = with pkgs; [ pkgs.gcc postgresql python39 ];
          };
        });
      systemIndependent = { };
    in systemDependent // systemIndependent;
}
