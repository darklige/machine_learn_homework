<!-- ppt-master-schema: design-spec/v1 -->
# CS2 饰品大盘指数预测 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | cs2_index_talk_20261123 |
| Canvas Format | ppt169 (1280 × 720) |
| Page Count | 17 |
| Primary Language | zh-CN |
| Target Audience | 机器学习课程的老师和同学：懂回归/分类/集成学习等基本概念，多数人玩过或听说过 CS2，但不了解饰品市场和 SteamDT 大盘指数 |
| Communication Intent | 先汇报大作业：数据、特征、模型、评估、SHAP 解释与消融等完整流程和真实结果（包括未达标项）；再借结果讲清一个现实结论：这个市场主要被 V 社更新左右，模型只能吃到小而稳的优势，劝大家别把饰品当理财 |
| Desired Audience Outcome | 听众能说出：1 天预测稳定优于持平基线、7/30 天的大幅优势来自单边下跌行情；比特币、黄金等外部资产几乎无关，V 社规则更新才是决定性因素；并带着“不赌为赢”的结论笑着离场 |
| Core Message / Ask / Action | 模型有一定精度（1 天预测显著胜过基线），但 CS2 饰品价格由 V 社说了算、极易被操盘——不要相信暴富，不赌为赢 |
| Delivery Context | 主讲人现场演讲的课程大作业答辩，约 10–15 分钟，风格幽默风趣，可用梗图；会后可能作为作业材料提交 |
| Artifact Afterlife | 作为课程大作业的展示材料提交存档，演讲者会照着 PPT 和备注演讲 |
| Reading Mode | presentation |
| Content Strategy | balanced default（用户留空）：按叙事重组报告内容，事实与数字全部来自 report.md、personal_ideas.md 与用户截图；幽默程度“学术为主，梗点缀”——实验页保持严谨，梗集中在开场、暴跌事件和结尾劝退环节 |
| Design Style | CS2 交易终端：深色底、CS2 橙强调、红色警示、HUD 角标与等宽数字 |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — final Stage-2 proactive policy（用户确认“演讲备注开启”） |
| Custom Animations | disabled — workflow default |
| Narration Audio | disabled — workflow default |
| Created Date | 2026-11-23 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 56 px left/right, 40 px top, 36 px bottom |
| Content Area | x 56–1224, y 40–684 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode References**: narrative
- **Mode Behavior**: 以“回合”推进的叙事：先像正常答辩一样交代对象、数据、特征和模型（情境），在结果页抛出“达标了”再立刻用“先别急着鼓掌”反转（冲突），随后用外部资产无关、V 社一刀、回测亏损把矛盾推到顶点，最后用作者本人的饰品账单和梗图落到“不赌为赢”（解决）。标题写成推进剧情的判断句，实验页的数字与结论保持严谨，幽默只出现在标题措辞、旁白式小注和结尾环节。
- **Visual style**: custom
- **Visual Style References**: dark-tech
- **Visual Style Behavior**: 深色石板底上的“交易终端 / 游戏 HUD”：页面四角用细线直角括号框定内容区，左上角放等宽字体的“ROUND NN”回合标签作为页码与章节导航，关键数字用等宽大号数字配橙色或红色强调；实验 PNG 放在浅色“显示器”面板里，面板顶部有一条窄标题栏；卡片为直角或 4 px 微圆角、1 px 边线、无投影，深度只靠同色系渐变和极少量橙色描边光晕；大面积留黑，强调色只落在每页的一个焦点上。
- **Theme**: CS2 饰品交易终端——像在一块行情屏上复盘一场“开箱”式的市场
- **Tone**: 严谨的数据复盘 + 克制的吐槽；结尾转为真诚劝退

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #12161C | 全局深色底 |
| Secondary background | #1C232D | 卡片、面板、表格底 |
| Primary | #F5A623 | CS2 橙：焦点数字、回合标签、关键强调 |
| Accent | #E5484D | 警示红：暴跌、亏损、未达标、V 社 |
| Secondary accent | #4CC2FF | 数据蓝：模型 / 预测线、次要系列 |
| Body text | #E6EDF3 | 正文 |
| Secondary text | #8B98A9 | 注释、来源、脚注 |
| Divider | #2D3742 | 细线、边框、网格 |
| Surface light | #F4F6F8 | 承载白底实验图和手机截图的“显示器”面板 |
| Positive | #3FB950 | 达标、优于基线 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 粗黑无衬线，干脆 | Microsoft YaHei | Arial | sans-serif |
| Body | 中性无衬线 | Microsoft YaHei | Arial | sans-serif |
| Data | 等宽数字、HUD 标签 | Microsoft YaHei | Consolas | monospace |
| Hero number | 等宽大号数字 | Microsoft YaHei | Consolas | monospace |
| Kpi | 等宽 KPI 数字 | Microsoft YaHei | Consolas | monospace |

