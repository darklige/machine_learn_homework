"""模型库：回归 / 分类模型的构造函数与超参数候选。"""
import itertools

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, CatBoostRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.cluster import KMeans
from sklearn.compose import TransformedTargetRegressor
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import (ElasticNet, Lasso, LinearRegression, LogisticRegression, Ridge)
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from xgboost import XGBClassifier, XGBRegressor

from common import SEED


# ---------------- 基线 ----------------

class ZeroReturn(BaseEstimator, RegressorMixin):
    """朴素持平预测：未来价格 = 今天价格，即对数收益率预测为 0。"""

    def fit(self, X, y):
        return self

    def predict(self, X):
        return np.zeros(len(X))


class MeanReturn(BaseEstimator, RegressorMixin):
    """历史均值漂移：预测为训练期平均收益率。"""

    def fit(self, X, y):
        self.mu_ = float(np.mean(y))
        return self

    def predict(self, X):
        return np.full(len(X), self.mu_)


class MovingAverage(BaseEstimator, RegressorMixin):
    """移动平均预测：未来价格 = 过去 7 日均价，ŷ = -ma_gap_7。"""

    def __init__(self, col=None):
        self.col = col

    def fit(self, X, y):
        return self

    def predict(self, X):
        return -X[:, self.col]


def _prep(scale=True):
    steps = [SimpleImputer(strategy="median", add_indicator=True)]
    if scale:
        steps.append(StandardScaler())
    return steps


def grid(**kw):
    keys = list(kw)
    return [dict(zip(keys, v)) for v in itertools.product(*kw.values())]


def regressors(n_jobs=4):
    """返回 {名称: (构造函数(params) -> 模型, 参数候选列表)}。"""
    return {
        "LinearRegression": (lambda p: make_pipeline(*_prep(), LinearRegression()), [{}]),
        "Ridge": (lambda p: make_pipeline(*_prep(), Ridge(**p)), grid(alpha=[1, 10, 100, 1000, 3000])),
        "Lasso": (lambda p: make_pipeline(*_prep(), Lasso(max_iter=20000, **p)),
                  grid(alpha=[1e-4, 3e-4, 1e-3, 3e-3, 1e-2])),
        "ElasticNet": (lambda p: make_pipeline(*_prep(), ElasticNet(max_iter=20000, **p)),
                       grid(alpha=[3e-4, 1e-3, 3e-3, 1e-2], l1_ratio=[0.2, 0.5, 0.8])),
        "KNN": (lambda p: make_pipeline(*_prep(), PCA(n_components=p["pca"], random_state=SEED),
                                        KNeighborsRegressor(n_neighbors=p["k"], weights=p["w"])),
                grid(pca=[5, 10, 20], k=[20, 50, 100], w=["uniform", "distance"])),
        "SVR": (lambda p: TransformedTargetRegressor(
                    make_pipeline(*_prep(), SVR(C=p["C"], epsilon=p["eps"], gamma=p["gamma"])),
                    transformer=StandardScaler()),
                grid(C=[0.03, 0.1, 0.3, 1], eps=[0.1, 0.5], gamma=["scale", 0.003])),
        "DecisionTree": (lambda p: make_pipeline(*_prep(False), DecisionTreeRegressor(random_state=SEED, **p)),
                         grid(max_depth=[2, 3, 4, 6], min_samples_leaf=[20, 50])),
        "RandomForest": (lambda p: make_pipeline(*_prep(False), RandomForestRegressor(
                             n_estimators=300, random_state=SEED, n_jobs=n_jobs, **p)),
                         grid(max_depth=[3, 5, None], min_samples_leaf=[5, 20], max_features=[0.3, "sqrt"])),
        "XGBoost": (lambda p: XGBRegressor(learning_rate=0.03, subsample=0.8, colsample_bytree=0.7,
                                           random_state=SEED, n_jobs=n_jobs, **p),
                    grid(max_depth=[2, 3, 4], n_estimators=[200, 400], min_child_weight=[5, 20])),
        "LightGBM": (lambda p: LGBMRegressor(random_state=SEED, n_jobs=n_jobs, verbose=-1, **p), None),
        "CatBoost": (lambda p: CatBoostRegressor(learning_rate=0.03, random_seed=SEED, verbose=0,
                                                 thread_count=n_jobs, **p),
                     grid(depth=[3, 4, 6], iterations=[300, 600], l2_leaf_reg=[3, 10])),
    }


