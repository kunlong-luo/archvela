---
name: archvela-architect
description: 场景驱动的前端与渲染产品架构 Skill，帮助独立开发者/单人团队规划高质量 SaaS、企业官网、跨境电商、AI 工作台、农村与住宅数字孪生、GIS、2D/3D 网页游戏等 62 种场景。根据真实仓库选择 React/Next.js/Astro/Vite/Rsbuild、Motion/GSAP、Three.js/R3F/CesiumJS/Babylon.js 等，生成 ADR、功能模块、四层分包、性能预算和可验收的 AI 编程开发任务。适用于新项目及既有前端项目评审；先审计再修改，绝不强迫重构。
license: MIT
compatibility: Agent Skills-capable coding agents; optional Python 3.10+ CLI helpers.
metadata:
  author: kunlong-luo
  version: "0.1.0"
---

# Archvela Architect · 智能产品架构工坊

目标：将一个具体用户需求转换为有辨识度、可测试、可分阶段交付的**前端与浏览器渲染**产品，不机械叠加技术。

## 适用与边界

- 用于新建网站、SaaS、后台管理、在线编辑器、企业官网、跨境展示站、GIS/住宅/工业数字孪生、Web 游戏、教育可视化与架构审查。
- 仅设计前端、UI/UX、渲染、构建、浏览器资源及前端测试。后端、数据库、支付和云架构只标明接口边界，不擅自设计实现。
- 除非用户明确授权，不自动安装依赖、运行不受信任脚本、改变生产环境、执行部署或发布。
- 禁止只为追逐流行而重写存量项目；默认不推荐 Vue 3、Ant Design 6（项目既有依赖则先评估风险，不擅自删除）。

## 核心步骤

1. **先只读审计**：若已有仓库，读 `AGENTS.md`、README、package.json、锁文件、路由、构建配置、现有测试与业务约束。无法访问时如实标注。若新项目，确定核心用户任务、目标浏览器/设备、SEO、离线/性能/尺寸/交付边界。
2. **匹配场景**：先按编号或自然语言查询。主场景仅选一个，辅助最多两个。只加载需要的参考资料，而不是每次读完全部 62 个场景。
3. **架构取舍 ADR**：明确采用与排除的选项。静态内容/简单官网常用 Astro；复合 SaaS 可用 Next.js；已有 Pagevela React+Vite、Voxnelo React+Rsbuild/Electron 不强制迁移。Next.js 16 内置 Turbopack，无须叠加 Vite。GIS 用 CesiumJS；住宅/设备精模用 Three.js+R3F；网页游戏按需 Babylon.js/PlayCanvas。
4. **四层分包**：分别给出 (a) 源码 Package（单产品默认独立仓库），(b) Feature（用户任务边界），(c) JS Chunk（路由和重编辑器/地图分割），(d) 资源 Pack（图像、视频、GLB、KTX2、瓦片、游戏场景按需）。两个以上项目有真实复用收益时才抽共享包。
5. **产品特色**：定义独立品牌、设计 tokens、页面动线、动画节奏和一个可证明价值的真实演示，不照搬 UI 或版权角色。Motion 用于 UI，GSAP 用于复杂滚动，3D/游戏动画由渲染引擎管理；一个项目以一套图标和组件系统为主。
6. **纵向 MVP**：从用户可完成的一件事开始。指定最小模块、目录树、首屏及失败回退、测试用例、性能预算。3D/GIS 先校验坐标系与几何尺寸，游戏要独立状态机和帧循环；WebGPU 必须有经验证的兼容策略。
7. **交付验证**：typecheck、lint、单测、build、关键 E2E、可访问性及性能。区分建议/已实现/在真实设备通过。未经授权不执行危险动作。

## 检索 62 场景

在本 Skill 根目录运行：

```bash
python3 scripts/scenes.py --list-domains
python3 scripts/scenes.py --query "农村数字孪生"
python3 scripts/scenes.py --query "home digital twin" --json
python3 scripts/scenes.py --domain 03 --limit 5
python3 scripts/scenes.py --id V3-26 --json
```

没有 Python 时阅读 `references/07_V3_全场景蓝图与选型索引.md`。定位编号后阅读 `references/00_通用_单人产品工厂与前端架构规范.md` 和对应的 `references/01_网站与商业展示.md`～`references/06_地理数据与公共展示.md` 中**一卷**。

## 生成架构文档

```bash
# 预演：无任何写入
python3 scripts/new_project_docs.py --scene V3-26 --project home-digital-twin --output ./example-project

# 用户确认写入目的目录后，再执行
python3 scripts/new_project_docs.py --scene V3-26 --project home-digital-twin --output ./example-project --write
```

写入仅生成 `docs/architecture/` 下三份**按领域预填充**的 ADR、性能预算和通用 AI Agent 开发任务草案；默认只预演，已有同名文件时拒绝覆盖，失败时回滚本轮生成的文件。辅助脚本可用 `--json` 返回路径清单。文档均需结合仓库审计和目标设备实测审核，不代表自动实施。

领域预填充规则：`references/architecture_profiles.json`（六大领域）；参考模板：`references/templates/T01_新项目立项与架构决策_ADR.md`、`T02_分包策略与性能预算.md`、`T03_OpenCode_立项与交付任务卡.md`。

## 固定输出

- **场景与证据**：编号、用户任务、产品差异化、已知/未知和约束。
- **架构决策**：前端框架、UI、动画、渲染、打包与拒绝选项的理由。
- **目录与分包**：源码包、Feature、JS Chunk、媒体/模型 Asset Pack、回退策略。
- **MVP 与预算**：页面/交互、交付阶段、性能指标与质量门禁。
- **执行任务**：按 PR 拆分，附测试结果与未验证事项。

本 Skill 不是自动生成完整应用的保证，也不能代替专业施工图精度、临床规范、版权审核或真实商业验证。
