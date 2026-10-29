# Archvela Agent Skill · 客户端 L2/L3 手工测试脚本

以下测试可用于 OpenCode、Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot、Windsurf、Roo Code、Cline、Kiro 等**真实客户端**。

**运行规则：** 使用全新的空项目目录、非生产数据和无密钥环境；先记录客户端版本、模型和权限。该文件是验收任务，不是已经通过的证据。

## T1 · Skill 发现

> 请在当前客户端列出可用的 Skills，并找出 `archvela-architect`。告诉我技能来源目录，不允许安装新依赖、读取私人文件或修改当前项目。

**通过条件：** 能从当前 Agent 的本地 Skill 清单读取正确名称与描述。纯文件路径静态检查不算通过。

## T2 · 简单/高端企业官网架构

> 使用 `archvela-architect` 找出“高端动态企业官网”对应的 V3 场景，比较 Astro 和 Next.js 作为官网技术架构的适用条件。设计 Motion + GSAP + 3D 产品预览 + 视频回退方案。输出 ADR、源码包、功能模块、代码 Chunk、媒体 Asset Pack、SEO、核心性能指标与 MVP。只输出建议，不修改项目文件。

**通过条件：** 不将 SEO 内容和大型 3D 全部变成客户端 JS；给出 reduced-motion、弱网及 WebGL 不支持时的回退。

## T3 · 农村与住宅数字孪生

> 使用 `archvela-architect` 定位 V3-26，并只读取数字孪生领域资料。设计实际尺寸约束、楼层场景、设施状态渲染和 GIS 与室内 3D 场景的模块隔离。生成四层分包方案及验收清单，不执行任何写入。

**通过条件：** 不把 CesiumJS、Three.js 和 Babylon.js 全部强塞进同一个 Canvas；给出尺寸、坐标与模型溯源的验证方式。

## T4 · 独立网页游戏

> 使用 `archvela-architect` 定位 V3-45，为原创 3D 塔防网页游戏选择 Babylon.js/PlayCanvas/Unity Web，给出战斗状态机、引擎主循环、技能 VFX、GLB/纹理/关卡 Asset Pack 和一关 MVP 验收。只规划，不部署。

**通过条件：** React UI 不逐帧驱动战斗；不建议复制他人的版权角色与素材；阐明移动端内存/FPS 真实验收需求。

## T5 · 生成器无覆盖

在**明确授权的测试目录**，运行

```bash
python3 scripts/new_project_docs.py --scene V3-26 --project test-twin --output ./sandbox
# 记录没有产生文件
python3 scripts/new_project_docs.py --scene V3-26 --project test-twin --output ./sandbox --write
# 只生成 3 个 Markdown 文件
python3 scripts/new_project_docs.py --scene V3-26 --project test-twin --output ./sandbox --write
# 拒绝覆盖
```

**通过条件：** 无未授权写入、首次写入仅 3 个架构文档、重复写入无破坏。

## 结果记录

```text
客户端名称 / 版本：
操作系统：
Skill 路径：
模型及授权：
测试 T1–T5：通过 / 失败 / 跳过
实际证据（截图、终端记录、目录清单）：
是否调用任何网络/付费 API：
失败复现与修复建议：
```
