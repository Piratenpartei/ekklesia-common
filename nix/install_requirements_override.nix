{ pkgs, python }:

with pkgs.python37Packages;

self: super: {

  "setuptools-scm" = setuptools_scm;

  "more-babel-i18n" = python.overrideDerivation super."more-babel-i18n" (old: {
    buildInputs = old.buildInputs ++ [ setuptools_scm ];
  });

  "more-browser-session" = python.overrideDerivation super."more-browser-session" (old: {
    buildInputs = old.buildInputs ++ [ setuptools_scm ];
  });

}
