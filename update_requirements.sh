#!/bin/sh

pushd python_requirements
python create_requirement_files.py
popd

pushd nix

pypi2nix -V python38 -r ../python_requirements/install_requirements.txt \
  --basename install_requirements \
  -E postgresql_12 -E libffi -E openssl.dev -s setuptools-scm

pypi2nix -V python38 -r ../python_requirements/test_requirements.txt \
  --basename test_requirements

popd