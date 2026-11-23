"""补充实验：消融、事件冲击、扩展区间评估、SHAP 解释、模拟回测。

依赖 run_regression.py 的输出（reg_best_params.json、predictions/reg_h*.csv）。
用法：python src/analysis.py
"""
import json
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from lightgbm import LGBMRegressor

from common import CLIP, OUT, SEED, load_all, regression_metrics, save_table, split_points, walk_forward
from models import ZeroReturn, add_regime, regressors
from plot_style import PALETTE, setup

warnings.filterwarnings("ignore")
FIG = OUT / "figures"
SHOCK = pd.Timestamp("2025-10-22")


def load_params():
    info = json.loads((OUT / "tables" / "reg_best_params.json").read_text())
    return {int(k): v for k, v in info["best_by_val"].items()}, \
        {int(k): v for k, v in info["params"].items()}


def builder(name, params):
    if name == "Naive(持平)":
        return lambda: ZeroReturn()
    build, _ = regressors()[name]
    return lambda: build(params[name])


def base_model(best_name, params):
    """融合模型不能直接重训；消融时退回到验证集上表现最好的单模型。"""
    if best_name in regressors():
        return best_name
    w = params.get(best_name, {})
    return max(w, key=w.get) if w else "LightGBM"


# ---------------- 消融实验 ----------------

def ablation(df, X, Y, groups, best, params, v0, t0):
    rows = []
    sets = {"全部特征": []}
    for g in [g for g in ("volume", "players", "competitor", "fx", "btc", "gold", "event", "calendar") if g in groups]:
        sets[f"去掉 {g}"] = groups[g]
    sets["去掉 regime"] = [c for c in X.columns if c.startswith("regime_")]
    sets["仅价格特征"] = [c for c in X.columns if c not in groups["price"]]
    for h in (7, 30):
        y = Y[f"y{h}"]
        models = sorted({"LightGBM", "Ridge", base_model(best[h], params[h])})
        for name in models:
            mk = builder(name, params[h])
            for label, drop in sets.items():
                Xs = X.drop(columns=drop)
                for split, a, b in (("val", v0, t0 - h), ("test", t0, len(X))):
                    p = walk_forward(mk, Xs, y, h, a, b)
                    r = regression_metrics(df["close"].loc[p.index], y.loc[p.index], p)
                    rows.append({"h": h, "model": name, "特征集": label, "split": split,
                                 "n_features": Xs.shape[1], **r})
            print(f"  消融 h={h} {name} 完成")
    res = pd.DataFrame(rows)
    save_table(res, "ablation.csv", index=False)
    return res


# ---------------- 事件冲击 ----------------

def shock_analysis(df, X, Y, groups, params):
    """在 2025-07-01 ~ 2026-01-15 上做每 7 天重训的滚动预测，比较汰换更新前后的误差。"""
    h = 7
    y = Y[f"y{h}"]
    pos = lambda d: int(X.index.searchsorted(pd.Timestamp(d)))
    a, b = pos("2025-07-01"), pos("2026-01-16")
    preds = {"Naive(持平)": walk_forward(lambda: ZeroReturn(), X, y, h, a, b, step=7)}
    lp = params[h]["LightGBM"]
    mk = lambda: LGBMRegressor(random_state=SEED, verbose=-1, **lp)
    preds["LightGBM(全部特征)"] = walk_forward(mk, X, y, h, a, b, step=7)
    preds["LightGBM(无事件特征)"] = walk_forward(mk, X.drop(columns=groups["event"]), y, h, a, b, step=7)
    preds["LightGBM(不截尾标签)"] = walk_forward(mk, X, y, h, a, b, step=7, clip=0)
    P = pd.DataFrame(preds)
    windows = {"更新前 (07-01~10-14)": ("2025-07-01", "2025-10-14"),
               "冲击窗口 (10-15~10-28)": ("2025-10-15", "2025-10-28"),
               "冲击后 1 月 (10-29~11-28)": ("2025-10-29", "2025-11-28"),
               "冲击后 2 月 (11-29~01-15)": ("2025-11-29", "2026-01-15")}
    rows = []
    for w, (s, e) in windows.items():
        idx = P.loc[s:e].index
        for m in P:
            r = regression_metrics(df["close"].loc[idx], y.loc[idx], P.loc[idx, m])
            rows.append({"窗口": w, "模型": m, "MAPE%": r["MAPE%"], "DA": r["DA"], "n": r["n"]})
    res = pd.DataFrame(rows).pivot(index="窗口", columns="模型", values="MAPE%").loc[list(windows)]
    save_table(res.round(3), "shock_mape.csv")
    P.assign(y=y.loc[P.index], close=df["close"].loc[P.index]).to_csv(
        OUT / "predictions" / "shock_h7.csv", encoding="utf-8-sig")
    return res, P


