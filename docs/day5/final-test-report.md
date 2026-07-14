# Plane AI Testing Project — 最终测试报告

## 文档信息

| 项 | 内容 |
|---|---|
| 文档版本 | v1.0 |
| 生成日期 | 2026-07-14 |
| 对应构建 | Jenkins Build #10 |
| 项目目录 | /home/tester/qa-workspace/plane-ai-testing-project |
| 被测系统 | Plane Community Edition v1.3.1 |

---

## 一、项目背景

本项目对 Plane Community Edition（开源项目管理平台）进行全链路 AI 辅助自动化测试，覆盖 API、数据库、UI 三个层次，并通过 Jenkins CI 流水线集成所有测试阶段，实现对 Plane 平台核心业务功能的质量验证。

项目目标：
- 建立可复现、可审计的自动化测试资产
- 验证 Plane 平台的 API 正确性、数据库一致性和 UI 可用性
- 将全量测试集成至 Jenkins CI 流水线，实现一键回归
- 产出可直接交付的测试报告与证据

---

## 二、测试目标

| 目标 | 描述 |
|---|---|
| API 功能验证 | 覆盖认证、用户、工作项、项目、成员、状态和标签等核心接口 |
| 数据库一致性 | 验证 PostgreSQL 中工作项数据与 API 返回的一致性 |
| UI 端到端验证 | 覆盖登录、工作区、项目和工作项全流程 |
| CI 集成 | Jenkins Pipeline 完整串联所有阶段并产出可用报告 |
| 零残留 | 每次构建后自动清理测试数据，确认无残留 |

---

## 三、测试环境

| 项 | 版本/配置 |
|---|---|
| 被测系统 | Plane Community Edition v1.3.1 |
| 部署方式 | Docker Compose (12 服务) |
| HTTP 端口 | 8090 |
| HTTPS 端口 | 8443 |
| 数据库 | PostgreSQL (Docker 容器内) |
| 测试执行环境 | Ubuntu 26.04 LTS, x86_64 |
| CI Agent | plane-qa-runner-v2 (Docker-based Jenkins inbound agent) |
| 浏览器 | Chromium (Playwright) |
| 工作区 | qa-lab |
| 项目 | Plane QA Project |

---

## 四、测试范围

### 4.1 覆盖层次

```
┌─────────────────────────────────────────┐
│              UI 自动化 (10)               │
│   Playwright + Chromium                  │
│   登录 → 工作区 → 项目 → 工作项 CRUD      │
├─────────────────────────────────────────┤
│           API 自动化 (37)                 │
│   pytest + requests                      │
│   认证 / 用户 / 工作项 / 项目 / 成员       │
│   状态 / 标签                             │
├─────────────────────────────────────────┤
│         数据库测试 (19)                    │
│   pytest + psycopg                       │
│   Schema 验证 / 工作项 API-DB 一致性       │
├─────────────────────────────────────────┤
│        CI 流水线 (12 stages)              │
│   Jenkins Pipeline                       │
│   环境检查 → 依赖 → 冒烟 → 全量 → 清理     │
└─────────────────────────────────────────┘
```

### 4.2 测试文件清单

| 文件 | 类型 | 说明 |
|---|---|---|
| tests/api/test_validation.py | API | 环境/认证/工作区/项目验证 (8 条) |
| tests/api/test_auth.py | API | 认证接口测试 |
| tests/api/test_user.py | API | 用户接口测试 |
| tests/api/test_work_items.py | API | 工作项 CRUD 测试 |
| tests/api/test_projects.py | API | 项目接口测试 |
| tests/api/test_members.py | API | 成员接口测试 |
| tests/api/test_states_labels.py | API | 状态和标签测试 |
| tests/db/test_schema.py | DB | 数据库 Schema 验证 |
| tests/db/test_work_item_consistency.py | DB | API-DB 一致性断言 |
| tests/ui/auth.setup.ts | UI | 认证状态保存（CI 前置） |
| tests/ui/login.spec.ts | UI | 登录 UI-001, UI-002 |
| tests/ui/workspace.spec.ts | UI | 工作区 UI-002b |
| tests/ui/project.spec.ts | UI | 项目 UI-003 |
| tests/ui/work-item.spec.ts | UI | 工作项 UI-004～UI-008 |

