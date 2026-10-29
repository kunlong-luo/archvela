# Archvela · 可机器检查的架构规划合同

用于 OpenCode、Codex、Claude Code、Cursor、Gemini CLI 等 AI 编程代理交接架构规划进度，而不要求代理共享某一厂商的专有会话格式。

## 生成方式

在 Archvela 仓库目录运行：

```bash
SKILL=".agents/skills/archvela-architect"
python3 "$SKILL/scripts/new_project_docs.py" \
  --scene V3-26 --project home-twin --output ./demo --plan-json --json
# 此时仅预演，未写入任何文件

# 核对路径并同意后，添加 --write；输出合法 JSON 收据
python3 "$SKILL/scripts/new_project_docs.py" \
  --scene V3-26 --project home-twin --output ./demo --plan-json --write --json
```

这会在 `demo/docs/architecture/` 下新增三份 Markdown 和 `archvela-plan.json`。如果任一文件存在则拒绝写入；失败只回滚本轮新创建的文件。默认不带 `--plan-json` 时仍仅生成三份 Markdown。项目根目录、`docs` 或 `architecture` 是符号链接时拒绝写入。

## 数据合同字段

- `schema_version: 1`：当前合同版本；不擅自更新已有合同。
- `project`、`scenario`：项目名称、V3 场景 ID/名称/领域；验证器会和场景目录核对一致性。
- `status`：`draft`、`reviewed`、`delivered`。
- `stack`：候选技术栈、选定技术、决策理由、被否定方案。
- `boundaries`：四层分包 `package`、`feature`、`chunk`、`assets`，同时保留初始建议和最终方案。
- `fallback`：低性能设备、无 WebGL、弱网、减少动画等实际适用回退。
- `repository_audit`：是否审计过真实项目、所依据的文件或记录。
- `target_environment`：浏览器、设备和目标用户环境。
- `risks`：初始风险与实际缓解措施。
- `delivery`：MVP、PR 切片、计划测试、实际测试记录、测量结果。
- `provenance`：内容来源及实现真实性的自声明。

所有字段是跨工具交接契约，不包含私有 API Token、生产账户数据或自动部署指令。

## 三档质量门禁

| 层级 | 检查项 | 不代表什么 |
|---|---|---|
| `draft` | 格式有效，V3 场景真实，候选栈与四层建议存在 | 不代表方案经过项目审计 |
| `reviewed` | 已选择技术并写出理由、四层最终边界、代码审计证据、目标设备与验收计划 | 不代表编译、E2E 或性能测试通过 |
| `delivered` | 有测试记录、至少一个通过的测试、不存在失败测试、实测值与证据引用，以及交付声明 | **不代表校验器亲自运行过那些测试或核实了证据真假** |

用法：

```bash
python3 "$SKILL/scripts/plan_contract.py" \
  ./demo/docs/architecture/archvela-plan.json --level draft --json
python3 "$SKILL/scripts/plan_contract.py" \
  ./demo/docs/architecture/archvela-plan.json --level reviewed
python3 "$SKILL/scripts/plan_contract.py" \
  ./demo/docs/architecture/archvela-plan.json --level delivered
```

刚生成的合同只会通过 `draft`；`reviewed` 与 `delivered` 必须由开发者或代理加入真实项目证据后才可能通过。仅填写字符串或伪造数据不能替代验证。

## 可靠性与边界

1. Archvela **不执行** `archvela-plan.json` 中提到的 Shell、JavaScript、测试命令或部署操作，只读解析 JSON。
2. 使用标准库而不是把数据库、模型 SDK、JSON Schema 依赖安装进 Skill；每种代理安装后都可离线执行验证。
3. CI 分别测 `draft` 成功、未填写的 `reviewed` 失败、检查失败测试不可冒充 `delivered`，并在 26 组隔离代理安装中实际运行 JSON 文档生成与草案合同验证。
4. AI 生成内容需要人工复核。真实质量须再检查构建日志、CI 链接、测试覆盖、设备参数和数据/素材许可证。

下一阶段可为真正的应用脚手架提供验收证据自动采集；本合同目前是**可审计的计划和证据组织格式**，而非可信的测试执行系统。
