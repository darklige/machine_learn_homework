"""下载原始数据到 data/raw/。

数据来源：
- SteamDT 大盘指数（日频 / 小时频，近 3 年）、在线人数、成交额、CS2 更新记录
- SteamCharts CS2 及竞品游戏在线峰值
- Frankfurter（欧洲央行）USD/CNY 汇率
- btc126 比特币日 K 线、新浪财经伦敦金现货日 K 线

只用标准库，请求间隔 1 秒。用法：python src/download_data.py
"""
import json
import time
import urllib.request
from datetime import date
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124 Safari/537.36")
API = "https://www.steamdt.com/api"


def fetch(url, data=None, referer="https://www.steamdt.com/section?type=BROAD"):
    headers = {"User-Agent": UA, "Referer": referer}
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    time.sleep(1)
    return json.loads(raw)


def save(name, obj):
    (RAW / name).write_text(json.dumps(obj, ensure_ascii=False))
    print("saved", name)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    # 大盘指数：type=2 日频，type=1 小时频；dateType=5 为近 3 年
    save("steamdt_broad_daily_3y.json", fetch(f"{API}/user/statistics/v2/chart?type=2&dateType=5"))
    save("steamdt_broad_hourly_3y.json", fetch(f"{API}/user/statistics/v2/chart?type=1&dateType=5"))
    save("steamdt_players.json", fetch(f"{API}/index/players/trend/v1/all"))
    save("steamdt_transaction.json", fetch(f"{API}/index/transaction/trend/v1/all"))
    page = 1
    while True:
        res = fetch(f"{API}/index/cs2-update-record/v1/page", {"pageNum": page, "pageSize": 20})
        save(f"steamdt_updates_p{page}.json", res)
        total = int(res["data"]["total"])
        if page * 20 >= total:
            break
        page += 1
    # CS2 及竞品游戏（三角洲行动、漫威争锋、PUBG、Apex、彩虹六号、守望先锋 2、Dota 2）的在线峰值
    for app in (730, 2507950, 2767030, 578080, 1172470, 359550, 2357570, 570):
        save(f"steamcharts_{app}.json", fetch(f"https://steamcharts.com/app/{app}/chart-data.json",
                                              referer=f"https://steamcharts.com/app/{app}"))
    # 比特币日 K 线（btc126）与伦敦金现货日 K 线（新浪财经，jsonp 原样保存）
    save("btc126_bitcoin.json", fetch("https://history.btc126.com/api_optimized.php?symbol=bitcoin",
                                      referer="https://history.btc126.com/"))
    req = urllib.request.Request(
        "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20_XAU=/"
        "GlobalFuturesService.getGlobalFuturesDailyKLine?symbol=XAU",
        headers={"User-Agent": UA, "Referer": "https://finance.sina.com.cn/"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        (RAW / "sina_xau.js").write_bytes(resp.read())
    print("saved sina_xau.js")
    end = date.today().isoformat()
    save("fx_usd_cny.json", fetch(f"https://api.frankfurter.app/2023-09-01..{end}?from=USD&to=CNY",
                                  referer="https://www.frankfurter.app/"))


if __name__ == "__main__":
    main()