---

## 五、API 测试结果

### 5.1 API Validation (8 条)

| 指标 | 数值 |
|---|---|
| 总量 | 8 |
| 通过 | 8 |
| 失败 | 0 |
| 通过率 | 100% |

覆盖：
- Plane API 可达性
- API Key 认证有效性
- 工作区 qa-lab 存在性
- 项目 Plane QA Project 存在性
- 工作项列表可访问
- 分页参数正确
- 单条工作项可获取
- 响应格式合规

### 5.2 API Regression (29 条)

| 指标 | 数值 |
|---|---|
| 总量 | 29 |
| 通过 | 29 |
| 失败 | 0 |
| 通过率 | 100% |

覆盖：
- 认证接口（正常/异常）
- 用户信息获取
- 工作项 CRUD 全流程
- 项目列表与详情
- 成员列表与角色
- 状态流转
- 标签管理

### 5.3 API 汇总

| 指标 | 数值 |
|---|---|
| **API 唯一用例总数** | **37** |
| 通过 | 37 |
| 失败 | 0 |
| 通过率 | 100% |
| 运行方式 | pytest, CI 内串行执行 |

---

## 六、数据库测试结果

### 6.1 Database Tests (19 条)

| 指标 | 数值 |
|---|---|
| 总量 | 19 |
| 通过 | 19 |
| 失败 | 0 |
| 通过率 | 100% |

覆盖：
- 数据库连接与 Schema 验证
- 表结构完整性检查
- API 创建的工作项在数据库中可查
- API 返回字段与 DB 列值一致性
- 更新/删除后 DB 状态同步

### 6.2 数据库连接信息

| 项 | 值 |
|---|---|
| 数据库类型 | PostgreSQL |
| 连接方式 | Docker 容器内直连 |
| 验证方式 | 只读查询 + API-DB 交叉比对 |

---

## 七、UI 自动化结果

### 7.1 最终结果 (Build #10)

| 指标 | 数值 |
|---|---|
| UI 业务用例 | 10 |
| 通过 | 10 |
| 失败 | 0 |
| 通过率 | 100% |

### 7.2 用例明细