- **Title stack**: Microsoft YaHei, Arial, sans-serif
- **Body stack**: Microsoft YaHei, Arial, sans-serif
- **Data stack**: Consolas, Microsoft YaHei, monospace
- **Hero number stack**: Consolas, Microsoft YaHei, monospace
- **Kpi stack**: Consolas, Microsoft YaHei, monospace
- **Role rationale**: Data、Hero number、Kpi 角色承载回合标签、大号数字和表格数值，等宽字体是终端风格的核心识别。

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 28 |
| Title | 44 |
| Subtitle | 32 |
| Lead | 30 |
| Annotation | 20 |
| Footnote | 16 |
| Cover title | 88 |
| Hero number | 120 |
| Kpi | 56 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 左上回合标签 → 判断句标题 → 一个焦点（大数字 / 图 / 截图）→ 右下或底部一句“旁白”小结
- **Composition tendency**: 每页一个主角；数据页常用“左大图右要点”或“上标题下全宽证据”，对比页用左右并排；锚点页大留白
- **Cross-page continuity**: HUD 四角括号、左上“ROUND NN / 章节名”标签、底部细线 + 来源脚注在所有内容页重复；封面的指数折线在结尾以缩小形态回归
- **Spacing posture**: variable by page rhythm；dense 页紧凑但保留 24 px 呼吸，breathing / anchor 页大留白
- **Spacing anchors**: page margin 56, block gap 24, column gutter 32, corner radius 4, body leading 1.4

## VI. Icon Usage Specification

- **Primary bundled library**: tabler-filled

| Icon Path | Suitable Scenarios |
| --- | --- |
| icons/tabler-filled/database.svg | 数据来源 |
| icons/tabler-filled/chart-candle.svg | 行情、指数 |
| icons/tabler-filled/chart-dots.svg | 回归、散点 |
| icons/tabler-filled/alert-triangle.svg | 警示、风险 |
| icons/tabler-filled/coin-bitcoin.svg | 比特币 |
| icons/tabler-filled/coin-yuan.svg | 钱、价格 |
| icons/tabler-filled/coin.svg | 黄金、硬通货 |
| icons/tabler-filled/bulb.svg | 结论、启示 |
| icons/tabler-filled/trophy.svg | 排行榜、最佳 |
| icons/tabler-filled/scale.svg | 对比、检验 |
| icons/tabler-filled/calendar-event.svg | 事件、日历 |
| icons/tabler-filled/device-gamepad-2.svg | 游戏、玩家 |
| icons/tabler-filled/dice.svg | 赌博、随机 |
| icons/tabler-filled/circle-check.svg | 达标 |
| icons/tabler-filled/circle-x.svg | 未达标 |
| icons/tabler-filled/flame.svg | 暴跌、冲击 |
| icons/tabler-filled/puzzle.svg | 特征组 |
| icons/tabler-filled/stack-2.svg | 模型融合 |
| icons/tabler-filled/eye.svg | 解释、SHAP |
| icons/tabler-filled/mood-sad.svg | 亏损情绪 |
| icons/tabler-filled/shield-check.svg | 防泄漏 |

## VII. Visualization Reference List

