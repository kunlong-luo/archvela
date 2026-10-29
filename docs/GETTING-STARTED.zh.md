# Archvela · Getting started / 快速上手

[中文 README](../README.zh.md) · [English README](../README.md) · [English Quickstart](./GETTING-STARTED.md) · [兼容性说明](./COMPATIBILITY.md)

这个指南展示**两条不同路线**：

- **A · 让 Coding Agent 帮你规划架构**：在自己的项目目录安装 `archvela-architect`，向 Agent 提问。无需克隆 Archvela。
- **B · 不依赖 AI，自己探索场景和生成项目**：克隆 Archvela，使用标准库 Python CLI 或三个可运行的 Starter。

> Archvela 不会代替你购买 API、登录模型或部署应用。安装路径测试（L1）不证明模型实际读取技能（L2/L3）。

## 准备环境

| 场景 | 需要 |
|---|---|
| 安装到 Agent | Node.js 22.20+、npm、可访问 GitHub；对应 Agent 客户端由你自行安装并登录 |
| Python 场景/文档工具 | Python 3.10+，核心脚本不需要额外 pip 包 |
| 运行 React/Next/Vite 示例 | Node.js 24 / npm，以提交的 `package-lock.json` 为准 |

## A · 在自己的项目中安装 Agent Skill

**1. 打开你的目标项目目录。** 在终端执行：

```bash
npx skills add kunlong-luo/archvela --skill archvela-architect
```

按交互提示选择 Codex、Claude Code、OpenCode 或其他适配目标。想跳过交互并同时装到三个主流客户端：

```bash
npx skills add kunlong-luo/archvela --skill archvela-architect \
  --agent codex --agent claude-code --agent opencode --copy --yes
```

默认是**项目级安装**；`--global` 是用户级安装，会触及用户主目录。安装前检查目标项目是否已有同名 Skill，必要时先备份其现有内容，不要无意覆盖定制版本。

**2. 查看实际安装文件。** 从项目根目录检查对应路径：

| Agent | 项目级安装目录 |
|---|---|
| Codex / OpenCode | `.agents/skills/archvela-architect/SKILL.md` |
| Claude Code | `.claude/skills/archvela-architect/SKILL.md` |
| 其他目标 | [兼容矩阵](./COMPATIBILITY.md) |

Skills CLI 可能根据版本使用共享目录或专用目录，以**实际安装输出为准**。可以执行 `npx skills list` 查询安装结果。

**3. 在真正的 Agent 会话中测试。** 开一个全新会话，显式要求使用 `archvela-architect`：

> 使用 Archvela 帮我为已有 React 网站做只读架构审查。先找出主要用户旅程、路由、依赖和构建方式；只输出 V3 场景匹配、ADR、四层分包、性能预算和验收条件。不要修改文件或执行部署。

验证 Agent 能否真的加载 `SKILL.md`、引用所选的场景，而不是仅从安装目录推断模型已经调用。

**4. 升级或卸载。** 请先阅读对应 Skills CLI 的确认提示：

```bash
npx skills list
npx skills check
npx skills update archvela-architect
npx skills remove archvela-architect
```

[Skills CLI 命令文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)

## B · 离线检索场景和生成文档

**1. 获取完整仓库：**

```bash
git clone https://github.com/kunlong-luo/archvela.git
cd archvela
```

**2. 查找场景：**

```bash
python3 .agents/skills/archvela-architect/scripts/scenes.py --list-domains
python3 .agents/skills/archvela-architect/scripts/scenes.py --query "digital twin"
python3 .agents/skills/archvela-architect/scripts/scenes.py --id V3-26 --json
```

**3. 预演架构文档，再决定是否写入：**

```bash
python3 .agents/skills/archvela-architect/scripts/new_project_docs.py \
  --scene V3-26 --project my-home --output ./scratch/my-home --plan-json
```

只有核对预演中的目标路径并确认允许创建后，才执行：

```bash
python3 .agents/skills/archvela-architect/scripts/new_project_docs.py \
  --scene V3-26 --project my-home --output ./scratch/my-home --plan-json --write
python3 .agents/skills/archvela-architect/scripts/plan_contract.py \
  ./scratch/my-home/docs/architecture/archvela-plan.json --level draft
```

输出包括 ADR、性能/分包预算、Agent 任务卡，以及可选 `archvela-plan.json`。`draft` 检查字段结构；`reviewed` 和 `delivered` 也不证明填入的性能或测试数据真实。

**4. 从三个经过构建验证的场景生成代码：**

```bash
python3 scripts/archvela_create.py list
python3 scripts/archvela_create.py create --scene V3-02 --project brand-demo --output ./workspace
python3 scripts/archvela_create.py create --scene V3-02 --project brand-demo --output ./workspace --write
cd workspace/brand-demo
npm ci
npm run build
npm run dev
```

`V3-02` 是电影化企业官网、`V3-14` 是 SaaS 工作台、`V3-26` 是住宅数字孪生；**其余场景还不能生成可运行代码**。独立构建后查看服务启动的本地地址，不需要部署。

## 故障排查

| 症状 | 先检查 |
|---|---|
| `npx` 或安装失败 | `node --version`、`npm --version`、网络访问、代理、npm registry；检查 Skills CLI 输出 |
| Agent 看不到 Skill | 在正确项目根目录重新打开会话，检查实际目录与 `SKILL.md`；不要把文件存在当成模型发现 |
| 找不到 Python 脚本 | 是否在 `archvela` 仓库根目录，或使用了不属于该 Agent 的安装路径 |
| 提示目标文件已存在 | **预期的安全防护**；更换新输出目录，不要直接覆盖 |
| 想验证“比不装 Skill 更好” | 用 [真实 Agent 评测协议](./AGENT-EVAL-PROTOCOL.md) 和 [试点工具](../benchmarks/README.md)，不能用安装测试替代 |

## 下一步

继续阅读 [场景目录](../.agents/skills/archvela-architect/references/07_V3_全场景蓝图与选型索引.md)、[可运行示例](../examples/README.md)、[架构合同](./PLAN-CONTRACT.md) 和 [贡献指南](../CONTRIBUTING.md)。

> 安全提示：不要将密钥、客户源码或未授权数据交给未知的 Agent 插件或安装器；所有生成文档与架构建议必须由开发者审核后再执行。
