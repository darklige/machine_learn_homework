#!/usr/bin/env bash
# 一键复现全部实验。用法：bash run_all.sh [--download]
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
# macOS 上 LightGBM/XGBoost 需要 libomp；没有 Homebrew libomp 时借用 scikit-learn 自带的那一份
SKL_OMP="$(ls -d .venv/lib/python3.*/site-packages/sklearn/.dylibs 2>/dev/null | head -1 || true)"
if [[ "$(uname)" == "Darwin" && -n "$SKL_OMP" ]]; then
  export DYLD_FALLBACK_LIBRARY_PATH="$PWD/$SKL_OMP"
  export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=4
fi
if [[ "${1:-}" == "--download" ]]; then
  $PY src/download_data.py
fi
$PY src/build_dataset.py
$PY src/eda.py
$PY src/run_regression.py
$PY src/run_classification.py
$PY -X faulthandler src/analysis.py
$PY src/make_figures.py
echo "完成。演示系统：bash run_app.sh"
