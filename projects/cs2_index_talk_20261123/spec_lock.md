<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-CN
- audience: 机器学习课程的老师和同学，懂基本 ML 概念，多数听说过 CS2 但不了解饰品市场
- objective: 先完整汇报大作业的数据、模型、评估与解释结果（含未达标项），再让听众记住“1 天预测稳定优于基线、7/30 天大幅优势来自单边下跌、外部资产无关而 V 社更新决定价格”，并笑着带走“不赌为赢”
- core_message: 模型有一定精度，但 CS2 饰品价格由 V 社说了算、极易被操盘——不要相信暴富，不赌为赢
- consumption_mode: presentation

## mode
- mode: custom
- mode_references: narrative
- mode_behavior: 以“回合”推进的叙事：先像正常答辩一样交代对象、数据、特征和模型，在结果页抛出“达标了”再立刻反转为“先别急着鼓掌”，随后用外部资产无关、V 社一刀、回测亏损把矛盾推到顶点，最后用作者本人的饰品账单和梗图落到“不赌为赢”；标题是推进剧情的判断句，实验页数字与结论保持严谨，幽默只在标题措辞、旁白式小注和结尾环节。

## visual_style
- visual_style: custom
- visual_style_references: dark-tech
- visual_style_behavior: 深色石板底上的交易终端 / 游戏 HUD：四角细线直角括号框定内容区，左上角等宽字体“ROUND NN”回合标签兼作页码与章节导航，关键数字用等宽大号数字配橙色或红色；实验 PNG 放在浅色“显示器”面板里，面板顶部有窄标题栏；卡片直角或 4 px 微圆角、1 px 边线、无投影，深度只靠同色系渐变和极少量橙色描边光晕；大面积留黑，强调色只落在每页一个焦点。

## colors
- background: #12161C
- secondary_bg: #1C232D
- primary: #F5A623
- accent: #E5484D
- secondary_accent: #4CC2FF
- body_text: #E6EDF3
- secondary_text: #8B98A9
- divider: #2D3742
- surface_light: #F4F6F8
- positive: #3FB950

## typography
- font_family: Microsoft YaHei, Arial, sans-serif
- title_family: Microsoft YaHei, Arial, sans-serif
- body_family: Microsoft YaHei, Arial, sans-serif
- data_family: Consolas, Microsoft YaHei, monospace
- hero_number_family: Consolas, Microsoft YaHei, monospace
- kpi_family: Consolas, Microsoft YaHei, monospace
- body: 28
- title: 44
- subtitle: 32
- lead: 30
- annotation: 20
- footnote: 16
- cover_title: 88
- hero_number: 120
- kpi: 56

## icons
- library: tabler-filled
- inventory: tabler-filled/database, tabler-filled/chart-candle, tabler-filled/chart-dots, tabler-filled/alert-triangle, tabler-filled/coin-bitcoin, tabler-filled/coin-yuan, tabler-filled/coin, tabler-filled/bulb, tabler-filled/trophy, tabler-filled/scale, tabler-filled/calendar-event, tabler-filled/device-gamepad-2, tabler-filled/dice, tabler-filled/circle-check, tabler-filled/circle-x, tabler-filled/flame, tabler-filled/puzzle, tabler-filled/stack-2, tabler-filled/eye, tabler-filled/mood-sad, tabler-filled/shield-check

## images
- p06: images/fig_leaderboard_mape.png | source=user | crop=no-crop
- p08: images/fig_pred_test_all_h.png | source=user | crop=no-crop
- p10: images/fig_shap_beeswarm_h7.png | source=user | crop=no-crop
- p12: images/fig_shock_tradeup.png | source=user | crop=no-crop
- p12_meme: images/meme_this_is_fine.jpg | source=web | crop=adaptive
- p13: images/fig_backtest_nav.png | source=user | crop=no-crop
- p15_bf_sold: images/butterfly_2022_sold.jpeg | source=user | crop=adaptive
- p15_bf_now: images/butterfly_now.jpeg | source=user | crop=adaptive
- p15_m9_sold: images/m9_2022_sold.jpeg | source=user | crop=adaptive
- p15_m9_now: images/m9_now.jpeg | source=user | crop=adaptive
- p15_gl_sold: images/gloves_2022_sold.jpeg | source=user | crop=adaptive
- p15_gl_now: images/gloves_now.jpeg | source=user | crop=adaptive
- p16_drop: images/meme_huanledou_drop.png | source=user | crop=adaptive
- p16_kurumi: images/meme_kurumi.png | source=user | crop=no-crop

## page_rhythm
- P01: anchor
- P02: dense
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: breathing
- P08: dense
- P09: breathing
- P10: dense
- P11: dense
- P12: dense
- P13: dense
- P14: dense
- P15: dense
- P16: breathing
- P17: anchor

## page_visualizations
- P02: chart/line_chart
- P04: chart/horizontal_bar_chart
- P07: chart/grouped_bar_chart
- P11: chart/grouped_bar_chart
- P14: table/record_table

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
