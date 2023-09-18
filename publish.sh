#!/usr/bin/env bash
rm -rf dist/*
python3 -m build
twine upload dist/*
