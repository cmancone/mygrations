#!/usr/bin/env bash
# there does not appear to be a way to pass the token at run-time, so build our .pypirc file and delete when done
echo '[pypi]' > ~/.pypirc
echo 'username = __token__' >> ~/.pypirc
echo "password = $(akeyless get-secret-value -n /pypi)" >> ~/.pypirc
python3 -m build
python3 -m twine upload dist/*
rm ~/.pypirc
