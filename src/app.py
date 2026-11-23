"""Streamlit 演示系统：SteamDT CS2 饰品大盘指数预测。

启动：bash run_app.sh（或 streamlit run src/app.py）
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from common import OUT, load_all, split_points  # noqa: E402
from models import add_regime  # noqa: E402

st.set_page_config(page_title="CS2 饰品大盘指数预测", layout="wide")
TAB = OUT / "tables"


@st.cache_data
def data():
    df, X, Y, groups = load_all()
    v0, t0 = split_points(len(X))
    X, centers, regime = add_regime(X, v0)
    return df, X, Y, groups, regime, t0


@st.cache_resource
def model(h):
    return joblib.load(OUT / "models" / f"lgbm_h{h}.pkl")


def preds(h):
    return pd.read_csv(OUT / "predictions" / f"reg_h{h}.csv", parse_dates=["date"], index_col="date")


df, X, Y, groups, regime, t0 = data()
best = {int(k): v for k, v in json.loads((TAB / "reg_best_params.json").read_text())["best_by_val"].items()}

st.title("CS2 饰品大盘指数预测")
st.caption("数据：SteamDT 大盘指数（日收盘，北京时间）。仅用于课程学习，不构成投资建议。")

with st.sidebar:
    h = st.radio("预测时长 h（天）", [1, 7, 30], index=1)
    asof = st.date_input("预测基准日", value=X.index[-1].date(),
                         min_value=X.index[0].date(), max_value=X.index[-1].date())
    show_days = st.slider("历史显示天数", 60, len(df), 365)

asof = pd.Timestamp(asof)
M = model(h)
x = X.loc[[asof], M["columns"]]
c0 = float(df.loc[asof, "close"])
q10, q50, q90 = (float(M[k].predict(x.values)[0]) for k in ("q10", "q50", "q90"))
point = float(M["point"].predict(x.values)[0])
adj = M["cqr_adj"]
lo, hi = c0 * np.exp(q10 - adj), c0 * np.exp(q90 + adj)
# K-Means 的 3 个簇被 2025-10 暴跌主导：0=暴跌、1=暴跌后修复、2=常态（见报告第 3 节）
state = {0: "暴跌状态", 1: "暴跌后修复", 2: "常态"}.get(regime.get(asof), "未知")

k1, k2, k3, k4 = st.columns(4)
k1.metric(f"{asof.date()} 收盘", f"{c0:.2f}")
k2.metric(f"{h} 天后点预测（LightGBM）", f"{c0 * np.exp(point):.2f}", f"{point * 100:+.2f}%")
k3.metric("80% 预测区间", f"{lo:.0f} ~ {hi:.0f}")
k4.metric("K-Means 市场状态", state)
st.caption("注：演示用的最终模型在全部已知标签上训练；选择历史基准日时，该日之后的数据也参与了训练，"
           "只用于展示。严格的样本外表现见“测试集回放”。")

tab1, tab2, tab3, tab4 = st.tabs(["历史与预测", "测试集回放", "模型解释", "模型排行榜"])

with tab1:
    hist = df["close"].loc[:asof].iloc[-show_days:]
    fig = go.Figure()
    fig.add_scatter(x=hist.index, y=hist, name="大盘指数", line=dict(color="#2a6fdb"))
    tgt = asof + pd.Timedelta(days=h)
    fig.add_scatter(x=[asof, tgt], y=[c0, c0 * np.exp(point)], name="点预测",
                    line=dict(color="#f2a33a", dash="dash"), mode="lines+markers")
    fig.add_scatter(x=[asof, tgt, tgt, asof], y=[c0, hi, lo, c0], fill="toself", name="80% 区间",
                    line=dict(width=0), fillcolor="rgba(242,163,58,0.2)")
    after = df["close"].loc[asof:tgt]
    if len(after) > 1:
        fig.add_scatter(x=after.index, y=after, name="实际走势", line=dict(color="#222"))
    fig.update_layout(height=480, margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

with tab2:
    P = preds(h)
    P = P[P["split"] == "test"]
    opts = [c for c in P.columns if c not in ("close", "y", "split") and not c.startswith("Q")]
    sel = st.multiselect("对比模型", opts, default=["Naive(持平)", best[h]] if best[h] in opts else opts[:2])
    tg = P.index + pd.Timedelta(days=h)
    fig = go.Figure()
    fig.add_scatter(x=tg, y=P["close"] * np.exp(P["y"]), name="真实值", line=dict(color="#222", width=2))
    fig.add_scatter(x=tg, y=P["close"] * np.exp(P["Q90_cqr"]), line=dict(width=0), showlegend=False)
    fig.add_scatter(x=tg, y=P["close"] * np.exp(P["Q10_cqr"]), fill="tonexty", line=dict(width=0),
                    name="80% 区间", fillcolor="rgba(42,111,219,0.15)")
    for m in sel:
        fig.add_scatter(x=tg, y=P["close"] * np.exp(P[m]), name=m)
    fig.update_layout(height=480, margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    met = pd.read_csv(TAB / "reg_metrics.csv")
    st.dataframe(met[(met.h == h) & (met.split == "test")].drop(columns=["h", "split"])
                 .sort_values("MAPE%").round(4), width="stretch", hide_index=True)

with tab3:
    import shap
    ex = shap.TreeExplainer(M["point"])
    sv = ex.shap_values(x.values)[0]
    s = pd.Series(sv, index=M["columns"])
    top = s.reindex(s.abs().sort_values(ascending=False).index)[:12][::-1]
    fig = go.Figure(go.Bar(x=top.values * 100, y=[f"{k} = {x.iloc[0][k]:.4g}" for k in top.index],
                           orientation="h", marker_color=np.where(top.values > 0, "#2e9e5b", "#d0342c")))
    fig.update_layout(height=460, title=f"{asof.date()} 的预测由哪些特征推动（SHAP，单位：收益率百分点）",
                      margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, width="stretch")
    st.write(f"基准值（训练集平均预测）{ex.expected_value * 100:+.2f}%，"
             f"加上各特征贡献后得到 {point * 100:+.2f}%。")
    f = TAB / f"shap_group_importance_h{h}.csv"
    if f.exists():
        st.subheader("特征组整体重要性（测试集 mean|SHAP|）")
        st.bar_chart(pd.read_csv(f, index_col=0))

with tab4:
    met = pd.read_csv(TAB / "reg_metrics.csv")
    piv = met[met.split == "test"].pivot(index="model", columns="h", values="MAPE%")
    piv = piv.join((1 - piv / piv.loc["Naive(持平)"]).mul(100).add_prefix("vs持平%_h"))
    st.subheader("回归：测试集 MAPE%（及相对持平基线的降低幅度）")
    st.dataframe(piv.round(3).sort_values(7), width="stretch")
    cls = pd.read_csv(TAB / "cls_metrics.csv")
    st.subheader("方向分类：测试集")
    st.dataframe(cls[cls.split == "test"].pivot(index="model", columns="h", values=["Accuracy", "MacroF1"])
                 .round(3), width="stretch")
    dm = pd.read_csv(TAB / "reg_dm_test.csv")
    st.subheader("Diebold-Mariano 检验（对比持平基线，DM<0 表示模型更好）")
    st.dataframe(dm.round(3), width="stretch", hide_index=True)