| Page | Family | Template | Usage |
| --- | --- | --- | --- |
| P02 | chart | line_chart | 三年大盘指数日收盘走势，标出最高点、暴跌日和最新值 |
| P04 | chart | horizontal_bar_chart | 8 个特征组各自的特征数量 |
| P07 | chart | grouped_bar_chart | 同一模型在测试段与近两年整体上相对持平基线的 MAPE 降幅对比 |
| P11 | chart | grouped_bar_chart | 加入比特币/黄金前后 KNN 近两年降幅对比 |
| P14 | table | record_table | 计划书 6 项验收目标、结果与是否达标 |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fig_leaderboard_mape.png | 1500×900 | 1.67 | P06 回归排行榜证据 | Chart screenshot | 浅色显示器面板内完整展示，右侧放验证集选出模型的三个数字 | no-crop | user | Existing | 报告 6.1 节排行榜图 | none | local |
| fig_pred_test_all_h.png | 1950×1500 | 1.30 | P08 测试集 1/7/30 天预测与真实值对比 | Chart screenshot | 左侧大面板完整展示三联图，右侧三个 MAPE 数字纵向排列 | no-crop | user | Existing | 报告 6.3 节预测对比图 | none | local |
| fig_shap_beeswarm_h7.png | 1350×900 | 1.50 | P10 SHAP 蜂群图 | Chart screenshot | 左侧面板完整展示，右侧特征组重要性与解读 | no-crop | user | Existing | 报告第 8 节 h=7 蜂群图 | none | local |
| fig_shock_tradeup.png | 1950×1050 | 1.86 | P12 汰换规则更新前后预测与误差 | Chart screenshot | 宽幅面板占页面主体，梗图作为角落贴纸压在面板边缘外侧 | no-crop | user | Existing | 报告第 11 节事件冲击图 | none | local |
| fig_backtest_nav.png | 1800×675 | 2.67 | P13 回测净值曲线 | Chart screenshot | 全宽横幅面板，下方放费率对比小表 | no-crop | user | Existing | 报告第 12 节回测图 | none | local |
| butterfly_2022_sold.jpeg | 1206×2622 | 0.46 | P15 蝴蝶刀 2022 年卖出订单 ¥4990 | Phone screenshot | 手机竖屏截图，与现价截图成对并排，三对横向排开 | adaptive | user | Existing | BUFF 订单详情，聚焦上半部订单与商品区 | none | local |
| butterfly_now.jpeg | 1206×2622 | 0.46 | P15 蝴蝶刀久经现价 ¥3150 | Phone screenshot | 与卖出截图成对，裁取上半部价格区 | adaptive | user | Existing | BUFF 在售列表，聚焦顶部商品与久经价格 | none | local |
| m9_2022_sold.jpeg | 1206×2622 | 0.46 | P15 M9 刺刀 2022 年卖出 ¥3920 | Phone screenshot | 同上成对展示 | adaptive | user | Existing | BUFF 订单详情上半部 | none | local |
| m9_now.jpeg | 1206×2622 | 0.46 | P15 M9 刺刀久经现价 ¥2337.5 | Phone screenshot | 同上成对展示 | adaptive | user | Existing | BUFF 在售列表顶部 | none | local |
| gloves_2022_sold.jpeg | 1206×2622 | 0.46 | P15 专业手套 2022 年卖出 ¥2600 | Phone screenshot | 同上成对展示 | adaptive | user | Existing | BUFF 订单详情上半部 | none | local |
| gloves_now.jpeg | 1206×2622 | 0.46 | P15 专业手套久经现价 ¥617.5 | Phone screenshot | 同上成对展示 | adaptive | user | Existing | BUFF 在售列表顶部 | none | local |
| meme_huanledou_drop.png | 1206×2622 | 0.46 | P16 无涂装蝴蝶刀近 30 天价格从约 ¥7200 跌到约 ¥5400 | Phone screenshot | 竖屏截图裁取价格走势区，放在左侧手机框中 | adaptive | user | Existing | 悠悠有品价格走势页，聚焦 30 天曲线 | none | local |
| meme_kurumi.png | 850×478 | 1.78 | P16 “老实赚钱，很枯燥吧”梗图 | Meme | 右侧完整展示，下方一句反转旁白 | no-crop | user | Existing | 用户提供的 FX 战士久留美截图，字幕必须完整可见 | none | local |
| meme_this_is_fine.jpg | 1024×1024 | 1.00 | P12 “This is fine”梗图，调侃模型在暴跌中“稳如老狗” | Meme | 小尺寸贴纸，斜放在冲击图右上角外侧 | adaptive | web | Sourced | 经典 KC Green “This is fine” 狗坐在着火房间里喝咖啡的画面，需要可辨认的狗和火焰 | none | local |

