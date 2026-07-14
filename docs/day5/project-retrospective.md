# Plane AI Testing Project — 项目复盘

## 一、五天实际完成内容

### Day 1 — 项目初始化与环境基线

- 项目目录结构搭建
- Plane Community Edition v1.3.1 Docker Compose 部署
- 12 服务运行确认，1 migrator 成功退出
- 环境基线采集（OS、Docker、端口、健康检查）
- 系统分析文档（服务拓扑、API 结构、数据库结构）
- .gitignore、安全基线配置

### Day 2 — 需求分析与 API 探索

- 测试需求分析与用例设计
- Plane REST API 系统性探索
- API 认证机制验证（X-API-Key）
- 核心接口文档化（工作区、项目、工作项、成员、状态、标签）
- API 测试骨架搭建

### Day 3 — 接口自动化与 Playwright 核心流程

- API 自动化测试开发（pytest + requests）
- Playwright 核心 UI 流程自动化
- 页面对象（Page Object）模式实现
- 登录、工作区、项目、工作项流程覆盖
- 权限测试
- HTML 报告产出

### Day 4 — 数据库断言、异常测试与 Jenkins Pipeline

- PostgreSQL 数据库 Schema 验证
- API-DB 工作项一致性断言（创建→查询→更新→删除 全生命周期）
- API 异常场景测试
- Jenkins Pipeline 设计与实现
- Jenkins Agent (plane-qa-runner) 配置
- CI 凭据管理
- 自动清理机制

### Day 5 — 回归、凭据收口、证据归档与报告

- Jenkinsfile 凭据 ID 统一收口（plane-ui-email-v2 / password-v2）
- UI Credential Smoke 前置校验阶段
- 完整流水线验证（Build #10: SUCCESS）
- 最终测试报告生成
- 项目复盘与面试总结
- 证据归档

---

## 二、使用的工具与框架

| 层次 | 工具 | 用途 |
|---|---|---|
| 被测系统 | Plane Community Edition v1.3.1 | 开源项目管理平台 |
| 容器化 | Docker Compose | Plane 服务部署与管理 |
| API 测试 | Python, pytest, requests, jsonschema, pytest-html | API 自动化测试 |
| 数据库测试 | Python, psycopg (psycopg2) | PostgreSQL 直连验证 |
| UI 测试 | Playwright, TypeScript, Chromium | UI 端到端自动化 |
| CI/CD | Jenkins (Pipeline) | 持续集成流水线 |
| CI Agent | Docker-based Jenkins inbound agent | 测试执行环境 |
| 版本管理 | Git | 代码版本控制 |
| 报告 | JUnit XML, pytest-html, Playwright HTML Reporter | 测试报告产出 |
| AI 辅助 | ChatGPT, Codex, Claude Code | 方案设计、代码编写、执行与排障 |

---

## 三、遇到的主要问题

### 3.1 环境与基础设施

| 问题 | 严重程度 | 分类 |
|---|---|---|
| Plane Docker Compose 服务启动顺序与依赖等待 | 中 | 环境问题 |
| Plane HTTPS 自签名证书导致 curl 健康检查需 `-k` | 低 | 环境问题 |
| SCP 文件传输时 dos2unix 不可用 | 低 | 环境问题 |

### 3.2 API 测试

| 问题 | 严重程度 | 分类 |
|---|---|---|
| Plane API 429 限流导致连续测试失败 | 高 | 测试环境问题 |
| 测试数据残留 (AUTO-D) 污染后续运行 | 高 | 自动化设计问题 |
| API ReadTimeout 偶发（网络抖动） | 低 | 测试环境问题 |

### 3.3 Jenkins CI

| 问题 | 严重程度 | 分类 |
|---|---|---|
| Pipeline Script 配置方式错误 | 中 | CI 配置问题 |
| 凭据注入未生效 | 高 | 凭据管理问题 |
| UI 凭据记录内容不一致导致登录失败（Build #4-#8） | 严重 | 凭据管理问题 |

### 3.4 UI 自动化

| 问题 | 严重程度 | 分类 |
|---|---|---|
| UI-007 首次执行超时未找到修改后的元素 | 低 | 自动化稳定性问题 |
| Playwright auth state 在不同项目间共享的隔离问题 | 中 | 自动化设计问题 |

---

## 四、如何定位与解决

### 4.1 凭据问题定位（Build #4-#8 的关键排障链）

```
1. 假设：Playwright 脚本或页面对象有 bug
   → 在 Agent 容器内手动执行 auth.setup.ts：1 passed
   → 排除：代码和框架正常

2. 假设：Plane 服务问题
   → 同一时刻手动输入凭据登录成功
   → 排除：服务正常

3. 假设：Jenkins 凭据注入有问题
   → 对比手动输入的值与 Jenkins Credential 记录
   → 确认：凭据记录内容不一致

4. 解决：新建凭据 → 更新 Jenkinsfile → 验证通过
```

