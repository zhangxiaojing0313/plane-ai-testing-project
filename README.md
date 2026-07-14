# Plane AI Testing Project

## 项目定位

本项目是针对 Plane Community Edition 的企业级项目管理平台 AI 辅助全链路测试实践。项目以真实测试工程流程为主线，逐步建设环境基线、需求与用例、接口自动化、UI 自动化、数据库断言、持续集成、缺陷与测试报告等可复核资产。

## 项目状态

**✅ 已完成 — 建议交付**

| 指标 | 数值 |
|---|---|
| 唯一业务测试总数 | 66 |
| API 唯一用例 | 37 |
| 数据库用例 | 19 |
| UI 端到端用例 | 10 |
| 通过率 | 100% |
| Jenkins CI 阶段 | 12 |
| 最终构建 | Build #10 SUCCESS |
| AUTO-D 残留 | 0 |
| 发现的产品缺陷 | 0 |

## 测试架构

```
       ┌──────────┐
       │ UI (10)   │  Playwright + TypeScript + Chromium
       ├──────────┤   登录 → 工作区 → 项目 → 工作项 CRUD
       │ API (37)  │  pytest + requests + jsonschema
       ├──────────┤   认证 / 用户 / 工作项 / 项目 / 成员 / 状态 / 标签
       │ DB (19)   │  pytest + psycopg
       └──────────┘   Schema 验证 + API-DB 一致性交叉断言
```

## 测试目标

- 建立可复现、可审计的 Plane 测试项目骨架
- 基于实际部署环境完成需求分析、接口探索和核心业务验证
- 使用 Python、pytest、requests 建设 API 自动化；使用 Playwright 与 TypeScript 建设 UI 自动化
- 将 PostgreSQL 数据库断言、Docker Compose 环境检查和 Jenkins Pipeline 纳入质量验证链路
- 保留命令、日志、报告和截图等证据，并避免提交任何敏感信息

## 五天计划概览

| 阶段 | 重点 | 状态 |
|---|---|---|
| Day 1 | 项目初始化、部署、环境基线、系统分析 | ✅ |
| Day 2 | 需求分析、测试用例设计、API 探索 | ✅ |
| Day 3 | 接口自动化、Playwright 核心流程、权限测试 | ✅ |
| Day 4 | 数据库断言、异常测试、Jenkins Pipeline | ✅ |
| Day 5 | 回归、凭据收口、测试报告、证据归档 | ✅ |

完整安排见 docs/project-plan.md。

## 技术栈

- 被测系统：Plane Community Edition v1.3.1
- API 自动化：Python、pytest、requests、pytest-html、jsonschema
- UI 自动化：Playwright、TypeScript、Chromium
- 数据库验证：PostgreSQL、psycopg (psycopg2)
- 环境与交付：Linux (Ubuntu 26.04)、Docker Compose、Jenkins Pipeline
- AI 辅助：ChatGPT (方案设计)、Codex (代码与文档)、Claude Code (执行与排障)

## 目录说明

| 路径 | 用途 |
|---|---|
| docs/ | 项目计划、环境基线、部署记录、系统分析、Day 1-5 文档 |
| docs/day5/ | 最终测试报告、构建摘要、项目复盘、面试总结 |
| tests/api/ | API 自动化测试代码（8 文件，37 条用例） |
| tests/ui/ | Playwright UI 自动化测试代码（5 文件，10 条用例） |
| tests/db/ | 数据库断言测试代码（3 文件，19 条用例） |
| pages/ | Page Object 页面对象 |
| utils/ | 可复用测试工具 |
| test-data/ | 脱敏且可重复使用的测试数据 |
| scripts/ | 环境采集与健康检查脚本 |
| reports/ | 生成的测试报告目录 |
| evidence/ | 按阶段归档、可追溯的测试证据 |
| evidence/jenkins-build-10/ | Build #10 最终报告归档 |
| .qa/ | 项目上下文与变更影响记录 |

## Jenkins CI

