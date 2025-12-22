#!/usr/bin/env bash
set -euo pipefail

# Compile top-level deps into a pinned requirements/base.txt using pip-compile
# Usage: ./scripts/compile_requirements.sh

if ! command -v pip-compile >/dev/null 2>&1; then
  echo "pip-compile not found. Install with: pip install pip-tools"
  exit 1
fi

pip-compile requirements/top_level_deps.in --output-file=requirements/base.txt
echo "Wrote requirements/base.txt"
