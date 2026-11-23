"""回归任务：预测 SteamDT 大盘指数未来 h 天（1/7/30）的对数收益率，并换算为价格。

流程：验证集上调参（滚动前向验证）→ 测试集上滚动前向评估 → 融合 → 分位数回归 → DM 检验。
用法：python src/run_regression.py [--trials 30]
"""
import argparse
import json
import warnings

import joblib
import numpy as np
import optuna
import pandas as pd
from lightgbm import LGBMRegressor
from scipy.optimize import minimize

from common import (CLIP, HORIZONS, OUT, SEED, dm_test, load_all, price_from_ret, regression_metrics,
                    save_table, split_points, walk_forward)
from models import MeanReturn, MovingAverage, ZeroReturn, add_regime, lgbm_space, regressors

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)
STACK_ALPHAS = (0.0, 0.03, 0.1, 0.3, 1.0)   # Stacking 权重向等权收缩的强度候选


def mae_ret(y, p):
    m = y.notna()
    return float((y[m] - p[m]).abs().mean())


def tune(name, build, cands, X, y, h, v0, v1, trials):
    """在验证段上选参数，返回 (最优参数, 验证段预测)。"""
    if cands is None:  # LightGBM 用 Optuna
        def obj(trial):
            p = lgbm_space(trial)
            return mae_ret(y.iloc[v0:v1], walk_forward(lambda: build(p), X, y, h, v0, v1))
        study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=SEED))
        study.optimize(obj, n_trials=trials)
        best = {**study.best_params, "subsample_freq": 1}
    else:
        scores = []
        for p in cands:
            pred = walk_forward(lambda: build(p), X, y, h, v0, v1)
            scores.append(mae_ret(y.iloc[v0:v1], pred))
        best = cands[int(np.argmin(scores))]
    return best, walk_forward(lambda: build(best), X, y, h, v0, v1)


def stack_weights(P, y, alpha=1.0):
    """Stacking 元学习器：最小化 MSE/Var(y) + alpha·||w - 1/k||²，约束 w ≥ 0、Σw = 1。

    岭惩罚把权重往等权方向收缩；凸组合约束保证融合结果不会放大任何一个成员的预测。
    除以 Var(y) 是为了让目标函数量级在 1 左右，否则 SLSQP 的默认容差会让它停在初始值。
    """
    k = P.shape[1]
    w0 = np.full(k, 1 / k)
    v = np.var(y)
    obj = lambda w: np.mean((P @ w - y) ** 2) / v + alpha * np.sum((w - w0) ** 2)
    res = minimize(obj, w0, method="SLSQP", bounds=[(0, 1)] * k,
                   constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}],
                   options={"ftol": 1e-10, "maxiter": 500})
    return res.x