| 属性 | 值 |
|---|---|
| Job | plane-qa-pipeline |
| Agent | plane-qa-runner-v2 |
| Pipeline | 12 stages (Declarative) |
| 凭据 | plane-api-key, plane-ui-email-v2, plane-ui-password-v2 |
| 最终构建 | Build #10 — SUCCESS |

### Pipeline 阶段

1. Checkout / Sync Source
2. Environment Preflight
3. Python Environment
4. Node Dependencies
5. UI Credential Smoke
6. Create Temporary CI Environment
7. API Validation (8)
8. API Regression (29)
9. Rate-Limit Cooldown (45s)
10. Database Tests (19)
11. Playwright UI Tests (10)
12. Cleanup Verification

## 报告目录

| 文档 | 路径 |
|---|---|
| 最终测试报告 | docs/day5/final-test-report.md |
| Jenkins Build #10 摘要 | docs/day5/jenkins-build-10-summary.md |
| 项目复盘 | docs/day5/project-retrospective.md |
| 面试项目总结 | docs/day5/interview-project-summary.md |
| Jenkins Build #10 原始证据 | evidence/jenkins-build-10/jenkins-original/ |
| └ 控制台日志 | evidence/jenkins-build-10/jenkins-original/console.log |
| └ 原始归档 (HTML/XML/Playwright) | evidence/jenkins-build-10/jenkins-original/archive/ |
| └ SHA-256 校验和 | evidence/jenkins-build-10/jenkins-original/SHA256SUMS.txt |
| 本地等同报告（参考） | evidence/local-equivalent-reports/ |

## 项目亮点

- **三层测试金字塔**：API (37) + 数据库 (19) + UI (10)，66 条唯一用例全部通过
- **12 阶段 Jenkins CI 流水线**：含凭据冒烟、限流冷却、自动清理、零残留确认
- **凭据安全**：Jenkins withCredentials 注入，`set +x` 防日志泄露，Post always 清理
- **429 限流自适应**：45s 冷却 + 指数退避重试 + Retry-After 响应头解析
- **API-DB 交叉断言**：创建→查询→更新→删除全生命周期数据库一致性验证
- **Flaky 识别**：UI-007 区分自动化稳定性 vs 产品缺陷，retry 机制兜底
- **完整排障记录**：10 次 Jenkins 构建的问题、根因和解决方案全部可追溯

## 已知限制

- UI 测试覆盖偏向核心正向流程，边缘路径未覆盖
- API 未做完整 JSON Schema 严格校验
- 无负载/性能测试
- UI-007 存在偶发 flaky（自动化稳定性观察项，当前不修改代码）
- CI Agent 镜像依赖预装环境

## 运行说明

> 以下说明不包含任何敏感信息。真实凭据在 Jenkins 中管理，不在此仓库中。

### 本地运行 API 测试

```bash
# 需要 .env 文件（不提交到仓库）
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/api/ -v
```

### 本地运行数据库测试

```bash
# 需要 Plane PostgreSQL 可访问
pytest tests/db/ -v
```

### 本地运行 UI 测试

```bash
# 需要设置环境变量
export PLANE_UI_EMAIL="<from-jenkins>"
export PLANE_UI_PASSWORD="<from-jenkins>"
export PLANE_BASE_URL="http://192.168.146.132:8090"
export PLANE_WORKSPACE_SLUG="qa-lab"

npm ci
npx playwright install chromium
npx playwright test tests/ui --project=chromium --project=chromium-login
```

### CI 运行

Jenkins Job `plane-qa-pipeline` 配置 Pipeline Script from SCM 或直接粘贴 Jenkinsfile 内容。所有凭据通过 Jenkins Credentials Binding 注入。

## 安全说明

真实环境变量只能写入本地 .env 文件，严禁提交密码、Cookie、API Key、Personal Access Token、数据库凭据或其他敏感信息。请以 .env.example 为变量参考。所有 Jenkins 凭据通过 withCredentials 注入，不在代码或日志中暴露。
