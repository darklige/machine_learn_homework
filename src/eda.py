"""探索性数据分析：描述统计、平稳性检验、自相关、周内效应、事件前后对比。

输出 outputs/tables/eda_*.csv 和 outputs/figures/eda_*.png。
"""
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf, adfuller

from common import OUT, save_table
from features import load_daily, load_events
from plot_style import setup

warnings.filterwarnings("ignore")


def main():
    setup()
    fig_dir = OUT / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    df = load_daily()
    ev = load_events()
    c = df["close"]
    r = np.log(c).diff().dropna()

    # ---- 描述统计 ----
    desc = pd.DataFrame({
        "起始日": [c.index.min().date()], "结束日": [c.index.max().date()], "天数": [len(c)],
        "起始值": [c.iloc[0]], "结束值": [c.iloc[-1]], "最高值": [c.max()], "最高日": [c.idxmax().date()],
        "最低值": [c.min()], "最低日": [c.idxmin().date()],
        "日收益均值%": [r.mean() * 100], "日收益标准差%": [r.std() * 100],
        "年化波动率%": [r.std() * np.sqrt(365) * 100], "偏度": [r.skew()], "峰度": [r.kurt()],
        "|日收益|>5% 天数": [(r.abs() > 0.05).sum()],
    }).T.rename(columns={0: "值"})
    save_table(desc, "eda_summary.csv")

    # ---- 平稳性 ----
    rows = []
    for name, s in (("对数价格", np.log(c)), ("对数收益率", r)):
        stat, p, *_ = adfuller(s.dropna(), autolag="AIC")
        rows.append({"序列": name, "ADF统计量": stat, "p值": p, "结论": "平稳" if p < 0.05 else "非平稳"})
    lb = acorr_ljungbox(r, lags=[1, 7, 30], return_df=True)
    lb2 = acorr_ljungbox(r ** 2, lags=[1, 7, 30], return_df=True)
    for lag in (1, 7, 30):
        rows.append({"序列": f"收益率 Ljung-Box lag={lag}", "ADF统计量": lb.loc[lag, "lb_stat"],
                     "p值": lb.loc[lag, "lb_pvalue"], "结论": "存在自相关" if lb.loc[lag, "lb_pvalue"] < 0.05 else "无显著自相关"})
        rows.append({"序列": f"收益率平方 Ljung-Box lag={lag}", "ADF统计量": lb2.loc[lag, "lb_stat"],
                     "p值": lb2.loc[lag, "lb_pvalue"], "结论": "波动聚集" if lb2.loc[lag, "lb_pvalue"] < 0.05 else "无"})
    save_table(pd.DataFrame(rows), "eda_stationarity.csv", index=False)

    # ---- 周内效应 / 月份 ----
    wd = r.groupby(r.index.dayofweek).agg(["mean", "std", "count"])
    wd.index = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    save_table(wd * [100, 100, 1], "eda_weekday.csv")

    # ---- 事件前后 ----
    rows = []
    lc = np.log(c)
    for _, e in ev[ev["type"].isin(["major", "case_release", "shock", "steam_sale"])].iterrows():
        d = e["date_start"]
        if d - pd.Timedelta(days=14) < c.index.min() or d + pd.Timedelta(days=14) > c.index.max():
            continue
        def at(k):
            return lc.asof(d + pd.Timedelta(days=k))
        rows.append({"事件": e["name"], "类型": e["type"], "日期": d.date(),
                     "前14天涨跌%": (at(-1) - at(-15)) * 100, "后7天涨跌%": (at(6) - at(-1)) * 100,
                     "后14天涨跌%": (at(13) - at(-1)) * 100,
                     "前14天波动%": r[d - pd.Timedelta(days=14):d - pd.Timedelta(days=1)].std() * 100,
                     "后14天波动%": r[d:d + pd.Timedelta(days=13)].std() * 100})
    evt = pd.DataFrame(rows)
    save_table(evt, "eda_event_window.csv", index=False)
    save_table(evt.groupby("类型")[["前14天涨跌%", "后7天涨跌%", "后14天涨跌%", "前14天波动%", "后14天波动%"]]
               .mean().round(3), "eda_event_type_mean.csv")

    # ---- 辅助变量与未来 7 天收益的相关性 ----
    y7 = lc.shift(-7) - lc
    aux = pd.DataFrame({
        "成交额7日变化": np.log(df["turnover"]).diff(7), "成交笔数7日变化": np.log(df["tx_count"]).diff(7),
        "在线人数7日变化(SteamDT)": np.log(df["players_avg"]).diff(7),
        "CS2 上月峰值环比(SteamCharts)": df["sc_players_chg1m"],
        "三角洲上月峰值环比": df["cmp_delta_chg1m"], "漫威争锋上月峰值环比": df["cmp_marvel_chg1m"],
        "PUBG 上月峰值环比": df["cmp_pubg_chg1m"], "Apex 上月峰值环比": df["cmp_apex_chg1m"],
        "CS2 份额": np.log(df["sc_players"] / (df["sc_players"] + sum(
            df[c].fillna(0) for c in df if c.startswith("cmp_") and not c.endswith(("1m", "3m"))))),
        "汇率7日变化": np.log(df["usdcny"]).diff(7),
        "比特币7日变化": np.log(df["btc"]).diff(7), "比特币30日变化": np.log(df["btc"]).diff(30),
        "黄金7日变化": np.log(df["gold"]).diff(7), "黄金30日变化": np.log(df["gold"]).diff(30), "过去7天收益": lc.diff(7), "过去30天收益": lc.diff(30),
        "30日波动率": r.rolling(30).std(),
    })
    corr = pd.DataFrame({"Pearson": aux.corrwith(y7), "Spearman": aux.corrwith(y7, method="spearman")})
    save_table(corr.round(4), "eda_aux_corr_y7.csv")

    # ---- 图 1：指数走势 + 事件 ----
    fig, ax = plt.subplots(2, 1, figsize=(13, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    ax[0].plot(c.index, c, color="#2a6fdb", lw=1.3, label="SteamDT 大盘指数（日收盘）")
    colors = {"major": "#f2a33a", "steam_sale": "#9b9b9b"}
    for _, e in ev[ev["type"].isin(colors)].iterrows():
        ax[0].axvspan(e["date_start"], e["date_end"], color=colors[e["type"]], alpha=0.18, lw=0)
    for _, e in ev[ev["type"].isin(["case_release", "shock"])].iterrows():
        ax[0].axvline(e["date_start"], color="#d0342c" if e["type"] == "shock" else "#2e9e5b", ls="--", lw=1)
    ax[0].plot([], [], color="#f2a33a", lw=6, alpha=0.4, label="Major 赛事")
    ax[0].plot([], [], color="#9b9b9b", lw=6, alpha=0.4, label="Steam 季节特卖")
    ax[0].plot([], [], color="#2e9e5b", ls="--", label="新武器箱")
    ax[0].plot([], [], color="#d0342c", ls="--", label="2025-10-22 汰换规则更新")
    ax[0].legend(loc="upper left", ncol=3, fontsize=9)
    ax[0].set_ylabel("指数")
    ax[0].set_title("SteamDT CS2 饰品大盘指数（2023-11 ~ 2026-11）")
    ax[1].bar(r.index, r * 100, color=np.where(r > 0, "#2e9e5b", "#d0342c"), width=1)
    ax[1].set_ylabel("日收益率 %")
    ax[1].set_ylim(-25, 25)
    fig.tight_layout()
    fig.savefig(fig_dir / "eda_index_events.png", dpi=150)
    plt.close(fig)

    # ---- 图 2：收益率分布 + ACF ----
    fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
    ax[0].hist(r.clip(-0.15, 0.15) * 100, bins=80, color="#2a6fdb", alpha=0.8)
    ax[0].set_title(f"日对数收益率分布（峰度 {r.kurt():.1f}）")
    ax[0].set_xlabel("%")
    for a, s, t in ((ax[1], r, "收益率 ACF"), (ax[2], r ** 2, "收益率平方 ACF（波动聚集）")):
        v = acf(s, nlags=30)[1:]
        a.bar(range(1, 31), v, color="#555")
        a.axhline(1.96 / np.sqrt(len(s)), color="#d0342c", ls="--", lw=1)
        a.axhline(-1.96 / np.sqrt(len(s)), color="#d0342c", ls="--", lw=1)
        a.set_title(t)
        a.set_xlabel("滞后天数")
    fig.tight_layout()
    fig.savefig(fig_dir / "eda_returns_acf.png", dpi=150)
    plt.close(fig)

    # ---- 图 3：辅助变量 ----
    fig, ax = plt.subplots(4, 1, figsize=(13, 10), sharex=True)
    ax[0].plot(df.index, df["turnover"] / 1e6, color="#7b4fd6", lw=1)
    ax[0].set_ylabel("成交额（百万元）")
    ax[0].set_yscale("log")
    ax[1].plot(df.index, df["players_avg"] / 1e4, label="SteamDT 平均在线", lw=1)
    ax[1].plot(df.index, df["sc_players"] / 1e4, label="CS2 上月峰值(SteamCharts)", lw=1, alpha=0.8)
    ax[1].set_ylabel("CS2 在线（万）")
    ax[1].legend(fontsize=9, loc="upper left")
    ax1b = ax[1].twinx()
    names = {"cmp_delta": "三角洲行动", "cmp_marvel": "漫威争锋", "cmp_pubg": "PUBG", "cmp_apex": "Apex",
             "cmp_r6": "彩虹六号", "cmp_ow2": "守望先锋2", "cmp_dota2": "Dota 2"}
    for c, n in names.items():
        if c in df:
            ax1b.plot(df.index, df[c] / 1e4, lw=0.9, ls="--", label=n)
    ax1b.set_ylabel("竞品上月峰值（万）")
    ax1b.legend(fontsize=7, ncol=4, loc="upper right")
    ax[2].plot(df.index, df["usdcny"], color="#c2410c", lw=1)
    ax[2].set_ylabel("USD/CNY")
    ax[3].plot(df.index, df["btc"] / 1e3, color="#f2a33a", lw=1, label="比特币（千美元，左轴）")
    ax[3].set_ylabel("BTC（千美元）")
    ax3b = ax[3].twinx()
    ax3b.plot(df.index, df["gold"], color="#b8860b", lw=1, ls="--", label="伦敦金（美元/盎司，右轴）")
    ax3b.set_ylabel("黄金（美元/盎司）")
    ax[3].legend(loc="upper left", fontsize=9)
    ax3b.legend(loc="lower right", fontsize=9)
    ax[0].set_title("辅助变量：成交额（对数坐标）、CS2 与竞品在线峰值、汇率、比特币与黄金")
    fig.tight_layout()
    fig.savefig(fig_dir / "eda_aux.png", dpi=150)
    plt.close(fig)

    print(desc.to_string())
    print(corr.round(3).to_string())
    print(evt.groupby("类型")[["后7天涨跌%", "后14天涨跌%"]].mean().round(2))


if __name__ == "__main__":
    main()
