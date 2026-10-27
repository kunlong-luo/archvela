# Archvela · 主流 AI 编程工具兼容性与验收矩阵

> 2026-10-27 核对官方路径。文档中的「支持」指 Agent Skills 发现格式符合目标客户端/安装器规则；「安装通过」须以 [compatibility.yml](../.github/workflows/compatibility.yml) 的真实运行成功结果为准；**不等于该客户端真实模型推理或 Skill 调用成功**。

## 测试分级

- **L0 规范静态检查**：`SKILL.md` YAML frontmatter、ID、description、参考目录、62 场景完整性、Scripts 基础单元测试。
- **L1 安装器执行**：用 Vercel [Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) 将本地 Archvela Skill 逐一安装到隔离的 20 种 Agent 专用项目目录；验证真实 `SKILL.md`、`references/scenarios.json`、`scripts/scenes.py` 等文件。附加对 6 种核心代理的全局安装目录检查。每个代理和 scope 使用**独立临时目录**，防止串扰。
- **L2 客户端发现**：在实际安装的 OpenCode、Codex、Claude Code、Cursor、Gemini CLI、Copilot 等客户端中检查列表中存在 Archvela，能显式激活，且资源可读取。
- **L3 用户任务端到端**：每种客户端使用相同的三种情境（企业官网、农村/住宅数字孪生、网页游戏）生成 ADR、四层分包策略与 MVP；验证输出事实，不仅检查是否能读文件。

**CI 只能自动证明 L0–L1。L2–L3 需要该客户端真实安装与必要模型授权。** 不允许把 20/20 安装成功描述为 20 个模型实际运行成功。

## 官方支持范围与目标路径

| 工具 | Skills CLI ID | 项目安装目录 | 全局目录 |
|---|---|---|---|
| opencode | `opencode` | `.agents/skills` | `~/.config/opencode/skills` |
| codex | `codex` | `.agents/skills` | `~/.agents/skills` |
| claude-code | `claude-code` | `.claude/skills` | `~/.claude/skills` |
| cursor | `cursor` | `.agents/skills` | `~/.cursor/skills` |
| gemini-cli | `gemini-cli` | `.agents/skills` | `~/.gemini/skills` |
| github-copilot | `github-copilot` | `.agents/skills` | `~/.copilot/skills` |
| windsurf | `windsurf` | `.windsurf/skills` | `~/.codeium/windsurf/skills` |
| cline | `cline` | `.agents/skills` | `~/.agents/skills` |
| roo | `roo` | `.roo/skills` | `~/.roo/skills` |
| kiro-cli | `kiro-cli` | `.kiro/skills` | `~/.kiro/skills` |
| antigravity | `antigravity` | `.agents/skills` | `~/.gemini/antigravity/skills` |
| kilo | `kilo` | `.agents/skills` | `~/.kilo/skills` |
| openhands | `openhands` | `.openhands/skills` | `~/.openhands/skills` |
| qwen-code | `qwen-code` | `.qwen/skills` | `~/.qwen/skills` |
| trae | `trae` | `.trae/skills` | `~/.trae/skills` |
| zed | `zed` | `.agents/skills` | `~/.agents/skills` |
| amp | `amp` | `.agents/skills` | `~/.config/agents/skills` |
| continue | `continue` | `.continue/skills` | `~/.continue/skills` |
| pi | `pi` | `.agents/skills` | `~/.agents/skills` |
| replit | `replit` | `.agents/skills` | `~/.config/agents/skills` |

路径来自 [Vercel Skills 官方 agent registry](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)。不同版本可能变化，以实际 `skills` CLI 输出为准。

**已观测的 Skills CLI 1.7.4 行为：** 对 OpenCode、Cursor、Gemini CLI、GitHub Copilot 执行 `-g --copy` 时，安装器选用的真实位置可能是共享的 `~/.agents/skills/archvela-architect`，而不是表中对应的专用全局目录。这些客户端官方均支持 `~/.agents/skills` 作为全局发现位置。兼容性脚本因此验证「官方专用位置或共享兼容位置」至少有一处成功，并在 JSON 报告中记录实际目录；绝不把安装器的预期目录当作已经写入的目录。

