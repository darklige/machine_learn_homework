"""特征工程与目标变量。

所有特征只使用截至第 t 天收盘时已知的信息；目标为未来 h 天的对数收益率
y_h(t) = log(P_{t+h}) - log(P_t)。
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HORIZONS = (1, 7, 30)


def load_daily():
    df = pd.read_csv(ROOT / "data" / "processed" / "daily.csv", parse_dates=["date"], index_col="date")
    return df.asfreq("D")


def load_events():
    ev = pd.read_csv(ROOT / "data" / "raw" / "events_manual.csv", parse_dates=["date_start", "date_end"])
    return ev


def _rsi(close, n=14):
    diff = close.diff()
    up = diff.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    down = (-diff.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / down)


def _ratio_log(s, n):
    return np.log(s / s.rolling(n, min_periods=max(2, n // 2)).mean())


def price_features(df):
    c = df["close"]
    lc = np.log(c)
    r = lc.diff()
    f = pd.DataFrame(index=df.index)
    for k in (1, 2, 3, 5, 7, 14, 30):
        f[f"ret_lag{k}"] = r.shift(k - 1)          # ret_lag1 = 当天收益
    for k in (3, 7, 14, 30, 60):
        f[f"mom_{k}"] = lc - lc.shift(k)            # 过去 k 天累计收益
    for k in (7, 14, 30):
        f[f"vol_{k}"] = r.rolling(k).std()
        f[f"skew_{k}"] = r.rolling(k).skew()
    for k in (7, 14, 30, 60):
        f[f"ma_gap_{k}"] = lc - np.log(c.rolling(k).mean())
    f["dd_60"] = lc - np.log(c.rolling(60, min_periods=10).max())
    f["dd_all"] = lc - np.log(c.cummax())
    f["up_60"] = lc - np.log(c.rolling(60, min_periods=10).min())
    f["rsi_14"] = _rsi(c, 14)
    ema12, ema26 = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    macd = (ema12 - ema26) / c
    f["macd"] = macd
    f["macd_hist"] = macd - macd.ewm(span=9, adjust=False).mean()
    ma20, sd20 = c.rolling(20).mean(), c.rolling(20).std()
    f["boll_pos"] = (c - ma20) / (2 * sd20)
    # 小时数据派生的日内特征
    f["range_intraday"] = np.log(df["high"] / df["low"])
    f["rv_intraday"] = df["rv_intraday"]
    f["rv_intraday_7"] = df["rv_intraday"].rolling(7).mean()
    f["close_vs_high"] = np.log(c / df["high"])
    # 不放入原始价格水平：它非平稳，树模型无法外推到训练集没见过的价位
    return f


def volume_features(df):
    f = pd.DataFrame(index=df.index)
    r = np.log(df["close"]).diff()
    for col, name in (("turnover", "to"), ("tx_count", "tx")):
        s = df[col].where(df[col] > 0)
        ls = np.log(s)
        f[f"{name}_chg1"] = ls.diff()
        f[f"{name}_chg7"] = ls - ls.shift(7)
        f[f"{name}_ratio7"] = _ratio_log(s, 7)
        f[f"{name}_ratio30"] = _ratio_log(s, 30)
    f["avg_ticket_ratio30"] = _ratio_log(df["turnover"] / df["tx_count"], 30)
    f["pv_corr_14"] = r.rolling(14).corr(np.log(df["turnover"]).diff())
    return f


def players_features(df):
    f = pd.DataFrame(index=df.index)
    for col, name in (("players_avg", "pl_avg"), ("players_peak", "pl_peak")):
        s = df[col]
        ls = np.log(s)
        f[f"{name}_chg7"] = ls - ls.shift(7)
        f[f"{name}_ratio30"] = _ratio_log(s, 30)
    f["pl_peak_avg_ratio"] = np.log(df["players_peak"] / df["players_avg"])
    # SteamCharts 上月峰值（月度，下月 1 日才可用）
    f["sc_chg1m"] = df["sc_players_chg1m"]
    f["sc_chg3m"] = df["sc_players_chg3m"]
    return f


def _asset_features(df, col, name):
    """另类资产价格：已知最新价相对 1/7/30 天前的变化、30 日波动率、相对 30 日均线、与指数的 30 日相关性。"""
    la = np.log(df[col])
    ra = la.diff()
    r = np.log(df["close"]).diff()
    f = pd.DataFrame(index=df.index)
    f[f"{name}_ret1"] = ra
    f[f"{name}_chg7"] = la - la.shift(7)
    f[f"{name}_chg30"] = la - la.shift(30)
    f[f"{name}_vol30"] = ra.rolling(30).std()
    f[f"{name}_ma_gap30"] = la - np.log(df[col].rolling(30).mean())
    f[f"{name}_corr30"] = r.rolling(30).corr(ra)
    return f


def btc_features(df):
    return _asset_features(df, "btc", "btc")


def gold_features(df):
    return _asset_features(df, "gold", "gold")


COMPETITOR_KEYS = ("delta", "marvel", "pubg", "apex", "r6", "ow2", "dota2")


def competitor_features(df):
    """竞品游戏 Steam 在线峰值（月度）：各自环比变化，CS2 在射击/竞技游戏中的份额。"""
    f = pd.DataFrame(index=df.index)
    keys = [k for k in COMPETITOR_KEYS if f"cmp_{k}" in df]
    for k in keys:
        f[f"cmp_{k}_chg1m"] = df[f"cmp_{k}_chg1m"]
    # 三角洲行动、漫威争锋 2024-12 上线，之前视为 0 人
    total = sum(df[f"cmp_{k}"].fillna(0) for k in keys)
    f["cs2_share"] = np.log(df["sc_players"] / (df["sc_players"] + total))
    f["cs2_share_chg3m"] = f["cs2_share"] - f["cs2_share"].shift(91)
    new = sum(df[f"cmp_{k}"].fillna(0) for k in ("delta", "marvel") if k in keys)
    f["new_rival_ratio"] = new / df["sc_players"]     # 新竞品峰值相对 CS2 的比例
    return f


def fx_features(df):
    lfx = np.log(df["usdcny"])
    return pd.DataFrame({"fx_chg7": lfx - lfx.shift(7), "fx_chg30": lfx - lfx.shift(30)}, index=df.index)


def _days_to(dates, points, future):
    """每个日期到最近（future=True 为下一个，否则为上一个）事件点的天数。"""
    pts = np.sort(np.array(points, dtype="datetime64[D]"))
    d = dates.values.astype("datetime64[D]")
    if future:
        pos = np.searchsorted(pts, d, side="left")
        out = np.full(len(d), np.nan)
        ok = pos < len(pts)
        out[ok] = (pts[pos[ok]] - d[ok]).astype(int)
    else:
        pos = np.searchsorted(pts, d, side="right") - 1
        out = np.full(len(d), np.nan)
        ok = pos >= 0
        out[ok] = (d[ok] - pts[pos[ok]]).astype(int)
    return out


def _active(dates, ev):
    a = np.zeros(len(dates), dtype=int)
    for s, e in zip(ev["date_start"], ev["date_end"]):
        a |= ((dates >= s) & (dates <= e)).astype(int)
    return a


def event_features(df, ev):
    d = df.index
    f = pd.DataFrame(index=d)
    maj = ev[ev["type"] == "major"]
    sale = ev[ev["type"] == "steam_sale"]
    case = ev[ev["type"] == "case_release"]
    f["major_active"] = _active(d, maj)
    f["days_to_major"] = np.clip(_days_to(d, maj["date_start"], True), 0, 120)
    f["days_since_major_end"] = np.clip(_days_to(d, maj["date_end"], False), 0, 180)
    f["sale_active"] = _active(d, sale)
    f["days_to_sale"] = np.clip(_days_to(d, sale["date_start"], True), 0, 90)
    f["days_since_case"] = np.clip(_days_to(d, case["date_start"], False), 0, 240)
    shock = ev.loc[ev["type"] == "shock", "date_start"].min()
    f["post_tradeup"] = (d >= shock).astype(int)
    f["days_since_tradeup"] = np.where(d >= shock, np.clip((d - shock).days, 0, 365), 0)
    f["cn_holiday"] = _active(d, ev[ev["type"] == "cn_holiday"])
    f["upd_high_7d"] = df["upd_high"].rolling(7, min_periods=1).sum()
    f["upd_mid_7d"] = df["upd_mid"].rolling(7, min_periods=1).sum()
    return f


def calendar_features(df):
    # 不放“月份/几号”：样本不足 3 年，树模型会用它们记住具体时段而不是学到可重复的规律
    d = df.index
    return pd.DataFrame({"dow": d.dayofweek, "is_weekend": (d.dayofweek >= 5).astype(int)}, index=d)


GROUPS = {
    "price": price_features,
    "volume": volume_features,
    "players": players_features,
    "competitor": competitor_features,
    "fx": fx_features,
    "btc": btc_features,
    "gold": gold_features,
    "calendar": calendar_features,
}
# 比特币、黄金两组只在补充实验中使用（第 13 节：加入后近两年整体误差变大，未纳入最终模型）。
# 复现该实验：CS2_EXTRA_GROUPS=btc,gold bash run_all.sh
OPTIONAL = {"btc", "gold"}
EXTRA = {g for g in os.environ.get("CS2_EXTRA_GROUPS", "").split(",") if g}


def build_features(df=None, ev=None):
    """返回 (X, groups)，groups 记录每个特征组包含的列名，供消融实验使用。"""
    df = load_daily() if df is None else df
    ev = load_events() if ev is None else ev
    parts, groups = [], {}
    for name, fn in GROUPS.items():
        if name in OPTIONAL and name not in EXTRA:
            continue
        p = fn(df)
        parts.append(p)
        groups[name] = list(p.columns)
    p = event_features(df, ev)
    parts.append(p)
    groups["event"] = list(p.columns)
    X = pd.concat(parts, axis=1).replace([np.inf, -np.inf], np.nan)
    return X, groups


def make_targets(df, horizons=HORIZONS):
    lc = np.log(df["close"])
    return pd.DataFrame({f"y{h}": lc.shift(-h) - lc for h in horizons}, index=df.index)