## IX. Content Outline

### Part 1: 开局——认识对手

#### Slide 01 - 封面

- **Audience move**: 以为是又一个普通的机器学习作业 → 被“模型说会跌，V 社说了算”勾起好奇
- **Relationships**: none
- **Cover impact**: 钩子“模型说会跌，V 社说了算”；以真实指数三年折线作为背景走势线，终点红色下坠
- **Composition**: 大字钩子居左偏下，完整课题名作副标题，背景一条橙色指数折线横贯，HUD 角标框住整页
- **Title**: 模型说会跌，V 社说了算
- **Core message**: 我们用集成学习预测 CS2 饰品大盘，最后发现真正的变量是开发者
- **Content**: 副标题“基于集成学习的 CS2 饰品大盘指数预测与走势分析” · 课程：机器学习 · 小组：刘同晟（组长）、潘旭、征安杰 · 数据截至 2026-11-22
- **Motion suggestion**: 封面背景折线在 P02 变成正式的指数图（Morph 候选）

#### Slide 02 - 预测对象

- **Audience move**: 不了解 SteamDT 大盘 → 知道它三年里翻倍又腰斩，是厚尾的过山车
- **Relationships**: order — 起点 859.6 → 最高 1747.5 → 2025-10 暴跌 → 最新 607.4
- **Composition**: 全宽指数折线为主角，三个时间点直接标注在线上；右侧或底部一列 KPI
- **Title**: 被预测对象：一台三年过山车
- **Core message**: 指数从 1747.5 的高点跌到 607.4，是三年最低
- **Content**: SteamDT CS2 饰品大盘指数，日收盘 · 2023-11-24 起 859.6 / 2025-05-06 最高 1747.5 / 2026-11-22 收于 607.4（三年最低） · 年化波动率 50% · 日收益偏度 −10.6、峰度 268.5：严重厚尾
- **Visualization**: index-3y 折线，周度采样自 data/processed/daily.csv，标注最高点、2025-10-22 汰换规则更新、最新值
- **Native-ready**: index-3y=no

#### Slide 03 - 任务、数据与划分

- **Audience move**: 不清楚题目边界 → 知道三个任务、七类数据源和严格的时间划分
- **Relationships**: membership — 三个任务（回归 / 分类 / 解释）；order — 训练 → 验证 → 测试 三段时间顺序
- **Composition**: 上半三张任务卡并排，下半一条时间轴分三段并标注天数；数据源作为小标签串在中间
- **Title**: 三个任务，一条时间线
- **Core message**: 只用历史预测未来，测试集只在最后看一次
- **Content**: 回归：预测 h=1/7/30 天后的对数收益率再换算价格 · 分类：未来 h 天 跌/平/涨 · 解释：SHAP、消融、事件窗口 · 数据：SteamDT 大盘（日+小时）/ 成交额与笔数 / 在线人数 / SteamCharts 7 款竞品 / USD-CNY / 事件表（Major、新箱子、特卖、节假日、汰换更新） · 训练 2024-01-23~2026-01-15（724 天）/ 验证 ~2026-06-19（155 天）/ 测试 ~2026-11-22（156 天） · 扩展窗口滚动前向，每 30 天重训，训练与预测间留 h 天间隔防标签泄漏

#### Slide 04 - 特征工程