## 手动安装与发现验证

本仓库可直接通过 CLI 从本地文件安装到项目或用户目录：

```bash
# 在仓库根目录：仅列出发现的 Skill
npx skills add . --list

# 全局安装到指定主流代理（此命令写入用户级 Skills 目录）
npx skills add . --skill archvela-architect -g \
  -a opencode -a codex -a claude-code -a cursor \
  -a gemini-cli -a github-copilot -y
```

如果是下载公开仓库版本，合并 PR 之后才可使用 `npx skills add kunlong-luo/archvela`；未合并前公开仓库 `main` 中尚无技能。

**建议本地确认流程：**
1. 在真实代理里检查 Archvela 的技能名称、description 和根目录是否识别。
2. 显式触发 `archvela-architect`，要求“查找 V3-26，不执行任何写入”。
3. 确认能读到住宅三维参考、62 个目录项和正确技术栈。
4. 生成 T01/T02/T03 文档前先预演，核实目标目录并获许可后写入。
5. 校验重复执行不会覆盖文件，输出包含性能预算、真实尺寸/坐标约束及未验证事项。

## 已知差异与边界

- **Cursor**：项目 `.agents/skills` 可发现；用户级 `~/.cursor/skills` 与云端同步有单独规则，不要假设全局目录的 Skill 自动同步到 Cloud Agent。参考 [Cursor 官方文档](https://cursor.com/docs/skills)。
- **Gemini CLI**：支持 `.agents/skills` 作为别名，工作区可信度影响加载；使用 `/skills list` 与 `/skills reload` 确认。参考 [Gemini CLI 官方文档](https://geminicli.com/docs/cli/tutorials/skills-getting-started/)。
- **GitHub Copilot**：包括 Copilot CLI、云端代理和 VS Code 等不同运行面；项目的 `.agents/skills` 路径并不等于已配置好云端权限。参考 [GitHub 官方文档](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)。
- **OpenCode**：可发现本项目级 `.agents/skills`，全局 `~/.config/opencode/skills`；使用内置 Skill 工具进行读取。参考 [官方文档](https://docs.opencode.ai/docs/skills/)。
- **Codex**：项目级 `.agents/skills` 自动发现；使用客户端技能选择器显式验证。参考 [OpenAI 文档](https://learn.chatgpt.com/docs/build-skills)。
- **Claude Code**：项目级 `.claude/skills`，全局 `~/.claude/skills`；通过 Skills CLI 映射安装，不能以只存在原仓库的 `.agents` 路径代替对实际安装的验证。
- **Windsurf / Roo Code / Kiro CLI**：需要其对应 Skill 目录，CLI 的项目安装测试会验证这些目录是否正确映射。
- 这套 Skill 中有 Python 辅助脚本，但客户端可以只读纯 Markdown；**不能假定所有客户端具有 Python 或文件写权限**。
- **权限/费用**：L3 需要实际 Agent 账号、可访问的模型和工具授权；本仓库 CI 不保存个人密钥、不做外部发布和付费模型调用。

## 统一 L3 真实任务检查表

对目标客户端逐项记录：

| 项目 | 预期证据 |
|---|---|
| 安装与发现 | 客户端版本、Skill 名称与安装路径截图或命令输出 |
| 触发方式 | 显式调用成功，不要求一定能自动路由 |
| 场景定位 | `V3-02`、`V3-26`、`V3-45` 编号和内容正确 |
| 架构决策 | 说明选型及不选其他引擎的原因 |
| 四层分包 | Package / Feature / JS Chunk / Asset Pack 俱全 |
| 低风险原则 | 不擅自装依赖、迁移项目、执行部署或覆盖文件 |
| 验收内容 | 可测 MVP、测试清单、性能预算和未验证事项 |

**本清单只有在实际客户端跑通后才能标为 L2/L3 通过。**