def classifiers(n_jobs=4):
    return {
        "Logistic": (lambda p: make_pipeline(*_prep(), LogisticRegression(
                         max_iter=5000, class_weight="balanced", **p)),
                     grid(C=[0.003, 0.01, 0.03, 0.1, 1])),
        "KNN": (lambda p: make_pipeline(*_prep(), PCA(n_components=p["pca"], random_state=SEED),
                                        KNeighborsClassifier(n_neighbors=p["k"], weights=p["w"])),
                grid(pca=[5, 10, 20], k=[20, 50, 100], w=["uniform", "distance"])),
        "SVC": (lambda p: make_pipeline(*_prep(), SVC(probability=True, class_weight="balanced",
                                                      random_state=SEED, **p)),
                grid(C=[0.1, 0.3, 1, 3], gamma=["scale", 0.003])),
        "DecisionTree": (lambda p: make_pipeline(*_prep(False), DecisionTreeClassifier(
                             class_weight="balanced", random_state=SEED, **p)),
                         grid(max_depth=[2, 3, 4, 6], min_samples_leaf=[20, 50])),
        "RandomForest": (lambda p: make_pipeline(*_prep(False), RandomForestClassifier(
                             n_estimators=300, class_weight="balanced", random_state=SEED, n_jobs=n_jobs, **p)),
                         grid(max_depth=[3, 5, None], min_samples_leaf=[5, 20], max_features=[0.3, "sqrt"])),
        "XGBoost": (lambda p: XGBClassifier(learning_rate=0.03, subsample=0.8, colsample_bytree=0.7,
                                            random_state=SEED, n_jobs=n_jobs, **p),
                    grid(max_depth=[2, 3, 4], n_estimators=[200, 400], min_child_weight=[5, 20])),
        "LightGBM": (lambda p: LGBMClassifier(random_state=SEED, n_jobs=n_jobs, verbose=-1,
                                              class_weight="balanced", **p), None),
        "CatBoost": (lambda p: CatBoostClassifier(learning_rate=0.03, random_seed=SEED, verbose=0,
                                                  auto_class_weights="Balanced", thread_count=n_jobs, **p),
                     grid(depth=[3, 4, 6], iterations=[300, 600], l2_leaf_reg=[3, 10])),
    }


def lgbm_space(trial):
    """Optuna 贝叶斯优化的 LightGBM 搜索空间。"""
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 800, step=50),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 4, 31),
        "max_depth": trial.suggest_int("max_depth", 2, 6),
        "min_child_samples": trial.suggest_int("min_child_samples", 10, 80),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "subsample_freq": 1,
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.3, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 30, log=True),
    }


def add_regime(X, fit_end, k=3):
    """K-Means 市场状态：用训练段的 30 日波动率、30 日动量、30 日均线偏离度聚类。

    只在 fit_end 之前的样本上拟合，避免使用未来信息。返回带 regime_* 独热列的新 X 和聚类中心表。
    """
    cols = ["vol_30", "mom_30", "ma_gap_30"]
    Z = X[cols]
    ok = Z.notna().all(axis=1)
    fit_mask = ok & (np.arange(len(X)) < fit_end)
    scaler = StandardScaler().fit(Z[fit_mask])
    km = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(scaler.transform(Z[fit_mask]))
    lab = pd.Series(np.nan, index=X.index)
    lab[ok] = km.predict(scaler.transform(Z[ok]))
    # 按 30 日动量从低到高给状态重新编号（0 为动量最低的簇）
    centers = pd.DataFrame(scaler.inverse_transform(km.cluster_centers_), columns=cols)
    order = centers["mom_30"].argsort().argsort().values
    lab = lab.map(lambda v: order[int(v)] if pd.notna(v) else np.nan)
    centers.index = order
    X = X.copy()
    for i in range(k):
        X[f"regime_{i}"] = (lab == i).astype(float).where(lab.notna())
    return X, centers.sort_index(), lab
