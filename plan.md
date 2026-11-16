# `pm-chinese-naming` Open-Source Agent Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个面向全球主流 AI Agent（Claude Code, Cursor, Codex, Antigravity, OpenClaw）的独立开源 Agent Skill `pm-chinese-naming`（华人文化严谨起名与声律考据引擎），融合 Python 纯标准库确定性排盘算法与高维国学典籍意象生成，交付包含核心算法、数据基准、Skill 规范、交互原型与长辈说服文书的完整开源代码仓库。

**Architecture:** 采用两段式解耦设计。前置层使用无第三方依赖的 Python 脚本 `scripts/engine.py` 实现真太阳时（EOT拟合）、干支四柱八字（早夜子时划分）、调候与五行喜用神推断、平水韵平仄律动检测与千禧重名黑名单过滤；后置层依托 Agent LLM 完成典籍篇目考据（《诗经》《楚辞》篇目对齐防伪）、甲骨文字形源流解析与《长辈说服沟通卡》交付；附带单文件交互原型 `prototypes/naming-card.html`（内置 PM 调试状态切换栏）。

**Tech Stack:** Python 3 (标准库: `math`, `datetime`, `json`, `argparse`, `unittest`), Markdown (Agent Skills / agentskills.io 规范), HTML5 + Tailwind CSS (CDN) + Vanilla JS.

