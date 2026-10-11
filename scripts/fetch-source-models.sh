#!/usr/bin/env bash
set -euo pipefail
# Exact audited snapshot. Only model FBX files and license documents are checked out.
source_dest="${1:-/tmp/anatomy-z-original}"
source_revision='6c7f9016bd5899ac8edafd31b9900c151df42ed6'
if [[ ! -d "$source_dest/.git" ]]; then
  git init "$source_dest"
  git -C "$source_dest" remote add origin https://github.com/LluisV/Z-Anatomy.git
fi
git -C "$source_dest" fetch --depth 1 --filter=blob:none origin "$source_revision"
git -C "$source_dest" checkout FETCH_HEAD -- Resources/Models/FBX Resources/Models/License.txt LICENSE README.md