# ---------------- 扩展区间评估 ----------------

def extended_eval(df, X, Y, best, params):
    """2025-01-01 起的滚动前向评估（参数沿用验证集所选，验证段时间与此重叠，结论偏乐观）。"""
    rows = []
    a = int(X.index.searchsorted(pd.Timestamp("2025-01-01")))
    for h in (1, 7, 30):
        y = Y[f"y{h}"]
        names = ["Naive(持平)", "Ridge", "KNN", "SVR", "RandomForest", "LightGBM", "CatBoost"]
        P = pd.DataFrame({n: walk_forward(builder(n, params[h]), X, y, h, a, len(X)) for n in names})
        for period, (s, e) in {"2025H1": ("2025-01-01", "2025-06-30"), "2025H2": ("2025-07-01", "2025-12-31"),
                               "2026H1": ("2026-01-01", "2026-06-30"), "2026H2": ("2026-07-01", "2026-12-31"),
                               "全部": ("2025-01-01", "2026-12-31")}.items():
            idx = P.loc[s:e].index
            for n in names:
                r = regression_metrics(df["close"].loc[idx], y.loc[idx], P.loc[idx, n])
                rows.append({"h": h, "区间": period, "model": n, **r})
        print(f"  扩展评估 h={h} 完成")
    res = pd.DataFrame(rows)
    save_table(res, "extended_eval.csv", index=False)
    return res


# ---------------- SHAP 解释 ----------------

def shap_analysis(X, Y, groups, params, t0):
    """用测试段之前的数据训练 LightGBM，在测试段上计算 SHAP。"""
    out = {}
    for h in (7, 30):
        y = Y[f"y{h}"]
        tr = np.arange(0, t0 - h)
        tr = tr[y.iloc[tr].notna().values]
        yt = y.iloc[tr].clip(*y.iloc[tr].quantile([CLIP, 1 - CLIP]))
        model = LGBMRegressor(random_state=SEED, verbose=-1, **params[h]["LightGBM"]).fit(X.iloc[tr], yt)
        Xte = X.iloc[t0:]
        ex = shap.TreeExplainer(model)
        sv = ex.shap_values(Xte)
        imp = pd.Series(np.abs(sv).mean(0), index=X.columns).sort_values(ascending=False)
        gmap = {c: g for g, cols in groups.items() for c in cols}
        gimp = imp.groupby(lambda c: gmap.get(c, "regime")).sum().sort_values(ascending=False)
        save_table(imp.rename("mean|SHAP|").to_frame(), f"shap_importance_h{h}.csv")
        save_table(gimp.rename("mean|SHAP|").to_frame(), f"shap_group_importance_h{h}.csv")
        # 训练段（含 2025 年上涨与暴跌）上的 SHAP 也存一份，用于对比规律是否稳定
        sv_tr = ex.shap_values(X.iloc[tr])
        save_table(pd.Series(np.abs(sv_tr).mean(0), index=X.columns).sort_values(ascending=False)
                   .rename("mean|SHAP|").to_frame(), f"shap_importance_train_h{h}.csv")

        plt.figure()
        shap.summary_plot(sv, Xte, max_display=15, show=False, plot_size=(9, 6))
        plt.title(f"SHAP 蜂群图（h={h}，测试段）")
        plt.tight_layout()
        plt.savefig(FIG / f"shap_beeswarm_h{h}.png", dpi=150)
        plt.close("all")

        exp = shap.Explanation(sv[-1], ex.expected_value, Xte.iloc[-1].values, feature_names=list(X.columns))
        plt.figure()
        shap.plots.waterfall(exp, max_display=12, show=False)
        plt.title(f"单样本解释：{Xte.index[-1].date()} 对未来 {h} 天收益的预测")
        plt.tight_layout()
        plt.savefig(FIG / f"shap_waterfall_h{h}.png", dpi=150, bbox_inches="tight")
        plt.close("all")

        # 依赖图：最重要的 4 个特征
        fig, ax = plt.subplots(1, 4, figsize=(16, 3.6))
        for a, f in zip(ax, imp.index[:4]):
            j = list(X.columns).index(f)
            a.scatter(Xte[f], sv[:, j], s=8, alpha=0.6, c=PALETTE["model"])
            a.axhline(0, color="#888", lw=0.8)
            a.set_xlabel(f)
            a.set_ylabel("SHAP 值")
        fig.suptitle(f"SHAP 依赖图（h={h}）")
        fig.tight_layout()
        fig.savefig(FIG / f"shap_dependence_h{h}.png", dpi=150)
        plt.close(fig)
        out[h] = (imp, gimp)
        print(f"  SHAP h={h} top5:", list(imp.index[:5]))
    return out


