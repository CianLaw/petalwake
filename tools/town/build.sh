#!/usr/bin/env bash
# Rebuild the towns from whatever models exist: plan the lots, fit the ground, pack the geometry.
#   tools/town/build.sh            real models only (unbuilt lots stay empty)
#   STANDIN=1 tools/town/build.sh  fill unbuilt lots with models that do exist (for previews while modelling)
#   MODELS=1 tools/town/build.sh   first run every building and prop script through Blender (a few minutes;
#                                  needed once on a fresh clone, and after changing the kit). BLENDER=<path> to
#                                  name the Blender binary.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=tools/.venv/bin/python
if [ "${MODELS:-}" = "1" ]; then
  BL=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
  ids=$(ls tools/town/buildings tools/town/props | grep '\.py$' | sed 's/\.py$//' | grep -v '^_' | tr '\n' ' ')
  # shellcheck disable=SC2086
  "$BL" -b -P tools/town/make.py -- $ids --quiet
fi
$PY tools/town/layout.py
$PY tools/town/fit_terrain.py
$PY tools/town/assemble.py