- **Audience move**: 以为特征越多越好 → 看到 75 个特征的构成，也知道我们主动删掉了“背日历”的特征
- **Relationships**: membership — 8 个特征组构成全部特征；contrast — 保留的特征 vs 删除的“几号”
- **Composition**: 左侧横向条形图展示各组数量，右侧一张“踩坑记录”卡
- **Title**: 75 个特征，和一个被开除的“几号”
- **Core message**: 价格自身特征占大头；会让树模型记住具体日期的特征要删掉
- **Content**: price 33 · event 11 · volume 10 · competitor 10 · players 7 · regime 3（K-Means）· fx 2 · calendar 2 · 只用收益率和比率，不放价格水平 · 踩坑：“几号”曾在 h=7 SHAP 排第 2——样本不足 3 年，模型在背日历，删 · K-Means 本想分“跌/震荡/涨”，结果只分出“暴跌 / 暴跌后修复 / 常态”
- **Visualization**: feature-groups 横向条形图，8 组特征数量
- **Native-ready**: feature-groups=yes

#### Slide 05 - 模型阵容

- **Audience move**: 不知道用了哪些模型 → 看到从基线到融合的完整阵容和“只看验证集”的选择规则
- **Relationships**: order — 基线 → 线性 → 近邻/核 → 树 → 梯度提升 → 融合 → 区间；link — 所有选择只依据验证集
- **Composition**: 一条从左到右的“段位”阶梯，每级列出模型名；底部一条旁白讲 Stacking 翻车
- **Title**: 十五个模型，从“摆烂”到“融合”
- **Core message**: 只用经典机器学习，所有调参和选模只看验证集
- **Content**: 基线：持平（ŷ=0）/ 历史均值漂移 / 7 日均线 · 线性：线性回归、Ridge、Lasso、ElasticNet · PCA+KNN · SVR · 决策树、随机森林 · XGBoost、LightGBM（Optuna）、CatBoost · 融合：加权平均、Stacking（凸组合） · 区间：LightGBM 分位数 + CQR 校准 · 翻车记录：第一版 Stacking 给 KNN 系数 3.1，h=7 比持平还差 29%，改成凸组合后恢复正常

### Part 2: 对局——结果与反转

#### Slide 06 - 回归排行榜

- **Audience move**: 想知道模型行不行 → 看到验证集选出的模型全部超过 15% 目标且 DM 显著
- **Relationships**: contrast — 各模型 vs 持平基线；membership — h=1/7/30 三个时长
- **Composition**: 左侧排行榜图，右侧三张 KPI 卡（时长、模型、降幅、p 值）
- **Title**: 达标了！……吗？
- **Core message**: 按验证集选出的模型，三个时长都比持平基线低 15% 以上
- **Content**: h=1 加权平均 MAPE 0.498%，降 15.7%，DM p=0.000 · h=7 KNN 1.690%，降 30.5%，p=0.001 · h=30 KNN 3.878%，降 52.7%，p<0.001 · 计划书目标：7 天降幅 ≥15% · 线性回归误差过大未画出
- **Images**: fig_leaderboard_mape.png

#### Slide 07 - 先别急着鼓掌

- **Audience move**: 以为模型很强 → 明白大幅优势来自测试段的单边下跌，换到近两年整体只剩 4%~10%
- **Relationships**: contrast — 测试段降幅 vs 近两年整体降幅（同一模型）
- **Composition**: 主体为成组条形图，测试段橙色、近两年灰蓝；右侧一句结论“模型学会了一句话：继续跌”
- **Title**: 先别急着鼓掌
- **Core message**: 测试段是单边下跌，模型只要学会“继续跌”就能大胜；近两年整体只小幅领先
- **Content**: 随机森林 h=1：测试段 16.5% vs 近两年 4.4% · KNN h=7：30.5% vs 6.2% · KNN h=30：52.7% vs 10.1% · 测试段指数 918 → 607，81% 的 7 天收益为负 · KNN 方向准确率 h=7 85.2%、h=30 100% · 含暴跌的 2025H2，h=30 KNN 比持平还差 3.8%
- **Visualization**: gain-compare 成组条形图，3 个类别 × 2 个系列
- **Native-ready**: gain-compare=yes