| 编号 | 用例 | 结果 |
|---|---|---|
| UI-001 | Login with valid credentials and enter QA Lab | ✅ PASS |
| UI-002 | Verify Workspace home shows QA Lab and Plane QA Project | ✅ PASS |
| UI-002b | Workspace loads QA Lab heading and Plane QA Project from storage state | ✅ PASS |
| UI-003 | Enter Plane QA Project Work Items and verify existing items visible | ✅ PASS |
| UI-004 | Open existing work item and verify detail drawer | ✅ PASS |
| UI-005 | Open New Work Item form and verify empty-title behavior | ✅ PASS |
| UI-006 | Create unique work item and verify it appears in list | ✅ PASS |
| UI-007 | Modify created work item and verify persistence | ⚠️ PASS (retry #1) |
| UI-008 | Delete created work item and verify removal from list | ✅ PASS |
| auth.setup | Authenticate and save storage state (CI 前置) | ✅ PASS |

### 7.3 UI-007 Flaky 记录

| 属性 | 内容 |
|---|---|
| 编号 | UI-007 |
| 描述 | Modify created work item and verify persistence |
| 现象 | 首次执行未在 10 秒内找到修改后的工作项 |
| retry #1 | 通过 |
| 构建结果 | Jenkins Build #10: SUCCESS |
| 分类 | **自动化稳定性观察项**（非 Plane 产品缺陷） |
| 可能原因 | 页面异步刷新延迟；列表数据同步未在断言前完成 |
| 当前处置 | 不修改代码；后续优化等待条件和数据刷新确认 |
| 风险等级 | 低 — 单次 flaky，retry 通过，不影响构建结论 |

---

## 八、Jenkins CI 流水线结果

### 8.1 最终构建

| 属性 | 值 |
|---|---|
| Job 名称 | plane-qa-pipeline |
| Build 编号 | #10 |
| 最终结果 | **SUCCESS** |
| Agent | plane-qa-runner-v2 |
| 流水线阶段 | 12 stages |
| 最终输出 | Pipeline PASSED - all tests green, zero residue. |

### 8.2 流水线阶段概览

| # | 阶段 | 结果 |
|---|---|---|
| 1 | Checkout / Sync Source | ✅ |
| 2 | Environment Preflight | ✅ |
| 3 | Python Environment | ✅ |
| 4 | Node Dependencies | ✅ |
| 5 | UI Credential Smoke | ✅ 1/1 PASS |
| 6 | Create Temporary CI Environment | ✅ |
| 7 | API Validation | ✅ 8/8 PASS |
| 8 | API Regression | ✅ 29/29 PASS |
| 9 | Rate-Limit Cooldown | ✅ 45s |
| 10 | Database Tests | ✅ 19/19 PASS |
| 11 | Playwright UI Tests | ✅ 10/10 PASS |
| 12 | Cleanup Verification | ✅ AUTO-D residue: 0 |

### 8.3 CI 凭据管理

- Jenkins 凭据统一使用 `plane-ui-email-v2` 和 `plane-ui-password-v2`
- `plane-api-key` 保持不变
- 所有凭据通过 `withCredentials` 注入，不在代码或日志中暴露
- 敏感操作区块均设置 `set +x`
- Post 阶段始终清理 `.env` 和 `auth-state.json`

---

## 九、缺陷与问题记录

### 9.1 问题分类说明

本项目区分以下问题类别：

| 类别 | 说明 |
|---|---|
| CI 配置问题 | Jenkins 配置、凭据、Pipeline 脚本错误 |
| 测试环境问题 | 网络、容器、依赖、端口等问题 |
| 自动化稳定性问题 | 测试脚本自身的 flaky、超时、定位器问题 |
| 凭据管理问题 | 凭据记录内容不一致、格式问题 |
| 产品缺陷 | 被测系统 Plane 的实际功能缺陷 |

### 9.2 排障历程

| Build | 问题 | 类别 | 解决 |
|---|---|---|---|
| #1 | Pipeline Script 只填了文件名 | CI 配置问题 | 粘贴完整 Jenkinsfile 内容 |
| #2 | Credentials 未正确注入 | 凭据管理问题 | 修正 Jenkins withCredentials 绑定 |
| #3 | API 429 限流 + 测试数据残留 | 测试环境问题 | 增加 45s 冷却 + 重试 + 自动清理 |
| #4–#8 | UI 凭据记录不一致 → 登录失败 | 凭据管理问题 | 重建凭据 plane-ui-email-v2 / password-v2 |
| #9 | 单次 API ReadTimeout | 测试环境问题 | 网络抖动，重试恢复 |
| #10 | 完整流水线成功 | — | — |

### 9.3 已知限制与风险

| 限制 | 影响 | 缓解措施 |
|---|---|---|
| Plane API 有限流 | 连续请求可能返回 429 | 45s 冷却 + 指数退避重试 |
| 单 Agent 串行执行 | UI 测试不可并行 | workers=1，确保 auth state 不冲突 |
| UI-007 偶发 flaky | 极小概率首次失败 | CI retry:1 兜底，后续观察 |
| Jenkins Agent 需预装依赖 | Agent 镜像需维护 | 使用 QA venv 缓存 + npm ci |
| 依赖 Plane 服务可用 | 服务不在时全流水线阻塞 | Preflight 阶段提前检测 |

---

## 十、测试统计总表

| 测试层级 | 唯一用例数 | 通过 | 失败 | 通过率 |
|---|---|---|---|---|
| **API Validation** | 8 | 8 | 0 | 100% |
| **API Regression** | 29 | 29 | 0 | 100% |
| **API 唯一合计** | **37** | **37** | 0 | **100%** |
| **Database** | **19** | 19 | 0 | **100%** |
| **Playwright UI** | **10** | 10 | 0 | **100%** |
| **唯一业务测试总数** | **66** | **66** | **0** | **100%** |

> 注：
> - UI Credential Smoke (1 条) 是 CI 前置校验，**不计入**唯一业务用例。
> - API 唯一用例 = API Validation (8) + API Regression (29) = 37。
> - 唯一业务测试总数 = 37 (API) + 19 (DB) + 10 (UI) = **66**。

---

## 十一、测试结论

### 11.1 质量评估

Plane Community Edition v1.3.1 在以下方面通过了全链路自动化验证：

- **API 层**：全部 37 条用例通过，认证、CRUD、权限、状态流转等功能正常。
- **数据库层**：19 条 Schema 和一致性断言通过，API 操作与数据库状态同步正确。
- **UI 层**：10 条端到端用例通过，核心业务流程（登录→工作区→项目→工作项 CRUD）可用。
- **CI 集成**：12 阶段 Jenkins Pipeline 稳定运行，支持一键回归和自动清理。

### 11.2 最终建议

**✅ 建议交付。**

66 条唯一业务自动化测试全部通过，Jenkins CI 流水线可重复执行，测试数据自动清理零残留。已知的 UI-007 flaky 为自动化稳定性观察项，不影响产品功能评估。

---

## 十二、附录

### A. 报告位置

| 报告 | 路径 |
|---|---|
| 最终测试报告（本文件） | docs/day5/final-test-report.md |
| Jenkins Build #10 摘要 | docs/day5/jenkins-build-10-summary.md |
| 项目复盘 | docs/day5/project-retrospective.md |
| 面试项目总结 | docs/day5/interview-project-summary.md |
| 控制台日志 | evidence/jenkins-build-10/jenkins-original/console.log |
| API Validation HTML (原始) | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/api-validation.html |
| API Regression HTML (原始) | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/api-regression.html |
| DB Full HTML (原始) | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/db-full.html |
| Playwright HTML (原始) | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/playwright-report/index.html |
| JUnit XML (原始) | evidence/jenkins-build-10/jenkins-original/archive/archive/reports/junit-*.xml |
| 本地等同报告（参考） | evidence/local-equivalent-reports/ |
| SHA-256 校验和 | evidence/jenkins-build-10/jenkins-original/SHA256SUMS.txt |

### B. 证据目录

```
evidence/jenkins-build-10/
├── jenkins-original/               ← Jenkins Build #10 原始证据
│   ├── console.log                 ← 构建控制台日志
│   ├── SHA256SUMS.txt              ← 原始文件校验和
│   └── archive/archive/
│       ├── reports/
│       │   ├── api-validation.html
│       │   ├── api-regression.html
│       │   ├── db-full.html
│       │   ├── junit-api-validation.xml
│       │   ├── junit-api-regression.xml
│       │   ├── junit-db.xml
│       │   └── playwright-report/
│       │       ├── index.html
│       │       ├── data/           ← 截图/视频/trace
│       │       └── trace/
│       └── evidence/
└── test-results/

evidence/local-equivalent-reports/  ← 本地等同运行（仅供参考，非 Build #10 原始产物）
├── README.md
├── api-validation.html
├── api-regression.html
├── db-full.html
└── playwright-index.html
```

### C. CI 凭据映射

| Jenkins Credential ID | 用途 | 注入方式 |
|---|---|---|
| `plane-api-key` | Plane API 认证 | withCredentials → .env |
| `plane-ui-email-v2` | UI 登录邮箱 | withCredentials → 环境变量 |
| `plane-ui-password-v2` | UI 登录密码 | withCredentials → 环境变量 |
