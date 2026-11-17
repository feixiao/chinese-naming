# `chinese-naming` · 华人严谨起名与声律考据引擎

[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills Specification](https://img.shields.io/badge/Agent_Skills-Ready-emerald.svg)](https://agentskills.io)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard_Library_Only-blue.svg)](https://python.org)

> **面向 AI Coding Agent（Claude Code, Cursor, Codex, Antigravity, OpenClaw 等）的原生开源技能（Agent Skill）**。  
> 将日级天文近似、声律词库检查与古典意象生成分开，显式标注输入精度、词库范围及引文核验状态；用于传统文化语境下的命名参考，不提供命运、健康、财富或教育结果的预测。

---

## 🎯 为什么需要 `chinese-naming`？

华人起名常需兼顾审美、家族沟通与传统文化意象。本项目提供可审计的约束，而不把近似计算或模型生成包装成确定事实：

* 出生时分缺失时，不推定时柱或大运；
* 日级节气表在交节日前后一日拒绝判定月柱；
* 拼音表缺字或多音字未确认时，不输出声律结论；
* 谐音结果只报告内置词库命中，不宣称方言已覆盖；
* 典籍必须经独立核验后才可作为直接引文。

---

## 🏗️ 两段式解耦系统架构

```
[用户输入] (姓氏 + 公历时间 + 城市 + 性别 + 风格)
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段一：可审计约束 (scripts/engine.py，纯标准库)              │
│  1. 真太阳时近似校准（经度差 + EOT 近似）                     │
│  2. 分钟级输入校验；交节日前后一日拒绝月柱判定                │
│  3. 传统季候命名意象提示（不作人生预测）                      │
│  4. 内置拼音表的平仄/双声/叠韵检查；缺字即未验证              │
│  5. 高频名与谐音词库命中状态（不覆盖方言）                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ 输出证据状态与候选约束
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段二：文化意象交付                                           │
│  1. 已核验的典籍可作为直接引文；否则仅标为意象参考             │
│  2. 常用字义与书写观感                                         │
│  3. 候选名字与证据状态报告                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ 极速工作流指令 (Slash Commands)

安装该 Skill 后，可在任何支持 Agent Skills 的终端中直接使用如下指令：

| 快捷指令 | 目标场景 | 核心输入 | 标准结构化交付物 |
| :--- | :--- | :--- | :--- |
| **`/name baby`** | 新生儿起名 | 姓氏、出生时分地点、性别、风格 | 候选名字矩阵 + 证据状态报告 |
| **`/name audit`** | 已有备选名字体检 | 姓氏、候选名字、出生时分地点 | 读音、词库与季候意象报告 |
| **`/name scaffold`** | 生成小程序/Web 起名独立项目脚手架 | 目标平台（小程序/H5） | 输入校验与证据状态优先的原型 |

---

## 🚀 快速上手与使用

### 1. 运行引擎

引擎仅使用 Python 3.8+ 标准库。`--date` 必须精确到分钟；交节日前后一日会返回错误，要求以精确节气历确认月柱。

```bash
python3 scripts/engine.py --date "2026-08-15 14:30" --city "杭州" --surname "陈" --name "言溪" --gender "女"
python3 scripts/engine.py --date "2026-08-15 14:30" --city "杭州" --surname "陈" --name "言溪" --gender "女" --json
```

**输出含以下证据状态：**

- 出生时分和节气表精度；
- 传统季候意象（非人生预测）；
- 拼音数据是否完整；
- 高频名、谐音是否命中内置词库；
- 典籍引文是否经过独立核验。

### 2. 在 AI Agent 中载入技能 (Claude Code / Cursor / Codex / Antigravity)
将本目录软链接或复制到全局 Agent Skills 目录：
```bash
# Claude Code
cp -r . ~/.claude/skills/chinese-naming

# Cursor / Codex / Antigravity / OpenClaw
cp -r . ~/.agents/skills/chinese-naming
```
在会话中直接输入：
> `/name baby 姓陈，女宝，公历2026年8月15日14点30分出生在杭州，想要文雅清隽、暗合五行调候的名字`

---

## 🎨 单文件交互原型 (`prototypes/naming-card.html`)

仓库内置一份无外部编译依赖的单文件交互原型，包含 **`🛠️ PM 评审状态切换器`**：

* 状态 1：正常提案展示；
* 状态 2：空状态；
* 状态 3：计算中；
* 状态 4：高频名与词库风险提示。

直接在浏览器中双击 `prototypes/naming-card.html` 即可预览交互。

---

## 🧪 单元测试与端到端验证

全套测试用例开箱即测：
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

---

## 📄 开源许可证

本项目基于 [MIT 许可证](LICENSE) 开源，欢迎自由二次开发或封装为商业微 SaaS / 小程序。
