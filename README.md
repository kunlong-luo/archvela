# Archvela · 智能产品架构工坊

> **From Ideas to Architecture.** 一个面向独立开发者的场景驱动前端架构 Skill：将产品创意变成有依据的技术决策、可维护的分包方案和可验收的开发任务。

[English](./README.en.md) · [Skill](./.agents/skills/archvela-architect/SKILL.md) · [62 个场景](./.agents/skills/archvela-architect/references/07_V3_全场景蓝图与选型索引.md) · [贡献指南](./CONTRIBUTING.md)

## 为什么是 Archvela？

不仅推荐热门框架，而是以 **62 种实际产品场景 × 六大领域 × 四层分包策略** 帮一个人持续开发多个各具特色的产品，同时避免巨型 Monorepo、无差别添加依赖与未经验证的“架构升级”。

| 六大领域 | 场景数 | 代表产品 |
|---|---:|---|
| 网站与商业展示 | 13 | 简单/电影化企业官网、SaaS 营销、跨境独立站、3D 配置器 |
| 业务应用与生产工具 | 11 | 高级后台、Agent 工作流、BI、图片与视频编辑 |
| 空间与数字孪生 | 12 | 农村 GIS、住宅设施、工厂、BIM、仓储、光伏 |
| 教育与专业可视化 | 8 | 英语口语、物理实验、医学影像与工程培训 |
| 互动娱乐与沉浸体验 | 9 | 2D/3D 网页游戏、虚拟展馆、XR 与高保真展示 |
| 地理数据与公共展示 | 9 | 专题地图、交通轨迹、空间数据与交互式报告 |

**本仓库第一版提供 Skill + 参考资料 + 安全工具脚本，不是自动生成完整商业应用的网站。**

## OpenCode 安装

克隆仓库：

```bash
git clone https://github.com/kunlong-luo/archvela.git
cd archvela
```

在 Archvela 仓库中使用时，OpenCode 可发现 `.agents/skills/archvela-architect/SKILL.md`。若要在**其他项目**中全局使用：

```bash
mkdir -p ~/.config/opencode/skills
ln -s "$(pwd)/.agents/skills/archvela-architect" ~/.config/opencode/skills/archvela-architect
```

如目标目录已存在，请先检查，不要直接覆盖。也可以把该技能目录复制到对应 OpenCode 全局 Skill 目录。更多兼容位置参考 [OpenCode Skills 官方文档](https://docs.opencode.ai/docs/skills/)。

## 使用示例

在 OpenCode 中提问：“使用 `archvela-architect`，帮我设计一个高端动态企业官网；只审计和输出架构 ADR、分包方案、性能预算、MVP 任务卡，暂不修改代码。”

不依赖代理，也能查询资料：

```bash
SKILL_DIR=".agents/skills/archvela-architect"
python3 "$SKILL_DIR/scripts/scenes.py" --list-domains
python3 "$SKILL_DIR/scripts/scenes.py" --query "住宅"
python3 "$SKILL_DIR/scripts/scenes.py" --query "home digital twin" --json
python3 "$SKILL_DIR/scripts/scenes.py" --domain 03 --limit 5
python3 "$SKILL_DIR/scripts/scenes.py" --id V3-26 --json
python3 "$SKILL_DIR/scripts/new_project_docs.py" --scene V3-26 --project home-twin --output ./demo
# 仅检查过目标目录且同意创建文件后，再添加 --write
```

生成器默认只预演；三份文档按所选场景和领域预填充真实功能、分包初稿、回退及 PR 切片，而不是简单复制空白模板。已有同名文件时拒绝覆盖，写入发生异常会回滚本轮已创建的文件；`--json` 可以输出机器可读的路径清单。

## 跨 AI 工具的架构交接文件

`new_project_docs.py` 可选 `--plan-json`，除了已有的三份 Markdown 草案，还会产生 `archvela-plan.json`。其中包含唯一场景编号、候选与最终技术选型、Package/Feature/Chunk/Asset Pack 四层决策、仓库审计、兼容设备、回退、测试记录和证据引用。默认仍只预演，不会写文件。

```bash
SKILL_DIR=".agents/skills/archvela-architect"
python3 "$SKILL_DIR/scripts/new_project_docs.py" --scene V3-26 --project demo --output ./example --plan-json
# 确认目标目录后才执行 --write
python3 "$SKILL_DIR/scripts/new_project_docs.py" --scene V3-26 --project demo --output ./example --plan-json --write
python3 "$SKILL_DIR/scripts/plan_contract.py" ./example/docs/architecture/archvela-plan.json --level draft
```

`reviewed` 要求架构决策、四层分包、审计证据、设备与测试计划；`delivered` 要求测试/实测证据字段。**这些验证是可追踪的格式门禁，不会自动验证 AI 的结论或真实性。**

## 四层分包原则

| 层级 | 关注点 | 例子 |
|---|---|---|
| Package | 是否跨项目真实复用 | 先保持每个产品独立；有需求才抽公共包 |
| Feature | 按用户任务边界组织代码 | editor、scene、map、campaign、game-combat |
| Chunk | 代码按路由和重功能加载 | 地图、3D、PDF、视频编辑器按需加载 |
| Asset Pack | 大媒体和模型资源策略 | 海报、KTX2、GLB/LOD、视频、地图瓦片 |

## 实例及兼容性

- **Pagevela** 的现有 React + Vite PWA 架构应保留；改造从真实性能证据出发。
- **Voxnelo** 目前是 React + Rsbuild/Electron，本地优先语音练习；官网与桌面端是不同架构决策。
- 数字孪生将地理尺度的 CesiumJS 和住宅设备精模的 R3F 分开组织；复杂 Web 游戏选专门的引擎。

所有示例是候选技术方案，不意味着已在项目中安装、部署或验证。实施时重新检查 API、版本、浏览器支持和素材许可证。

## 跨 AI 编程工具兼容性验证

Archvela 不限于 OpenCode：项目计划使用官方 Skills CLI，对 OpenCode、Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot、Windsurf、Cline、Roo Code、Kiro CLI 等 **20 种代理安装目标**逐一执行项目级路径和文件内容验证，并对六个核心代理做全局安装测试；同时在每个安装副本内运行场景查询和架构生成器预演，验证复制后的 Skill 可以独立工作。

真实模型运行另分 L2/L3；**安装通过不等于模型已读取或执行成功**。查看 [兼容矩阵和测试分级](./docs/COMPATIBILITY.md) 与 [统一真实客户端测试题](./docs/L3-TEST-PROMPTS.md)。

## 研发与质量

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .agents/skills/archvela-architect/scripts
```

GitHub Actions 对目录元数据、62 场景、脚本安全行为和生成器的“不覆盖”规则进行自动检查。见 [AGENTS.md](./AGENTS.md) 和 [SECURITY.md](./SECURITY.md)。

## 开源说明

本 PR 提议采用 MIT 许可证；**仓库所有者合并 PR 前应确认此授权决定**。第三方商标、源代码、数据、图像、模型和音乐不因本项目许可证而自动获权。
