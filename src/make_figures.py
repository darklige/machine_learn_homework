"""汇总结果图表：预测对比、预测区间、模型排行榜、事件冲击、消融、回测。"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import OUT
from plot_style import PALETTE, setup

FIG = OUT / "figures"
TAB = OUT / "tables"


def read(name, **kw):
    return pd.read_csv(TAB / name, **kw)


def fig_predictions(best):
    fig, axes = plt.subplots(3, 1, figsize=(13, 10))
    for ax, h in zip(axes, (1, 7, 30)):
        P = pd.read_csv(OUT / "predictions" / f"reg_h{h}.csv", parse_dates=["date"], index_col="date")
        P = P[P["split"] == "test"]
        tgt = P.index + pd.Timedelta(days=h)          # 预测对应的目标日期
        actual = P["close"] * np.exp(P["y"])
        ax.plot(tgt, actual, color=PALETTE["actual"], lw=1.5, label="真实值")
        ax.plot(tgt, P["close"], color=PALETTE["naive"], lw=1, ls="--", label="持平基线")
        m = best[h]
        ax.plot(tgt, P["close"] * np.exp(P[m]), color=PALETTE["model"], lw=1.3, label=f"{m}")
        ax.fill_between(tgt, P["close"] * np.exp(P["Q10_cqr"]), P["close"] * np.exp(P["Q90_cqr"]),
                        color=PALETTE["band"], alpha=0.15, label="80% 区间（LightGBM 分位数 + CQR）")
        ax.set_title(f"测试集：提前 {h} 天预测的大盘指数")
        ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG / "pred_test_all_h.png", dpi=150)
    plt.close(fig)


def fig_leaderboard():
    m = read("reg_metrics.csv")
    m = m[m["split"] == "test"]
    piv = m.pivot(index="model", columns="h", values="MAPE%")
    base = piv.loc["Naive(持平)"]
    rel = (1 - piv / base) * 100
    rel = rel.drop(index=["LinearRegression"], errors="ignore").sort_values(7)
    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(rel))
    for i, h in enumerate((1, 7, 30)):
        ax.barh(y + (i - 1) * 0.27, rel[h], height=0.27, label=f"h={h}")
    ax.axvline(0, color="#333", lw=1)
    ax.axvline(15, color=PALETTE["down"], ls="--", lw=1, label="计划书目标 15%")
    ax.set_yticks(y, rel.index)
    ax.set_xlabel("测试集 MAPE 相对持平基线的降低幅度 %（越大越好）")
    ax.set_title("模型排行榜（LinearRegression 误差过大未画出）")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "leaderboard_mape.png", dpi=150)
    plt.close(fig)


def fig_shock():
    P = pd.read_csv(OUT / "predictions" / "shock_h7.csv", parse_dates=["date"], index_col="date")
    tgt = P.index + pd.Timedelta(days=7)
    fig, ax = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
    ax[0].plot(tgt, P["close"] * np.exp(P["y"]), color=PALETTE["actual"], lw=1.5, label="真实值")
    for c, col in (("Naive(持平)", PALETTE["naive"]), ("LightGBM(全部特征)", PALETTE["model"]),
                   ("LightGBM(不截尾标签)", PALETTE["accent"])):
        ax[0].plot(tgt, P["close"] * np.exp(P[c]), lw=1, color=col, label=c)
    ax[0].axvline(pd.Timestamp("2025-10-22"), color=PALETTE["down"], ls="--")
    ax[0].legend(fontsize=9)
    ax[0].set_title("2025-10-22 汰换规则更新前后：提前 7 天预测")
    for c, col in (("Naive(持平)", PALETTE["naive"]), ("LightGBM(全部特征)", PALETTE["model"])):
        e = (P["close"] * np.exp(P[c]) / (P["close"] * np.exp(P["y"])) - 1).abs() * 100
        ax[1].plot(tgt, e.rolling(7, min_periods=1).mean(), color=col, label=c)
    ax[1].set_ylabel("7 日平均 APE %")
    ax[1].set_yscale("log")
    ax[1].legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "shock_tradeup.png", dpi=150)
    plt.close(fig)


def fig_ablation():
    a = read("ablation.csv")
    a = a[a["split"] == "test"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, h in zip(axes, (7, 30)):
        s = a[a["h"] == h].pivot(index="特征集", columns="model", values="MAPE%")
        s = s.sub(s.loc["全部特征"], axis=1)
        s.drop(index="全部特征").plot.barh(ax=ax)
        ax.axvline(0, color="#333", lw=1)
        ax.set_xlabel("相对全部特征的 MAPE 变化（百分点，>0 说明去掉后变差）")
        ax.set_title(f"消融实验 h={h}（测试集）")
    fig.tight_layout()
    fig.savefig(FIG / "ablation.png", dpi=150)
    plt.close(fig)


def fig_backtest():
    nav = pd.read_csv(OUT / "predictions" / "backtest_nav_cost1pct.csv", parse_dates=[0], index_col=0)
    fig, ax = plt.subplots(figsize=(12, 4.5))
    for c in nav:
        ax.plot(nav.index, nav[c], lw=1.4 if "买入" in c else 1.1, label=c)
    ax.axhline(1, color="#888", lw=0.8)
    ax.set_title("测试集模拟回测（单边费率 1%，只做多/空仓）")
    ax.set_ylabel("净值")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "backtest_nav.png", dpi=150)
    plt.close(fig)


def fig_cls():
    m = read("cls_metrics.csv")
    m = m[m["split"] == "test"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for ax, k in zip(axes, ("Accuracy", "MacroF1")):
        m.pivot(index="model", columns="h", values=k).plot.bar(ax=ax)
        ax.set_title(f"方向分类测试集 {k}")
        ax.axhline(1 / 3, color="#888", ls=":", lw=1)
        ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(FIG / "cls_test_metrics.png", dpi=150)
    plt.close(fig)


def main():
    setup()
    best = {int(k): v for k, v in json.loads((TAB / "reg_best_params.json").read_text())["best_by_val"].items()}
    for fn in (lambda: fig_predictions(best), fig_leaderboard, fig_shock, fig_ablation, fig_backtest, fig_cls):
        fn()
    print("图表已保存到", FIG)


if __name__ == "__main__":
    main()
