# CS2 饰品大盘指数预测（机器学习大作业）

预测目标：SteamDT CS2 饰品大盘指数（https://www.steamdt.com/section?type=BROAD）未来 1 / 7 / 30 天的走势。
只使用经典机器学习模型（线性、KNN、SVM、树模型、梯度提升、融合、分位数回归、K-Means）。

## 快速开始

```bash
# 1. 环境（Python 3.11，uv）
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt

# 2. 复现全部实验（约 25 分钟，M4 CPU）；加 --download 会重新下载原始数据
bash run_all.sh

# 3. 演示系统
bash run_app.sh
```

比特币 / 黄金补充实验（报告第 13 节）：`CS2_EXTRA_GROUPS=btc,gold bash run_all.sh`，会覆盖 `outputs/`，运行前先备份。
已有的各版本结果：`outputs/tables_v1_no_competitor/`、`outputs/tables/`（最终版）、`outputs/tables_v3_btc_gold/`。

macOS 上 LightGBM / XGBoost 需要 OpenMP。脚本会自动借用 scikit-learn 自带的 `libomp.dylib`；
也可以 `brew install libomp`。Linux / A100 开发机上不需要这一步，直接 `python src/xxx.py` 即可。

## 目录

| 路径 | 内容 |
|---|---|
| `data/raw/` | 原始数据（SteamDT 指数/成交/在线人数/更新记录、SteamCharts CS2 与 7 款竞品、汇率、比特币、黄金、手工事件表） |
| `data/processed/daily.csv` | 整合后的日频数据集（北京时间自然日） |
| `src/download_data.py` | 下载原始数据 |
| `src/build_dataset.py` | 清洗、对齐、合并 |
| `src/features.py` | 特征工程（价格、量能、在线人数、竞品、汇率、事件、日历；比特币/黄金可选） |
| `src/common.py` | 时间划分、滚动前向验证、评价指标、DM 检验 |
| `src/models.py` | 模型库、超参数候选、K-Means 市场状态 |
| `src/eda.py` | 探索性数据分析 |
| `src/run_regression.py` | 回归：价格/收益率预测、融合、分位数区间、DM 检验 |
| `src/run_classification.py` | 分类：涨 / 平 / 跌 |
| `src/analysis.py` | 事件冲击、SHAP、回测、扩展区间评估、消融 |
| `src/make_figures.py` | 结果图表 |
| `src/app.py` | Streamlit 演示系统 |
| `outputs/tables/` | 所有结果表（CSV，UTF-8 BOM，可直接用 Excel 打开） |
| `outputs/figures/` | 所有图表 |
| `outputs/predictions/` | 每个模型的逐日预测 |
| `outputs/models/` | 最终 LightGBM 点预测与分位数模型 |
| `报告.md` | 实验报告 |

## 数据划分

建模样本 2024-01-23 ~ 2026-11-22（前 60 天用于计算滚动特征）。按时间 70 / 15 / 15：

- 训练：2024-01-23 ~ 2026-01-15
- 验证（调参、选模型、定融合权重）：2026-01-16 ~ 2026-06-19
- 测试（只用一次）：2026-06-20 ~ 2026-11-22

验证和测试都用扩展窗口的滚动前向验证：每 30 天重训一次，训练样本与预测日之间留出 h 天间隔。