# ---------------- 模拟回测 ----------------

def _perf(ret):
    nav = np.exp(ret.cumsum())
    dd = (nav / nav.cummax() - 1).min()
    sharpe = ret.mean() / ret.std() * np.sqrt(365) if ret.std() > 0 else np.nan
    return {"累计收益%": (nav.iloc[-1] - 1) * 100, "最大回撤%": dd * 100, "年化夏普": sharpe}


def backtest(best):
    """每天收盘根据 7 天预测决定次日是否持有“指数篮子”（只能做多或空仓，不能做空）。

    换仓成本按单边费率计；指数本身不可交易，这里只把它当作“一篮子饰品”的代理，检验信号是否有用。
    """
    P = pd.read_csv(OUT / "predictions" / "reg_h7.csv", parse_dates=["date"], index_col="date")
    P = P[P["split"] == "test"]
    r_next = np.log(P["close"]).diff().shift(-1).dropna()
    rng = np.random.default_rng(SEED)
    rows, navs = [], {}
    strategies = {"买入持有": pd.Series(1.0, index=r_next.index)}
    for m in ("Naive(持平)", "Ridge", "KNN", "LightGBM", best[7]):
        if m in P and m != "Naive(持平)":
            strategies[f"模型信号:{m}"] = (P[m] > 0).astype(float).reindex(r_next.index)
    for cost in (0.0, 0.01, 0.025, 0.13):
        for name, pos in strategies.items():
            turn = pos.diff().abs().fillna(pos.iloc[0])
            ret = pos * r_next + np.log(1 - cost) * turn
            rows.append({"单边费率": cost, "策略": name, "换仓次数": int(turn.sum()), **_perf(ret)})
            if cost == 0.01:
                navs[name] = np.exp(ret.cumsum())
        # 随机策略：与 LightGBM 信号的持仓比例相同，重复 500 次
        p_hold = strategies.get("模型信号:LightGBM", strategies["买入持有"]).mean()
        sims = []
        for _ in range(500):
            pos = pd.Series((rng.random(len(r_next)) < p_hold).astype(float), index=r_next.index)
            turn = pos.diff().abs().fillna(pos.iloc[0])
            sims.append(_perf(pos * r_next + np.log(1 - cost) * turn))
        rows.append({"单边费率": cost, "策略": "随机(500次均值)", "换仓次数": np.nan,
                     **pd.DataFrame(sims).mean().to_dict()})
    res = pd.DataFrame(rows)
    save_table(res, "backtest.csv", index=False)
    pd.DataFrame(navs).to_csv(OUT / "predictions" / "backtest_nav_cost1pct.csv", encoding="utf-8-sig")
    return res


def main():
    setup()
    FIG.mkdir(parents=True, exist_ok=True)
    best, params = load_params()
    df, X, Y, groups = load_all()
    v0, t0 = split_points(len(X))
    X, _, regime = add_regime(X, v0)
    regime.rename("regime").to_csv(OUT / "predictions" / "regime.csv", encoding="utf-8-sig")
    print("[1/5] 事件冲击分析")
    shock, _ = shock_analysis(df, X, Y, groups, params)
    print(shock.round(2).to_string())
    print("[2/5] SHAP")
    shap_analysis(X, Y, groups, params, t0)
    print("[3/5] 模拟回测")
    bt = backtest(best)
    print(bt[bt["单边费率"] == 0.01].round(2).to_string())
    print("[4/5] 扩展区间评估")
    extended_eval(df, X, Y, best, params)
    print("[5/5] 消融实验")
    ablation(df, X, Y, groups, best, params, v0, t0)


if __name__ == "__main__":
    main()
