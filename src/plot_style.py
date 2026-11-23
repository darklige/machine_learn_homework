"""matplotlib 中文字体与统一配色。"""
import matplotlib
from matplotlib import font_manager

CANDIDATES = ["PingFang SC", "Hiragino Sans GB", "Heiti SC", "STHeiti", "Arial Unicode MS",
              "Noto Sans CJK SC", "Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei"]

PALETTE = {"actual": "#222222", "naive": "#9b9b9b", "model": "#2a6fdb", "band": "#2a6fdb",
           "up": "#2e9e5b", "down": "#d0342c", "accent": "#f2a33a"}


def setup():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for path in ("/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/STHeiti Medium.ttc",
                 "/Library/Fonts/Arial Unicode.ttf"):
        try:
            font_manager.fontManager.addfont(path)
        except (FileNotFoundError, RuntimeError):
            pass
    names = {f.name for f in font_manager.fontManager.ttflist}
    font = next((c for c in CANDIDATES if c in names), None)
    if font:
        matplotlib.rcParams["font.sans-serif"] = [font, "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False
    matplotlib.rcParams["axes.spines.top"] = False
    matplotlib.rcParams["axes.spines.right"] = False
    matplotlib.rcParams["axes.grid"] = True
    matplotlib.rcParams["grid.alpha"] = 0.25
    return font