#### Slide 08 - 越近越准

- **Audience move**: 怀疑模型完全没用 → 认识到短期预测确实有精度，误差随时长明显变大
- **Relationships**: order — h=1 → h=7 → h=30 误差递增
- **Composition**: 左侧大面板放三联预测图，右侧三个递增的 MAPE 数字，下方一句区间覆盖率小注
- **Title**: 越近越准：1 天误差只有 0.5%
- **Core message**: 1 天预测比 7 天、30 天准得多，说明模型本身有一定精度
- **Content**: 测试 MAPE：h=1 0.50% · h=7 1.69% · h=30 3.88% · 80% 预测区间校准后覆盖率 88.4% / 92.6% / 91.3%，目标 75%~85%，偏宽 · h=1 多数树模型与融合模型比持平低 14%~17%，DM 显著
- **Images**: fig_pred_test_all_h.png

#### Slide 09 - 方向分类

- **Audience move**: 期待分类能判断涨跌 → 发现最强分类器还不如“闭眼喊跌”
- **Relationships**: contrast — 随机森林 vs “永远预测跌”；contrast — 实际 Macro-F1 vs 目标 0.55
- **Composition**: 左右两个大数字对擂（66.4% vs 73.8%），下方一行混淆矩阵要点
- **Title**: 最强分类器：闭眼喊跌
- **Core message**: 分类模型能认出“跌”，对“涨”和“平”基本没有区分能力
- **Content**: h=7 验证集选出随机森林：准确率 66.4%，Macro-F1 0.292 · “永远预测跌”：准确率 73.8% · 目标 Macro-F1 ≥ 0.55，未达标 · 混淆矩阵：真实“跌”110 天判对 98 天 / “平”25 天全错 / “涨”14 天只对 1 天 · h=1 上最简单的动量基线 Macro-F1 最高（0.445）
- **Visualization**: 两个对擂 KPI 与一行混淆矩阵数字，页面内绘制，不作为独立图表

#### Slide 10 - SHAP 解释

- **Audience move**: 想知道模型看重什么 → 知道价格、事件真正有用，竞品特征的高分多半是“记住了月份”
- **Relationships**: contrast — 可信规律 vs 可疑的竞品重要性；membership — 特征组重要性排序
- **Composition**: 左侧蜂群图面板，右侧上半特征组重要性迷你条，下半两栏“可信 / 可疑”
- **Title**: 模型在看什么？别全信
- **Core message**: 价格自身和事件特征最有用；竞品特征重要性很可能是虚假关系
- **Content**: h=7 mean|SHAP|：competitor 0.0131 · price 0.0106 · event 0.0080 · volume 0.0008 · players 0.0004 · fx 0.0001 · 可信：汰换规则更新后长期下行 / 波动率高→未来收益低，深度回撤后有反弹 / 临近 Steam 特卖为正、Major 后为负（弱证据） · 可疑：竞品特征每月才更新，训练段 cmp_marvel_chg1m 只有 12 个取值，无单调关系，方向反直觉（竞品越强 CS2 越涨），消融在验证段与测试段 4 处结论相反
- **Images**: fig_shap_beeswarm_h7.png

#### Slide 11 - 比特币与黄金

- **Audience move**: 以为饰品像另类资产会跟着币圈、金价走 → 知道它们几乎无关，加进去反而变差
- **Relationships**: contrast — 加入前 vs 加入后；contrast — 比特币 vs 黄金
- **Composition**: 左侧两个近零相关系数作为大数字，右侧成组条形图对比加入前后
- **Title**: 币圈和金价：跟 CS2 不熟
- **Core message**: CS2 饰品市场与加密资产、贵金属基本脱钩，最终模型不纳入这两组特征
- **Content**: 同日收益相关：比特币 −0.023，黄金 0.013 · 加入后 h=7 KNN 测试降幅 30.5% → 25.7%，DM p 0.001 → 0.074（不再显著） · 近两年整体：KNN h=7 6.2% → 5.3%，h=30 10.1% → 5.4% · 黄金：去掉后验证误差 6 个组合全部下降，整体有害 · 唯一变好：未校准区间覆盖率落入 75%~85%
- **Visualization**: btc-gold-effect 成组条形图，KNN h=7 / h=30 两类 × 加入前 / 加入后
- **Native-ready**: btc-gold-effect=yes

