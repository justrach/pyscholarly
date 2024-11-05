#!/bin/bash

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Create new distribution builds
python -m build

# Upload to PyPI using twine
python -m twine upload -r pyscholarly dist/*