"""分类任务：预测大盘指数未来 h 天走势方向（0=跌 / 1=平 / 2=涨）。

阈值 θ_h 取训练段 |y_h| 的 1/3 分位数：|收益| < θ_h 记为“持平”，使训练段三类大致均衡。
用法：python src/run_classification.py [--trials 20]
"""
import argparse
import json
import warnings

import numpy as np
import optuna
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, roc_auc_score

from common import HORIZONS, OUT, SEED, load_all, save_table, split_points, walk_forward
from models import add_regime, classifiers, lgbm_space

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)
CLASSES = [0, 1, 2]


def to_class(r, th):
    return pd.Series(np.where(r > th, 2, np.where(r < -th, 0, 1)), index=r.index).where(r.notna())


class Majority(BaseEstimator, ClassifierMixin):
    """多数类基线：总是预测训练集中最常见的类别。"""

    def fit(self, X, y):
        self.classes_ = np.array(CLASSES)
        cnt = np.bincount(y.astype(int), minlength=3)
        self.p_ = cnt / cnt.sum()
        return self

    def predict_proba(self, X):
        return np.tile(self.p_, (len(X), 1))


class Momentum(BaseEstimator, ClassifierMixin):
    """动量基线：认为未来 h 天的走势与过去 h 天相同。"""

    def __init__(self, col=None, th=None):
        self.col, self.th = col, th

    def fit(self, X, y):
        self.classes_ = np.array(CLASSES)
        return self

    def predict_proba(self, X):
        r = X[:, self.col]
        c = np.where(r > self.th, 2, np.where(r < -self.th, 0, 1))
        return np.eye(3)[c]


def score(y, P):
    m = y.notna()
    yt, P = y[m].astype(int), P[m]
    pred = P.values.argmax(axis=1)
    try:
        auc = roc_auc_score(yt, P.values, multi_class="ovr", average="macro", labels=CLASSES)
    except ValueError:
        auc = np.nan
    return {"Accuracy": accuracy_score(yt, pred), "MacroF1": f1_score(yt, pred, average="macro"),
            "ROC_AUC": auc, "n": int(m.sum())}


def run_h(h, X, Y, v0, t0, trials):
    r = Y[f"y{h}"]
    th = float(r.iloc[:v0].abs().quantile(1 / 3))
    y = to_class(r, th)
    n, v1 = len(X), t0 - h
    mom_col = list(X.columns).index({1: "ret_lag1", 7: "mom_7", 30: "mom_30"}[h])
    zoo = {"Majority": (lambda p: Majority(), [{}]),
           "Momentum": (lambda p: Momentum(mom_col, th), [{}]),
           **classifiers()}
    VP, TP, params = {}, {}, {}
    for name, (build, cands) in zoo.items():
        wf = lambda p, a, b: walk_forward(lambda: build(p), X, y, h, a, b, proba=True).reindex(columns=CLASSES).fillna(0)
        if cands is None:
            def obj(trial):
                p = lgbm_space(trial)
                return score(y.iloc[v0:v1], wf(p, v0, v1))["MacroF1"]
            st = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED))
            st.optimize(obj, n_trials=trials)
            best = {**st.best_params, "subsample_freq": 1}
        else:
            s = [score(y.iloc[v0:v1], wf(p, v0, v1))["MacroF1"] for p in cands]
            best = cands[int(np.argmax(s))]
        params[name] = best
        VP[name], TP[name] = wf(best, v0, v1), wf(best, t0, n)
        print(f"  h={h:>2} {name:<13} val MacroF1={score(y.iloc[v0:v1], VP[name])['MacroF1']:.3f}")
    # 软投票融合：验证集 Macro-F1 最高的 3 个模型
    base = [k for k in VP if k not in ("Majority", "Momentum")]
    top = sorted(base, key=lambda k: -score(y.iloc[v0:v1], VP[k])["MacroF1"])[:3]
    VP["SoftVote(top3)"] = sum(VP[k] for k in top) / 3
    TP["SoftVote(top3)"] = sum(TP[k] for k in top) / 3
    params["SoftVote(top3)"] = top

    rows = []
    for split, P in (("val", VP), ("test", TP)):
        for k, p in P.items():
            rows.append({"h": h, "split": split, "model": k, **score(y.loc[p.index], p)})
    met = pd.DataFrame(rows)
    best_name = met[(met.split == "val") & ~met.model.isin(["Majority", "Momentum"])] \
        .sort_values("MacroF1").iloc[-1]["model"]
    p = TP[best_name]
    m = y.loc[p.index].notna()
    cm = pd.DataFrame(confusion_matrix(y.loc[p.index][m].astype(int), p[m].values.argmax(1), labels=CLASSES),
                      index=["真实_跌", "真实_平", "真实_涨"], columns=["预测_跌", "预测_平", "预测_涨"])
    dist = y.iloc[t0:].value_counts(normalize=True).reindex(CLASSES).round(3).to_dict()
    out = pd.DataFrame({"y_class": y})
    for k, P in TP.items():
        out[f"{k}_pred"] = pd.Series(P.values.argmax(1), index=P.index)
    out.loc[TP[best_name].index].to_csv(OUT / "predictions" / f"cls_h{h}.csv", encoding="utf-8-sig")
    return met, cm, params, th, best_name, dist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--horizons", type=int, nargs="*", default=list(HORIZONS))
    args = ap.parse_args()
    df, X, Y, groups = load_all()
    v0, t0 = split_points(len(X))
    X, _, _ = add_regime(X, v0)
    (OUT / "predictions").mkdir(parents=True, exist_ok=True)
    mets, info = [], {}
    for h in args.horizons:
        met, cm, params, th, best_name, dist = run_h(h, X, Y, v0, t0, args.trials)
        mets.append(met)
        save_table(cm, f"cls_confusion_h{h}.csv")
        info[h] = {"threshold": th, "best_by_val": best_name, "test_class_dist": dist, "params": params}
        print(f"  h={h} 阈值 θ={th:.4f}，验证集最优: {best_name}，测试集类别分布 {dist}")
    save_table(pd.concat(mets), "cls_metrics.csv", index=False)
    (OUT / "tables" / "cls_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
