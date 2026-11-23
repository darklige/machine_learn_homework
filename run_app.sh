#!/usr/bin/env bash
# 启动 Streamlit 演示系统
set -euo pipefail
cd "$(dirname "$0")"
SKL_OMP="$(ls -d .venv/lib/python3.*/site-packages/sklearn/.dylibs 2>/dev/null | head -1 || true)"
if [[ "$(uname)" == "Darwin" && -n "$SKL_OMP" ]]; then
  export DYLD_FALLBACK_LIBRARY_PATH="$PWD/$SKL_OMP"
  export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=4
fi
.venv/bin/streamlit run src/app.py "$@"
