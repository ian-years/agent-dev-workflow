# Agent Dev Workflow（中文说明）

[English](README.md) | 中文

面向 [Codex](https://codex.openai.com/) 的多 Agent 协作开发工作流。五个可组合的 Skill，通过角色隔离的子 Agent 委派实现：编排者协调、架构师设计、编码者实现、审查者审查。没有任何 Agent 会审查自己的代码。

## 为什么需要

当单个 AI Agent 同时负责设计、实现和审查自己的代码时，它有一个盲区：无法用新鲜的眼光发现自己犯的错。本项目通过将开发拆分为不同阶段，每个阶段交给不同 Agent + 不同模型，让设计、实现、审查始终独立。

## 包含什么

### 5 个工作流 Skill

| Skill | 阶段 | 涉及 Agent | 用户确认点 | 适用场景 |
|-------|------|-----------|-----------|---------|
| `feature-dev` | 协调、设计、实现、测试、审查、归档 | architect、coder、reviewer | Phase 0、Phase 1 | 新功能开发、重构（3+ 文件） |
| `bugfix` | 协调、定位修复、验证、完成 | debugger、coder | Phase 0 | 根因不明的 Bug 修复 |
| `design` | 协调、（提案）、设计、确认 | architect | 每个确认点 | 编码前的方案设计；简单/复杂双模式 |
| `quick-code` | 协调、实现、完成 | 编排者直接执行 | 无 | 琐碎改动（1-2 文件，机械性） |
| `code-review` | 协调、审查、完成 | reviewer | 无 | 对任意 diff 的独立审查 |

### 4 个子 Agent 角色

| Agent | 角色 | 职责 | 绝对不做 |
|-------|------|------|---------|
| `architect` | 设计者 | 读代码库、提架构方案、写带 Task ID 的实现计划 | 绝不写生产代码 |
| `coder` | 实现者 | 实现单个任务、跑测试、带 Task ID 提交 | 绝不审查自己的代码 |
| `debugger` | 调试者 | 追踪代码路径、定位根因、写证据 | 绝不直接修复 |
| `reviewer` | 质量关卡 | 审查 diff 的正确性、安全性、回归风险 | 绝不写代码，看不到实现过程 |

## 架构

```
用户
  |
  v
编排者（主 Codex Agent）
  |--- 委派 ---> architect（设计阶段）
  |--- 委派 ---> coder（实现阶段，每个任务一个）
  |--- 委派 ---> debugger（Bug 定位阶段）
  |--- 委派 ---> reviewer（审查阶段）
  |
  v
项目文件 + git 提交（事实依据）
```

### 关键设计决策

- **纯 Markdown，零运行时依赖。** Skill 是 `.md` 文件，由 Codex 的 skill 系统读取。没有 npm 包、没有脚本、没有数据库。
- **git log 作为幂等键。** 每个 coder 提交包含 Task ID（`[T1]: description`）。中断恢复时，编排者检查 `git log` 跳过已完成的任务。
- **状态文件持久化。** `docs/progress/workflow-state.md` 记录阶段 + 子任务级状态。能在模型断流和上下文压缩后恢复。
- **优雅降级。** 如果子 Agent 不可用（如 CLI 不支持委派），所有工作流回退到 solo 模式，端到端完成。
- **按角色分配模型。** 每个子 Agent 的模型在委派时从 `agents/<role>.md` 的 frontmatter 解析，而不是硬编码在 skill 里。强模型负责设计和审查；高效模型负责实现。

## 安装

### 方式一：Windows PowerShell

```powershell
git clone https://github.com/ian-years/agent-dev-workflow.git
cd agent-dev-workflow
powershell -ExecutionPolicy Bypass -File install.ps1
```

### 方式二：macOS / Linux

```bash
git clone https://github.com/ian-years/agent-dev-workflow.git
cd agent-dev-workflow
bash install.sh
```

### 方式三：手动复制

```bash
git clone https://github.com/ian-years/agent-dev-workflow.git
cd agent-dev-workflow

# 复制 skills
cp -r skills/* ~/.codex/skills/

# 复制 agents
cp -r agents/* ~/.codex/agents/
```

安装后重启 Codex 或开新对话，Skill 会根据你的请求关键词自动触发。

## 配置模型

每个 agent 的 frontmatter 有 `model:` 字段。编辑文件替换为你的实际模型名。这个文件是唯一真源：每个工作流在 Phase 0 和每次委派前读取它，若值为空或仍是占位符（`your-`）就报错停止。

| 文件 | 角色 | 默认占位符 | 建议模型层级 |
|------|------|-----------|------------|
| `agents/architect.md` | 设计 | `your-strong-model` | 最强推理模型 |
| `agents/coder.md` | 实现 | `your-efficient-model` | 高效编码模型 |
| `agents/debugger.md` | 调试 | `your-efficient-model` | 高效编码模型 |
| `agents/reviewer.md` | 审查 | `your-strong-model` | 最强推理模型 |

将 `your-strong-model` 和 `your-efficient-model` 替换为你的实际模型标识符。理由：设计和审查需要深度推理（值得花 Token），而实现和调试是执行密集型（高效模型足够）。

示例配置：

```yaml
# agents/architect.md frontmatter
---
name: architect
model: gpt-4o
description: ...
---
```

```yaml
# agents/coder.md frontmatter
---
name: coder
model: gpt-4o-mini
description: ...
---
```

## 使用方式

直接跟 Codex 对话即可，Skill 会根据关键词触发。

### 新功能开发
```
> 我要开发一个用户认证系统，支持 OAuth
```
Codex 触发 `feature-dev` 工作流（6 阶段）。你在 Phase 0 确认范围，Phase 1 批准设计，Phase 2-5 自动运行。

### Bug 修复
```
> 修个 bug：密码包含特殊字符时登录按钮报 500
```
Codex 触发 `bugfix` 工作流。debugger 追踪根因，coder 应用修复。

### 纯设计
```
> 帮我设计一个 API 缓存层方案
```
Codex 触发 `design` 工作流。不写代码，输出设计文档含方案对比和权衡。

### 快速小改
```
> 给 User 模型加个 phone 字段
```
Codex 触发 `quick-code` 工作流。快速、无审查、适合琐碎改动。

### 独立审查
```
> review 一下最近 3 天的改动
```
Codex 触发 `code-review` 工作流。独立 reviewer 只看 diff。

### 中断后恢复
```
> 继续未完成的工作
```
Codex 读取 `docs/progress/workflow-state.md`，恢复到正确的阶段，保持多 Agent 模式，通过 git log 的 Task ID 检查跳过已完成的子任务。

## 一致性机制

本系统解决了多 Agent 协作的经典一致性挑战：

| 挑战 | 解决方案 |
|------|---------|
| 任务语义重叠（重复执行） | architect 为每个任务声明 affected files AND functions/classes，有交集的必须串行 |
| 部分失败后重试（重复提交） | coder 开始前查 `git log` 是否有自己的 Task ID，有就跳过 |
| 中途断流（未提交的改动） | coder 检查 `git status`，评估部分完成的工作是继续还是清理重来 |
| 编排者崩溃（状态丢失） | `workflow-state.md` 持久化阶段 + 子任务状态，git log 是事实依据 |
| 子 Agent 不可用 | 优雅降级到 solo 模式，工作流永不阻塞 |

## 项目结构

```
agent-dev-workflow/
  .codex-plugin/
    plugin.json              # Codex 插件清单
  agents/
    architect.md             # 设计 Agent（强模型）
    coder.md                 # 实现 Agent（高效模型）
    debugger.md              # 调试 Agent（高效模型）
    reviewer.md              # 独立审查 Agent（强模型）
  skills/
    feature-dev/
      SKILL.md               # 6 阶段功能开发工作流
      references/
        workflow-state.md    # 状态持久化与恢复协议
    bugfix/
      SKILL.md               # 4 阶段 Bug 修复工作流
      references/
        workflow-state.md
    design/
      SKILL.md               # 设计工作流（简单/复杂双模式）
      references/
        workflow-state.md
    quick-code/
      SKILL.md               # 3 阶段快速实现
      references/
        workflow-state.md
    code-review/
      SKILL.md               # 3 阶段独立审查
      references/
        workflow-state.md
  templates/
    feature-plan.md           # 设计文档模板
    bug-report.md            # Bug 报告模板
    review-report.md         # 审查报告模板
    workflow-state.md        # 状态文件模板
  references/
    workflow-state.md        # 共享状态持久化协议
  AGENTS.md                  # 项目级 Agent 指令
  README.md                  # 英文说明
  README_CN.md               # 中文说明
  LICENSE
```

## 环境要求

- [Codex](https://codex.openai.com/)（桌面版或支持子 Agent 委派的 CLI）
- Git（用于幂等和状态追踪）
- 任意代码库（工作流与语言无关）

## 已知限制

- 子 Agent 委派需要 Codex 桌面版或支持委派的 CLI。在不支持的环境里，工作流降级为 solo 模式（较弱：自审而非独立审查）。
- agent frontmatter 的 `model:` 字段是委派的唯一真源。每个工作流在 Phase 0 和每次委派前解析它，若缺失或仍是占位符就快速失败。实际模型是否可用仍取决于 Codex 的委派实现。
- 状态持久化使用 Markdown 文件而非数据库。适用于单开发者工作流，不适用于并发多 Agent 系统。

## 贡献

参见 [CONTRIBUTING.md](CONTRIBUTING.md)。欢迎提交 Bug 报告和 Pull Request。

## 开源协议

[MIT License](LICENSE)