### Part 3: 真正的庄家

#### Slide 12 - V 社一刀

- **Audience move**: 以为市场由供需和情绪决定 → 亲眼看到一次规则更新让所有模型同时失效
- **Relationships**: order — 更新前 → 冲击两天 → 反弹 → 长期下行；contrast — 冲击窗口内各模型误差都在 57%~59%
- **Composition**: 宽幅冲击图为主体，左上叠两个红色大数字（两天跌幅），右上角贴“This is fine”梗图
- **Title**: 2025-10-22：V 社一刀
- **Core message**: 汰换规则更新没有任何预告，模型无法预测；决定价格的是开发者
- **Content**: 汰换规则更新（玩家俗称“5 合 1”） · 10-23、10-24 对数收益 −57.9%、−35.8%，10-25 反弹 +31.2% · 冲击窗口 h=7 MAPE：持平 56.99%，LightGBM 58.35% · 之后一个月反弹到约 1300，再一路跌到 607，比更新前的 1660 低 63% · 事件特征只能帮模型在冲击后稍快适应
- **Images**: fig_shock_tradeup.png；meme_this_is_fine.jpg 作为角落贴纸

#### Slide 13 - 模拟回测

- **Audience move**: 想用模型赚钱 → 看到扣手续费后最好的结果只是“少亏”
- **Relationships**: contrast — 买入持有 vs 模型信号 vs 随机；order — 费率 0% → 1% → 2.5% → 13%
- **Composition**: 上方全宽净值曲线面板，下方一张费率 × 策略小表，13% 一行用红色
- **Title**: 回测：最好的策略是少亏
- **Core message**: 只能做多的单边下跌里不可能盈利；Steam 13% 手续费下任何换仓都不可行
- **Content**: 规则：h=7 预测 >0 则次日持有，否则空仓 · 0% 费率：买入持有 −33.8% / Ridge −1.6% / LightGBM −17.6% / 随机 −14.7% · 13% 费率：−42.4% / −67.7% / −89.8% / −100% · KNN 一直预测跌、从不持有，收益 0%
- **Images**: fig_backtest_nav.png
- **Visualization**: backtest-fees 费率 × 策略小表（页面内绘制）
- **Native-ready**: backtest-fees=yes

#### Slide 14 - 验收对照

- **Audience move**: 需要对照计划书的承诺 → 看到 3 项达标、2 项未达标、1 项因题目调整不适用的诚实账单
- **Relationships**: membership — 6 项验收目标；contrast — 目标 vs 结果
- **Composition**: 全宽表格，状态列用图标与颜色区分
- **Title**: 对账：说到的做到了几项
- **Core message**: 回归、SHAP、演示系统达标；分类和区间覆盖率未达标
- **Content**: 数据：1095 天（3 年），单品数量因题目改为大盘不适用 · 7 天 MAPE 降 ≥15% 且 DM 显著：KNN 30.5%，p=0.001，达标（主要来自单边下跌） · 分类准确率 ≥60%、Macro-F1 ≥0.55：66.4% / 0.292，未达标 · 80% 区间覆盖 75%~85%：校准后 88.4/92.6/91.3%，未达标 · SHAP ≥3 条规律：4 条，达标 · 可交互演示系统：Streamlit，达标
- **Visualization**: acceptance 表格，列：目标 / 结果 / 状态
- **Native-ready**: acceptance=no（状态列带图标徽章，属于图形单元格）

### Part 4: 赛后复盘——写给想“理财”的你

#### Slide 15 - 我的饰品账单

