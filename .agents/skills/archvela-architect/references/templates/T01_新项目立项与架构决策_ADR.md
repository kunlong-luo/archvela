# T01｜新项目立项与架构决策（复制后填写）

> 项目名：`<project-name>` · 日期：`YYYY-MM-DD` · 状态：Draft / Approved / Retired

## 1. 一句话产品定位
- 产品给谁用：
- 要解决的单一高频任务：
- 与已有项目相比的差异：
- 愿意长期维护的理由：

## 2. 匹配 V3 场景
- 对应编号（V3-xx）：
- 对应 01–06 领域卷：
- 主场景（只有一个）：
- 次场景（最多两个）：
- 不做的能力：

## 3. 选型表（按需填写，不全装）
| 层 | 候选 | 最终选择 | 为什么 | 放弃了什么 |
|---|---|---|---|---|
| 框架 | Astro / Next.js / React SPA / 既有 | | | |
| 构建 | Astro内置 / Turbopack / Vite / Rsbuild / 引擎导出 | | | |
| UI | Tailwind + shadcn/Base UI / 原有组件 | | | |
| 图标 | Lucide / Phosphor / SVG 资产 | | | |
| 动效 | CSS / Motion / GSAP | | | |
| 图表 | ECharts / Recharts / D3 | | | |
| 2D | SVG / Canvas / Konva / Pixi / Phaser | | | |
| 3D | R3F / Cesium / Babylon / PlayCanvas / 无 | | | |
| 状态 | React local / Zustand / XState | | | |
| 前端数据缓存 | TanStack Query / 无 | | | |

## 4. 单人产品设计签名（必须差异化）
- 品牌故事/特色：
- 色彩与字体、排版体系：
- 代表性动效与视觉素材：
- 关键用户动作与成功反馈：
- 禁止照搬的 UI 风格：

## 5. 前端架构与边界
- 核心用户旅程：
- 模块/feature 边界：
- 复用组件：
- 浏览器与设备支持：
- 重资源 / 客户端边界：
- 模拟数据的明确标记与迁移方案：

## 6. 分包四层
- 源码 package（真正跨项目才抽取）：
- 功能 feature（按用户任务）：
- JS Chunk（路由、3D、图表、编辑器）：
- 资产 pack（图片、视频、GLB、贴图、瓦片、语音）：

## 7. 风险与验收
- 最大技术不确定性：
- 最大真实性/版权/隐私风险：
- 是否要 WebGL 失败降级：
- 是否要低运动偏好支持：
- 一个可用切片的验收：
- 实际测试设备与浏览器：
- 决策复审触发条件：