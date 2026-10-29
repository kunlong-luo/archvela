# Archvela Skill 参考资料（V3）

完整保留 2026-10-27 的六大领域技术选型文档与 62 场景蓝图。文档为历史决策基线，不保证实施时的包版本仍然最新。

## 阅读顺序

1. 先使用 `scripts/scenes.py` 查找编号，或阅读 [07 全场景索引](./07_V3_全场景蓝图与选型索引.md)。
2. 阅读 [00 通用规范](./00_通用_单人产品工厂与前端架构规范.md)。
3. 只读取匹配的 01–06 领域卷，避免一次性加载全部资料。
4. 使用 [T01 架构决策](./templates/T01_新项目立项与架构决策_ADR.md)、[T02 分包预算](./templates/T02_分包策略与性能预算.md)、[T03 任务卡](./templates/T03_OpenCode_立项与交付任务卡.md) 准备交付。

## 场景化生成资料

`architecture_profiles.json` 提供六种领域的 Package/Feature/Chunk/Asset 策略、回退路径、迭代 PR 和验收重点。生成器会将对应场景与领域规则合并到三份草案开头；原始 V3 文档与 T01/T02/T03 模板保持独立可回溯。

## 可选结构化规划合同

如需要在 OpenCode/Codex/Claude Code 等不同代理之间传递技术决策，使用 `scripts/new_project_docs.py --plan-json` 生成 `archvela-plan.json`，再运行 `scripts/plan_contract.py <path> --level draft`。reviewed/delivered 只是形式与证据引用校验，不代替真实测试。

## 范围

- 01 网站与商业展示：13 场景
- 02 业务应用与生产工具：11 场景
- 03 空间与数字孪生：12 场景
- 04 教育与专业可视化：8 场景
- 05 互动娱乐与沉浸体验：9 场景
- 06 地理数据与公共展示：9 场景

Pagevela 和 Voxnelo 既有技术栈只作参考，不自动迁移既有工程。具体版本/授权以开发时核查为准。