- **Audience move**: 以为“卖早了就是赚了、我是股神” → 明白躲过下跌是运气，接盘的人才是被收割的韭菜
- **Relationships**: contrast — 2022 年卖出价 vs 现价（三件饰品各一对）
- **Composition**: 三对手机截图横向排开（卖出 / 现价上下或左右成对），每对下方一个红色跌幅数字；底部一句反转旁白
- **Title**: 我卖早了，所以我是股神？
- **Core message**: 即便你真的赚到钱了，也不要相信自己是股神，你也可能是下一个接盘的韭菜
- **Content**: 蝴蝶刀 | 深红之网（久经）：2022-08-25 卖出 ¥4990 → 现价 ¥3150，−37% · M9 刺刀 | 黑色层压板（久经）：2022-11-26 卖出 ¥3920 → 现价 ¥2337.5，−40% · 专业手套 | 深红之网（久经）：2022-04-14 卖出 ¥2600 → 现价 ¥617.5，−76% · 三件合计 ¥11510 → ¥6105，−47%
- **Images**: butterfly_2022_sold.jpeg + butterfly_now.jpeg；m9_2022_sold.jpeg + m9_now.jpeg；gloves_2022_sold.jpeg + gloves_now.jpeg，三对同尺寸成对展示
- **Source note**: 价格读自用户提供的 BUFF 截图（订单“商品合计”与在售页久经最低价），跌幅按截图价格计算

#### Slide 16 - 欢乐豆式下跌

- **Audience move**: 觉得饰品至少保值 → 被“钱和欢乐豆一样跌”和久留美的反问逗笑，同时接住“不要相信暴富”
- **Relationships**: contrast — 暴富幻想 vs 老实赚钱
- **Composition**: 左侧手机框里的 30 天走势截图配红色 −25%，右侧久留美梗图与一句反转，底部引用“事到如今最对不起的就是父母”
- **Title**: 钱，和欢乐豆一样跌
- **Core message**: 不要相信暴富；老实赚钱很枯燥，但不会一个月跌掉四分之一
- **Content**: 无涂装蝴蝶刀近 30 天：约 ¥7200 → 约 ¥5400，约 −25% · 久留美：“老实赚钱，很枯燥吧” → 我们的回答：枯燥，但踏实 · 大学生名言：“事到如今，最对不起的就是父母”
- **Images**: meme_huanledou_drop.png；meme_kurumi.png
- **Source note**: 30 天价格读自 meme_huanledou_drop.png 走势图坐标，为近似值

#### Slide 17 - 结论

- **Audience move**: 记住零散的数字 → 带走三句话：模型有小优势、V 社说了算、不赌为赢
- **Relationships**: order — 模型结论 → 市场结论 → 行动建议
- **Closing impact**: 绑定结论“不赌为赢”；三条结论自上而下，最后一句放大，封面的指数折线以缩小形态在背景回归
- **Composition**: 左侧三条编号结论，右侧巨大“不赌为赢”
- **Title**: 赛后总结：不赌为赢
- **Core message**: 决定饰品价格的不是市场因素，而是开发者，极易被操盘——和赌博一样，不赌为赢
- **Content**: 01 模型有一定精度：1 天预测比持平低 15.7% 且显著，但近两年整体只领先 4%~10%，大盘多数时候接近随机游走 · 02 外部资产几乎无关（比特币、黄金），V 社更新才是决定性因素——2025 年 5 合 1 之后一路下跌 · 03 不要相信暴富，不赌为赢 · 致谢一行：谢谢聆听，欢迎提问
- **Motion suggestion**: 封面背景折线在此页以缩小形态回归，首尾呼应

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 每页 80~180 字的口语化讲稿，讲清本页一句话结论、关键数字的含义和到下一页的过渡；只使用 report.md、personal_ideas.md 与截图中的事实；在梗图页给出可直接说出口的包袱
- **Total duration**: 12–15 分钟
- **Notes style**: conversational，带轻松吐槽，实验页保持严谨
- **Presentation purpose**: 先汇报大作业完整流程与真实结果，再借结果讲清“V 社说了算、不赌为赢”
