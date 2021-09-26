{
  description = "A very basic flake";

  outputs = { self, nixpkgs, flake-utils }:
    let
      systemDependent = flake-utils.lib.eachDefaultSystem (system:
        let pkgs = import nixpkgs { inherit system; };
        in {
          devShell = pkgs.mkShell {
            buildInputs = (with pkgs; [ pkgs.gcc postgresql ])
              ++ (with pkgs.python39.pkgs; [ flake8 ]);
          };
        });
      systemIndependent = { };
    in systemDependent // systemIndependent;
}
