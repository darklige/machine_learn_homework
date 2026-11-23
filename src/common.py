"""公共工具：数据装配、时间划分、滚动前向验证、评价指标、DM 检验。"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from features import HORIZONS, build_features, load_daily, make_targets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
WARMUP = 60          # 前 60 天滚动特征不完整，不参与建模
STEP = 30            # 滚动前向验证中每 30 天重训一次
SEED = 42
CLIP = 0.01          # 训练标签截尾分位数


def load_all():
    df = load_daily()
    X, groups = build_features(df)
    Y = make_targets(df)
    X, Y, df = X.iloc[WARMUP:], Y.iloc[WARMUP:], df.iloc[WARMUP:]
    return df, X, Y, groups


def split_points(n, train=0.70, val=0.15):
    """返回验证集、测试集起点在样本中的位置（按时间顺序 70/15/15）。"""
    return int(n * train), int(n * (train + val))


def walk_forward(make_model, X, y, h, start, end, step=STEP, fit_kw=None, proba=False, clip=CLIP):
    """扩展窗口的滚动前向验证。

    在第 T 天重训时，只使用标签在 T-1 天收盘前已经揭晓的样本，即 t <= T-1-h，
    相当于训练集和预测段之间留出 h 天间隔（gap），避免标签重叠泄漏。
    回归任务把训练标签截尾到训练段的 [clip, 1-clip] 分位数，削弱 2025-10 暴跌等极端样本的影响
    （只改训练标签，评估仍用真实值）。
    返回位置 [start, end) 上的预测（Series；proba=True 时为 DataFrame）。
    """
    Xv, yv = X.values, y.values
    out = []
    for T in range(start, end, step):
        tr = np.arange(0, T - h)
        tr = tr[~pd.isna(yv[tr])]
        te = np.arange(T, min(T + step, end))
        ytr = yv[tr].astype(float)
        if not proba and clip:
            ytr = np.clip(ytr, *np.quantile(ytr, [clip, 1 - clip]))
        model = make_model()
        model.fit(Xv[tr], ytr if not proba else yv[tr], **(fit_kw or {}))
        if proba:
            p = model.predict_proba(Xv[te])
            out.append(pd.DataFrame(p, index=X.index[te], columns=model.classes_))
        else:
            out.append(pd.Series(model.predict(Xv[te]), index=X.index[te]))
    return pd.concat(out)


# ---------------- 评价指标 ----------------

def price_from_ret(close, ret):
    return close * np.exp(ret)


def regression_metrics(close, y_true, y_pred):
    """close 为第 t 天价格；y_* 为对数收益率。价格误差指标在价格尺度上计算。"""
    m = y_true.notna() & y_pred.notna()
    c, yt, yp = close[m], y_true[m], y_pred[m]
    pt, pp = price_from_ret(c, yt), price_from_ret(c, yp)
    err = pp - pt
    nz = yt != 0
    da = (np.sign(yp[nz]) == np.sign(yt[nz])).mean() if (yp[nz] != 0).any() else np.nan
    return {
        "MAE": err.abs().mean(),
        "RMSE": np.sqrt((err ** 2).mean()),
        "MAPE%": (err.abs() / pt).mean() * 100,
        "sMAPE%": (2 * err.abs() / (pt.abs() + pp.abs())).mean() * 100,
        "R2_ret": 1 - ((yt - yp) ** 2).sum() / ((yt - yt.mean()) ** 2).sum(),
        "DA": da,
        "n": int(m.sum()),
    }


def dm_test(e1, e2, h, power=2):
    """Diebold-Mariano 检验（Harvey-Leybourne-Newbold 小样本修正）。

    e1、e2 为两个模型的预测误差；负的 DM 统计量表示模型 1 更好。
    返回 (DM 统计量, 双侧 p 值)。
    """
    e1, e2 = np.asarray(e1), np.asarray(e2)
    d = np.abs(e1) ** power - np.abs(e2) ** power
    n = len(d)
    dbar = d.mean()
    # h 步预测误差存在 MA(h-1) 自相关，用 h-1 阶自协方差估计长期方差
    gamma = [np.mean((d[k:] - dbar) * (d[:n - k] - dbar)) for k in range(h)]
    var = (gamma[0] + 2 * sum(gamma[1:])) / n
    if var <= 0:
        var = gamma[0] / n
    dm = dbar / np.sqrt(var)
    hln = np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    stat = dm * hln
    p = 2 * stats.t.sf(np.abs(stat), df=n - 1)
    return stat, p


def save_table(df, name, index=True):
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "tables" / name, encoding="utf-8-sig", index=index)
    return df


__all__ = ["HORIZONS", "load_all", "split_points", "walk_forward", "regression_metrics",
           "dm_test", "save_table", "price_from_ret", "OUT", "SEED", "STEP"]
