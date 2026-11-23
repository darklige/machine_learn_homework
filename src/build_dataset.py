"""把 data/raw 中的原始 JSON/CSV 整合为日频数据集 data/processed/daily.csv。

时间统一为北京时间（UTC+8）自然日；指数取每天最后一个小时点作为收盘值，
并由小时数据计算当日最高、最低、日内波动率。当天未收盘的数据会被丢弃。
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
TZ = "Asia/Shanghai"


def load_json(name):
    return json.loads((RAW / name).read_text())


def load_index():
    h = pd.DataFrame(load_json("steamdt_broad_hourly_3y.json")["data"], columns=["ts", "v"])
    h["ts"] = pd.to_datetime(h["ts"].astype(int), unit="s", utc=True).dt.tz_convert(TZ)
    h["v"] = h["v"].astype(float)
    h = h.sort_values("ts").drop_duplicates("ts")
    h["date"] = h["ts"].dt.tz_localize(None).dt.normalize()
    h["logret_h"] = np.log(h["v"]).diff()
    g = h.groupby("date")
    daily = pd.DataFrame({
        "close": g["v"].last(),
        "open": g["v"].first(),
        "high": g["v"].max(),
        "low": g["v"].min(),
        "n_hours": g["v"].size(),
        # 日内已实现波动率：小时对数收益平方和开方
        "rv_intraday": g["logret_h"].apply(lambda s: np.sqrt(np.nansum(s.values ** 2))),
        "last_ts": g["ts"].last(),
    })
    # 用官方日频序列核对收盘值
    d = pd.DataFrame(load_json("steamdt_broad_daily_3y.json")["data"], columns=["ts", "v"])
    d["date"] = (pd.to_datetime(d["ts"].astype(int), unit="s", utc=True)
                 .dt.tz_convert(TZ).dt.tz_localize(None).dt.normalize())
    daily = daily.join(d.set_index("date")["v"].astype(float).rename("close_official"))
    # 丢弃最后一天（未收盘）
    if daily["last_ts"].iloc[-1].hour < 23:
        daily = daily.iloc[:-1]
    daily["close"] = daily["close_official"].fillna(daily["close"])
    return daily.drop(columns=["last_ts", "close_official"])


def load_transaction():
    t = pd.DataFrame(load_json("steamdt_transaction.json")["data"], columns=["date", "turnover", "tx_count"])
    t["date"] = pd.to_datetime(t["date"])
    return t.set_index("date").astype(float)


def load_players():
    p = pd.DataFrame(load_json("steamdt_players.json")["data"], columns=["date", "players_avg", "players_peak"])
    p["date"] = pd.to_datetime(p["date"])
    return p.set_index("date").astype(float)


# SteamCharts 上的竞品游戏（Steam appid）。无畏契约不在 Steam 上，tracker.gg 有 Cloudflare 拦截，未纳入
COMPETITORS = {
    "delta": 2507950,     # 三角洲行动（2024-12 上线 Steam）
    "marvel": 2767030,    # 漫威争锋（2024-12）
    "pubg": 578080,
    "apex": 1172470,
    "r6": 359550,         # 彩虹六号：围攻
    "ow2": 2357570,       # 守望先锋 2（2023-08 上线 Steam）
    "dota2": 570,
}


def load_steamcharts_monthly(appid):
    """SteamCharts 的 chart-data 是同时在线峰值：早期每月一个点，2026-08 末起改为每日峰值、最近一个月为小时值。

    三种粒度的数值不可比（日峰值 < 月峰值，小时值更低），统一成“自然月峰值”：
    每个 UTC 自然月取所有点的最大值；该月结束后（下月 1 日）才可用，避免信息泄漏。
    返回以“可用日期”为索引的序列。
    """
    s = pd.DataFrame(load_json(f"steamcharts_{appid}.json"), columns=["ts", "players"])
    t = pd.to_datetime(s["ts"], unit="ms", utc=True).dt.tz_localize(None)
    m = s.groupby(t.dt.to_period("M"))["players"].max()
    m.index = m.index.to_timestamp() + pd.offsets.MonthBegin(1)
    return m.astype(float)


def load_fx():
    rates = load_json("fx_usd_cny.json")["rates"]
    fx = pd.Series({pd.Timestamp(k): v["CNY"] for k, v in rates.items()}, name="usdcny")
    return fx.sort_index()


def load_btc():
    """btc126 比特币日 K 线：[时间戳(ms), 开, 高, 低, 收, 成交量, 市值]，时间戳为北京时间 0 点。

    无法确认该 K 线是在时间戳时刻收盘还是开盘，按保守口径处理：
    北京时间 D 日 0 点的这根 K 线，到 D+1 日（指数收盘前）一定已经收盘，记到 D+1 日。
    """
    k = pd.DataFrame(load_json("btc126_bitcoin.json")["data"],
                     columns=["ts", "open", "high", "low", "close", "volume", "mcap"])
    d = (pd.to_datetime(k["ts"], unit="ms", utc=True).dt.tz_convert(TZ)
         .dt.tz_localize(None).dt.normalize() + pd.Timedelta(days=1))
    return pd.Series(k["close"].astype(float).values, index=d, name="btc").sort_index()


def load_gold():
    """新浪财经伦敦金现货（XAU/USD）日收盘。D 日收盘在北京时间 D+1 日清晨，记到 D+1 日。"""
    s = (RAW / "sina_xau.js").read_text()
    rows = json.loads(s[s.index("(") + 1:s.rindex(")")])
    g = pd.Series({pd.Timestamp(r["date"]) + pd.Timedelta(days=1): float(r["close"]) for r in rows}, name="gold")
    return g.sort_index()


def load_updates():
    rows = []
    for f in sorted(RAW.glob("steamdt_updates_p*.json")):
        rows += load_json(f.name)["data"]["list"]
    u = pd.DataFrame(rows)
    u["date"] = pd.to_datetime(u["updateTime"]).dt.normalize()
    u = u.drop_duplicates("id")
    u.to_csv(OUT / "cs2_updates.csv", index=False,
             columns=["date", "title", "updateType", "marketImpactLevel", "gameplayImpactLevel"])
    return u


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_index()
    idx = df.index
    df = df.join(load_transaction(), how="left")
    df = df.join(load_players(), how="left")
    # SteamCharts 上月峰值及其环比、3 个月变化：每月 1 日更新一次，其余日期向后填充
    days = pd.date_range("2012-01-01", idx.max())
    for name, app in {"sc_players": 730, **{f"cmp_{k}": v for k, v in COMPETITORS.items()}}.items():
        if not (RAW / f"steamcharts_{app}.json").exists():
            continue
        m = load_steamcharts_monthly(app)
        lm = np.log(m)
        for col, s in ((name, m), (f"{name}_chg1m", lm.diff()), (f"{name}_chg3m", lm.diff(3))):
            df[col] = s.reindex(days).ffill().reindex(idx)
    fx = load_fx().reindex(pd.date_range("2023-09-01", idx.max())).ffill()
    df = df.join(fx, how="left")
    # 比特币（7×24 交易，偶有缺日）、黄金（周末休市）：向后填充到每个自然日
    for load in (load_btc, load_gold):
        if (RAW / {"load_btc": "btc126_bitcoin.json", "load_gold": "sina_xau.js"}[load.__name__]).exists():
            ser = load()
            df[ser.name] = ser.reindex(pd.date_range(ser.index.min(), idx.max())).ffill().reindex(idx)

    # SteamDT 更新记录（2026-04 起）：每天高/中影响更新的数量
    u = load_updates()
    lvl = u.assign(high=(u["marketImpactLevel"] == "高").astype(int),
                   mid=(u["marketImpactLevel"] == "中").astype(int))
    cnt = lvl.groupby("date")[["high", "mid"]].sum()
    df["upd_high"] = cnt["high"].reindex(idx).fillna(0)
    df["upd_mid"] = cnt["mid"].reindex(idx).fillna(0)
    df.loc[df.index < u["date"].min(), ["upd_high", "upd_mid"]] = np.nan

    df.index.name = "date"
    df.to_csv(OUT / "daily.csv")
    miss = df.isna().mean().round(3)
    print(f"daily.csv: {len(df)} 天, {df.index.min().date()} ~ {df.index.max().date()}")
    print("缺失率：\n", miss.to_string())


if __name__ == "__main__":
    main()