### 4.2 限流问题定位

```
1. 观察：API 测试批量失败，HTTP 429
2. 查阅 Plane 源码/文档，确认有限流机制
3. 在流水线中增加 45s 冷却间隔
4. 在 Python 测试代码中增加指数退避重试
5. 验证：后续构建不再出现因限流导致的批量失败
```

---

## 五、AI 工具参与方式

### 5.1 角色分工

| 角色 | AI 工具 | 职责 |
|---|---|---|
| 测试架构师 | ChatGPT | 总体规划、测试方案设计、问题分析、结果审核 |
| 高级工程师 | Codex (Claude Code IDE) | 测试代码编写、文档编写、代码审查、项目整理 |
| 执行工程师 | Claude Code Linux | Linux 环境操作、Docker 部署、测试执行、日志采集 |

### 5.2 AI 参与的具体环节

| 环节 | AI 参与 | 人工确认 |
|---|---|---|
| 测试方案设计 | ChatGPT 生成方案 | ✅ 人工审核通过后执行 |
| API 测试代码 | Codex 编写 pytest 用例 | ✅ 人工检查断言覆盖和边界 |
| Playwright 测试代码 | Codex 编写 TypeScript 用例 | ✅ 人工验证定位器和流程 |
| Jenkinsfile | Codex 生成 + Claude Code 修改 | ✅ 人工审查凭据绑定和安全 |
| 测试执行 | Claude Code 执行命令和脚本 | ✅ 人工确认输出和结果 |
| 缺陷分析 | ChatGPT 分析失败原因 | ✅ 人工区分环境问题和产品缺陷 |
| 报告生成 | Claude Code 整理数据和输出 | ✅ 人工确认准确性和完整性 |

### 5.3 最终判断

所有最终判断和确认由人工完成：
- 是否建议交付
- Flaky 用例是否修改
- 测试覆盖是否充分
- 报告内容是否准确

---

## 六、项目中的不足

1. **UI 测试覆盖偏窄** — 10 条用例集中在核心流程，边缘路径（如权限边界、并发操作、异常输入）未覆盖。
2. **API 测试未使用 Schema 严格校验** — 当前验证响应状态和关键字段，未对全部响应体做 JSON Schema 验证。
3. **数据库测试依赖已知 API 行为** — 未独立构造数据库写入场景验证约束和触发器。
4. **负载/性能测试缺失** — 未对 API 或数据库进行并发或压力测试。
5. **CI Agent 镜像缺少文档** — plane-qa-runner-v2 的构建过程和依赖未文档化。
6. **Flaky 用例未深入分析** — UI-007 的根本原因（页面刷新 vs 异步加载 vs 数据同步）未通过 trace 或日志精确定位。

---

## 七、下一步可优化方向

| 优先级 | 方向 | 说明 |
|---|---|---|
| 高 | UI 测试扩展 | 增加权限边界、筛选、排序、批量操作等场景 |
| 高 | JSON Schema 验证 | 对 API 响应体做结构化断言 |
| 中 | UI-007 根因分析 | 采集 trace + 日志精确定位超时原因并优化等待策略 |
| 中 | 性能基线 | 为关键 API 建立响应时间基线，检测回归 |
| 低 | 并行化 | 探索 Jenkins Parallel Stage 拆分 API/DB/UI 为独立并行阶段 |
| 低 | Agent 镜像文档化 | 记录 plane-qa-runner-v2 的 Dockerfile 和依赖清单 |
| 低 | 告警通知 | 集成 Jenkins 通知（邮件/IM），失败时主动告警 |

---

## 八、时间线

| 日期 | Day | 主要产出 |
|---|---|---|
| 2026-07-12 | Day 1 | 项目初始化、Plane 部署、环境基线 |
| 2026-07-12 | Day 2 | 需求分析、API 探索、用例设计 |
| 2026-07-13 | Day 3 | API 自动化、Playwright 核心流程 |
| 2026-07-13 | Day 4 | 数据库断言、Jenkins Pipeline |
| 2026-07-14 | Day 5 | 凭据收口、Build #10 成功、报告归档 |

---

## 九、数据摘要

| 指标 | 数值 |
|---|---|
| 测试代码文件 | 16 |
| API 唯一用例 | 37 |
| DB 用例 | 19 |
| UI 用例 | 10 |
| 唯一业务测试 | 66 |
| Jenkins 构建次数 | 10 (最终 #10 成功) |
| Pipeline 阶段 | 12 |
| 发现的产品缺陷 | 0 |
| 环境/配置问题 | 多次（已全部解决） |
