{ usePipenvShell ? true }:
let
  pkgs = import ./requirements/nixpkgs.nix;
in pkgs.stdenv.mkDerivation {
  src = null;
  name = "ekklesia_common-dev-env";
  phases = [];
  buildInputs = with pkgs.python37Packages; [ pkgs.pipenv pkgs.cloc pkgs.zsh python pkgs.postgresql_11 ];
  shellHook = if usePipenvShell then "PYTHONPATH= SHELL=`which zsh` exec pipenv shell --fancy" else "export PYTHONPATH=";
}