def run_h(h, df, X, Y, v0, t0, trials):
    y = Y[f"y{h}"]
    n = len(X)
    v1 = t0 - h               # 验证段标签不能用到测试段价格
    close = df["close"]
    ma_col = list(X.columns).index("ma_gap_7")
    zoo = {
        "Naive(持平)": (lambda p: ZeroReturn(), [{}]),
        "HistMean": (lambda p: MeanReturn(), [{}]),
        "MA7": (lambda p: MovingAverage(ma_col), [{}]),
        **regressors(),
    }
    val_pred, test_pred, params = {}, {}, {}
    for name, (build, cands) in zoo.items():
        best, vp = tune(name, build, cands, X, y, h, v0, v1, trials)
        params[name] = best
        val_pred[name] = vp
        test_pred[name] = walk_forward(lambda: build(best), X, y, h, t0, n)
        print(f"  h={h:>2} {name:<16} val MAE(ret)={mae_ret(y.iloc[v0:v1], vp):.5f} params={best}")
    VP, TP = pd.DataFrame(val_pred), pd.DataFrame(test_pred)

    # ---- 融合：只依据验证集结果选择成员和权重 ----
    base = [c for c in VP.columns if c not in ("Naive(持平)", "HistMean", "MA7")]
    val_mae = {c: mae_ret(y.loc[VP.index], VP[c]) for c in base}
    top = sorted(val_mae, key=val_mae.get)
    w = pd.Series({c: 1 / ((y.loc[VP.index] - VP[c]) ** 2).mean() for c in top[:3]})
    w /= w.sum()
    VP["WeightedAvg(top3)"] = VP[w.index] @ w
    TP["WeightedAvg(top3)"] = TP[w.index] @ w
    members = top[:5]
    # Stacking：权重非负且和为 1（凸组合），没有截距。验证段内前后两半交叉拟合：
    # 用一半拟合权重、在另一半上打分，据此选收缩强度 alpha，验证段预测也用交叉拟合结果，
    # 避免在拟合权重的同一批样本上评估而被高估。测试段用全部验证样本拟合的权重。
    yv = y.loc[VP.index]
    ok = yv.notna().values
    pos = np.arange(len(VP))
    half = ok.nonzero()[0][ok.sum() // 2]
    Pv = VP[members].values
    best_a, best_mse, best_cv = None, np.inf, None
    for a in STACK_ALPHAS:
        cv = np.full(len(VP), np.nan)
        for fit_m, pred_m in ((pos >= half, pos < half), (pos < half, pos >= half)):
            cv[pred_m] = Pv[pred_m] @ stack_weights(Pv[fit_m & ok], yv.values[fit_m & ok], a)
        mse = np.mean((cv[ok] - yv.values[ok]) ** 2)
        if mse < best_mse:
            best_a, best_mse, best_cv = a, mse, cv
    ws = stack_weights(Pv[ok], yv.values[ok], best_a)
    VP["Stacking"] = best_cv
    TP["Stacking"] = TP[members].values @ ws
    params["WeightedAvg(top3)"] = w.round(3).to_dict()
    params["Stacking"] = {"alpha": best_a, **dict(zip(members, ws.round(3).tolist()))}

    # ---- 分位数回归 + 共形校准（CQR）----
    lp = {k: v for k, v in params["LightGBM"].items()}
    q = {}
    for a in (0.1, 0.5, 0.9):
        mk = lambda a=a: LGBMRegressor(objective="quantile", alpha=a, random_state=SEED, verbose=-1, **lp)
        q[a] = (walk_forward(mk, X, y, h, v0, v1), walk_forward(mk, X, y, h, t0, n))
    yv = y.loc[q[0.1][0].index]
    score = np.maximum(q[0.1][0] - yv, yv - q[0.9][0]).dropna()
    adj = float(np.quantile(score, 0.8 * (1 + 1 / len(score))))
    TP["Q10"], TP["Q50"], TP["Q90"] = q[0.1][1], q[0.5][1], q[0.9][1]
    TP["Q10_cqr"], TP["Q90_cqr"] = TP["Q10"] - adj, TP["Q90"] + adj

    # ---- 评价 ----
    rows = []
    for split, P in (("val", VP), ("test", TP)):
        for c in [c for c in P.columns if not c.startswith("Q")]:
            r = regression_metrics(close.loc[P.index], y.loc[P.index], P[c])
            rows.append({"h": h, "split": split, "model": c, **r})
    met = pd.DataFrame(rows)
    yt = y.loc[TP.index]
    m = yt.notna()
    cov = {"raw": ((yt >= TP["Q10"]) & (yt <= TP["Q90"]))[m].mean(),
           "cqr": ((yt >= TP["Q10_cqr"]) & (yt <= TP["Q90_cqr"]))[m].mean(),
           "width_cqr": (TP["Q90_cqr"] - TP["Q10_cqr"])[m].mean()}

    # ---- DM 检验：每个模型 vs 持平基线（测试集，价格误差）----
    c0 = close.loc[TP.index][m]
    pt = price_from_ret(c0, yt[m])
    e0 = price_from_ret(c0, TP.loc[m, "Naive(持平)"]) - pt
    dm = []
    for c in [c for c in TP.columns if not c.startswith("Q") and c != "Naive(持平)"]:
        e1 = price_from_ret(c0, TP.loc[m, c]) - pt
        s_abs, p_abs = dm_test(e1, e0, h, power=1)
        s_sq, p_sq = dm_test(e1, e0, h, power=2)
        dm.append({"h": h, "model": c, "DM_abs": s_abs, "p_abs": p_abs, "DM_sq": s_sq, "p_sq": p_sq})

    best_name = met[(met.split == "val") & ~met.model.isin(["Naive(持平)", "HistMean", "MA7"])] \
        .sort_values("MAPE%").iloc[0]["model"]
    out = pd.DataFrame({"close": close, "y": y}).loc[pd.concat([VP, TP]).index]
    out = out.join(pd.concat([VP.assign(split="val"), TP.assign(split="test")]))
    (OUT / "predictions").mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "predictions" / f"reg_h{h}.csv", encoding="utf-8-sig")
    return met, pd.DataFrame(dm), params, cov, adj, best_name


def fit_final(h, X, Y, params, adj):
    """用全部已知标签训练最终模型（供演示系统做“未来 h 天”预测）。"""
    y = Y[f"y{h}"]
    ok = y.notna().values
    yt = y[ok].clip(*y[ok].quantile([CLIP, 1 - CLIP]))
    lp = params["LightGBM"]
    models = {"point": LGBMRegressor(random_state=SEED, verbose=-1, **lp).fit(X.values[ok], yt)}
    for a in (0.1, 0.5, 0.9):
        models[f"q{int(a * 100)}"] = LGBMRegressor(objective="quantile", alpha=a, random_state=SEED,
                                                   verbose=-1, **lp).fit(X.values[ok], yt)
    models["cqr_adj"] = adj
    models["columns"] = list(X.columns)
    (OUT / "models").mkdir(parents=True, exist_ok=True)
    joblib.dump(models, OUT / "models" / f"lgbm_h{h}.pkl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--horizons", type=int, nargs="*", default=list(HORIZONS))
    args = ap.parse_args()
    df, X, Y, groups = load_all()
    v0, t0 = split_points(len(X))
    X, centers, _ = add_regime(X, v0)
    print(f"样本 {len(X)} 天：训练 {X.index[0].date()}~{X.index[v0 - 1].date()}，"
          f"验证 {X.index[v0].date()}~{X.index[t0 - 1].date()}，测试 {X.index[t0].date()}~{X.index[-1].date()}")
    save_table(centers, "regime_centers.csv")
    mets, dms, allp, covs, best = [], [], {}, {}, {}
    for h in args.horizons:
        met, dm, params, cov, adj, best_name = run_h(h, df, X, Y, v0, t0, args.trials)
        mets.append(met), dms.append(dm)
        allp[h], covs[h], best[h] = params, cov, best_name
        fit_final(h, X, Y, params, adj)
        print(f"  h={h} 验证集最优（按 MAPE）: {best_name}；80% 区间覆盖率 raw={cov['raw']:.3f} cqr={cov['cqr']:.3f}")
    save_table(pd.concat(mets), "reg_metrics.csv", index=False)
    save_table(pd.concat(dms), "reg_dm_test.csv", index=False)
    save_table(pd.DataFrame(covs).T, "reg_interval_coverage.csv")
    (OUT / "tables" / "reg_best_params.json").write_text(
        json.dumps({"best_by_val": best, "params": allp}, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