**Spec:** [workspace/solo/pm-chinese-naming/design.md](file:///Users/fx/wk/github/ai-native-pm/workspace/solo/pm-chinese-naming/design.md)

## Global Constraints

- 存储与执行隔离：全套开源资产落盘于 `workspace/solo/pm-chinese-naming/`，自成独立 Git 仓库架构，严禁污染主仓库根目录。
- 零外部依赖：`scripts/engine.py` 必须能在纯 Python 3.9+ 标准库环境下直接运行，严禁依赖 pip 安装的第三方包。
- 坐标覆盖率：内置 340+ 中国地级市经纬度基准，真太阳时时差精度控制在 $\pm 2$ 分钟以内。
- 命理流派标准：严守“夜子时（23:00~24:00）属当日日柱、早子时（00:00~01:00）属次日日柱”；喜用神严守“寒热调候急救为先，病药通关次之，旺衰扶抑为辅”。
- 规范兼容：`SKILL.md` 严格遵循 agentskills.io 规范，YAML frontmatter `description` 不超过 1024 字符且以第三人称 "Use this skill when..." 开头。

## Review Focus

- 23:30 夜子时与 00:30 早子时跨天交界，日柱与时柱天干地支是否准确切分而不错位。
- 冬至/立春跨年换岁时刻，年柱与生肖判定是否严格以“立春”节气交节为界而非正月初一。
- 盛夏或深冬出生的极端八字，调候用神是否优先于身弱身强（如冬金极寒优先调候取火解冻）。
- 现代千禧重名高频词（如“梓涵”、“子轩”、“雨泽”）与双声叠韵拗口拼音是否被 100% 规则拦截。
- 单文件 HTML 原型双击在脱机浏览器中是否能够直接完整渲染并支持 PM 状态切换（正常/空态/生成中/拦截报错）。

---

### Task 1: 静态参考数据集 (`data/cities.json` & `data/blacklist.json`)

**Files:**
- Create: `workspace/solo/pm-chinese-naming/data/cities.json`
- Create: `workspace/solo/pm-chinese-naming/data/blacklist.json`
- Test: `workspace/solo/pm-chinese-naming/tests/test_data.py`

**Interfaces:**
- Produces:
  - `cities.json`: Dictionary mapping city name to `{"lng": float, "lat": float, "province": str}` covering 340+ Chinese prefecture cities.
  - `blacklist.json`: `{"cliche_names": list[str], "cliche_characters": list[str], "homophone_traps": list[dict]}`.

- [ ] **Step 1: Write test for datasets in `tests/test_data.py`**
  Verify `cities.json` contains major cities (北京, 上海, 广州, 杭州, 成都, 哈尔滨, 乌鲁木齐) with valid longitudes ($73^\circ \sim 135^\circ$), and `blacklist.json` contains known cliché names ("梓涵", "子轩", "浩宇", "雨泽", "欣怡").

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_data.py`
  Expected: FAIL with FileNotFoundError.

- [ ] **Step 3: Implement `data/cities.json` and `data/blacklist.json`**
  Construct `cities.json` with 340+ Chinese prefecture-level cities and their standard coordinates. Construct `blacklist.json` with over 100 high-frequency cliché baby name characters/combinations and typical homophone trap patterns.

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_data.py`
  Expected: OK.

---

### Task 2: 确定性天文排盘与声律引擎 (`scripts/engine.py`)

**Files:**
- Create: `workspace/solo/pm-chinese-naming/scripts/engine.py`
- Test: `workspace/solo/pm-chinese-naming/tests/test_engine.py`

**Interfaces:**
- Consumes: `data/cities.json`, `data/blacklist.json`
- Produces:
  - `calculate_true_solar_time(dt_str: str, city_name: str) -> dict`: Returns true solar time and EOT offset.
  - `get_bazi_pillars(solar_dt: datetime) -> dict`: Returns Year, Month, Day, Hour pillars (GanZhi) with proper solar terms and early/late Zi-shi split.
  - `evaluate_wuxing_and_yongshen(pillars: dict) -> dict`: Returns WuXing element counts, day master strength, and prioritized XiYongShen (TiaoHou > TongGuan > WangShuai).
  - `audit_phonetics_and_safety(surname: str, given_name: str) -> dict`: Returns PingZe tonal pattern, initial/final rhyme harmony check, and blacklist/homophone safety flags.
  - CLI Interface: `python3 engine.py --date "2026-08-15 14:30" --city "杭州" --surname "陈" --name "言溪"` returning unified JSON.

- [ ] **Step 1: Write unit tests in `tests/test_engine.py`**
  Cover:
  1. True solar time offset for Beijing ($116.4^\circ$) vs Urumqi ($87.6^\circ$).
  2. Late Zi-shi (23:30) keeps current day GanZhi, early Zi-shi (00:30) rolls to next day.
  3. Winter birth (Zi month / Chou month) triggers Fire (丙/丁火) as prioritized TiaoHou XiYongShen.
  4. Cliché name "陈梓涵" triggers blacklist flag; "杜子腾" triggers homophone warning; harmonious name "陈言溪" passes with Ping-Ze-Ping pattern.

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_engine.py`
  Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 3: Implement `scripts/engine.py` using pure Python standard library**
  Implement:
  1. Equation of Time (EOT) formula approximation + longitude time delta: $\Delta t = 4 \times (\text{lng} - 120) + \text{EOT}$.
  2. GanZhi calendar conversion algorithm with astronomical 24 solar terms.
  3. Zi-shi early/late discriminator (23:00~24:00 vs 00:00~01:00).
  4. WuXing distribution mapping and TiaoHou heuristic rules.
  5. Phonetic tonal dictionary check (中华新韵/平水韵平仄分类) and blacklist matcher.
  6. CLI argument parser and formatted JSON output.

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_engine.py`
  Expected: OK.

---

### Task 3: 核心开源 Agent Skill 规范文件 (`SKILL.md`)

**Files:**
- Create: `workspace/solo/pm-chinese-naming/SKILL.md`
- Test: `workspace/solo/pm-chinese-naming/tests/test_skill_spec.py`

**Interfaces:**
- Conforms to: agentskills.io format with YAML frontmatter (`name: pm-chinese-naming`, `description: Use this skill when...`).
- Defines:
  - Command routing: `/name baby`, `/name audit`, `/name elder`, `/name scaffold`.
  - Two-stage execution SOP (deterministic script run + LLM classical literature citation & elder card synthesis).
  - Strict anti-hallucination guardrails (prohibiting fake poetry, requiring chapter citations).
  - Elder persuasion card template and 5-dimension radar scoring criteria.

- [ ] **Step 1: Write validation test in `tests/test_skill_spec.py`**
  Verify `SKILL.md` has valid YAML frontmatter, `name` matches regex `^[a-z0-9-]+$`, `description` starts with "Use this skill when...", character length $\le 1024$, contains all 4 slash commands, and includes all anti-hallucination rules.

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_skill_spec.py`
  Expected: FAIL with FileNotFoundError.

- [ ] **Step 3: Author `SKILL.md`**
  Write complete, production-grade SKILL.md per spec:
  - Role definition: 华人文化严谨起名与声律考据专家 (Chinese Naming & Philology Master).
  - Mode 1: Direct naming workflow with structured JSON contract and Markdown deliverables.
  - Mode 2: Scaffold generator workflow.
  - Elder card synthesis heuristics (turning modern aesthetic names into culturally unassailable reasons for grandparents).

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_skill_spec.py`
  Expected: OK.

---

### Task 4: 单文件交互原型与长辈沟通卡 (`prototypes/naming-card.html`)

**Files:**
- Create: `workspace/solo/pm-chinese-naming/prototypes/naming-card.html`
- Test: `workspace/solo/pm-chinese-naming/tests/test_prototype.py`

**Interfaces:**
- Self-contained HTML with inline Tailwind CDN script, zero build tools required.
- Includes `🛠️ PM 评审状态切换器` floating bar with 5 states:
  - `State 1: 正常展示 (Active Proposal)`: Candidate names, radar chart, poetry citation, etymology.
  - `State 2: 空状态 (Empty)`: Prompting user for surname and birth time.
  - `State 3: 算法计算中 (Loading / Calculating)`: Solar time calibration and BaZi derivation in progress.
  - `State 4: 安全拦截异常 (Blocked / Cliché)`: Warning triggered by "梓涵" or homophone trap with suggestions.
  - `State 5: 长辈说服卡展开 (Elder Persuasion View)`: Dedicated classical blessing letter designed for grandparents with one-click copy button.

- [ ] **Step 1: Write automated DOM structure test in `tests/test_prototype.py`**
  Verify `naming-card.html` contains `PM 评审状态切换器`, all 5 states defined, zero local CSS/JS asset dependencies, and proper UTF-8 charset.

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_prototype.py`
  Expected: FAIL with FileNotFoundError.

- [ ] **Step 3: Implement `prototypes/naming-card.html`**
  Author the self-contained prototype with refined Chinese traditional typography (SongTi/KaiTi styling), responsive layout, dynamic radar chart via SVG, and interactive debug state switching.

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_prototype.py`
  Expected: OK.

---

### Task 5: 开源交付物打包与全链路端到端验收 (`README.md`, `LICENSE`, `cases.md`)

**Files:**
- Create: `workspace/solo/pm-chinese-naming/README.md`
- Create: `workspace/solo/pm-chinese-naming/LICENSE`
- Create: `workspace/solo/pm-chinese-naming/tests/cases.md`
- Test: `workspace/solo/pm-chinese-naming/tests/test_e2e_pipeline.py`

**Interfaces:**
- Produces:
  - `README.md`: Bilingual (Chinese/English) open-source landing documentation with badge, architecture diagram, installation guide for Claude Code/Cursor/Antigravity, and sample outputs.
  - `LICENSE`: Standard MIT license.
  - `cases.md`: Golden test cases (e.g. 2026丙午马年立春前后、夜子时、南北方经度差经典案例).
  - `test_e2e_pipeline.py`: Comprehensive test validating dataset -> engine -> CLI output -> prototype consistency.

- [ ] **Step 1: Write end-to-end integration test in `tests/test_e2e_pipeline.py`**
  Verify that invoking `engine.py` via subprocess with test arguments yields valid JSON, matches the schema expected by `SKILL.md`, and validates against `cases.md`.

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest workspace/solo/pm-chinese-naming/tests/test_e2e_pipeline.py`
  Expected: FAIL with FileNotFoundError or missing files.

- [ ] **Step 3: Create `README.md`, `LICENSE`, `cases.md` and finish integration**
  Write comprehensive README and MIT license, document test fixtures, and ensure all parts form a self-contained open-source repo.

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 -m unittest discover -s workspace/solo/pm-chinese-naming/tests -p "test_*.py"`
  Expected: ALL TESTS PASS.
