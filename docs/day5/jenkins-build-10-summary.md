# Jenkins Build #10 摘要

## 构建信息

| 属性 | 值 |
|---|---|
| Job | plane-qa-pipeline |
| Build | #10 |
| Agent | plane-qa-runner-v2 |
| 结果 | **SUCCESS** |
| 最终输出 | Pipeline PASSED - all tests green, zero residue. |
| Finished | SUCCESS |

---

## 全部构建历程

本 Job 从创建到 Build #10 最终成功，共经历 10 次构建。以下按问题类别记录每次失败的原因和解决方案。

### Build #1 — Pipeline Script 配置错误

| 属性 | 内容 |
|---|---|
| 问题类别 | **CI 配置问题** |
| 现象 | Pipeline 启动后立即失败 |
| 根因 | Jenkins Job 配置中 Pipeline Script 仅填写了 Jenkinsfile 文件名，未粘贴完整 Pipeline 脚本内容 |
| 解决 | 将完整 Jenkinsfile 内容粘贴到 Pipeline Script 文本框 |

### Build #2 — 凭据注入失败

| 属性 | 内容 |
|---|---|
| 问题类别 | **凭据管理问题** |
| 现象 | 测试执行时环境变量 PLANE_UI_EMAIL / PLANE_UI_PASSWORD 为空 |
| 根因 | Jenkins withCredentials 绑定未正确配置；Credential ID 与绑定变量之间的映射错误 |
| 解决 | 检查和修正 Jenkins Job 配置中的 Credentials Binding |

### Build #3 — API 限流与数据残留

| 属性 | 内容 |
|---|---|
| 问题类别 | **测试环境问题** |
| 现象 | API 连续调用触发 429 Too Many Requests；历史 AUTO-D 测试数据残留导致断言失败 |
| 根因 | (1) Plane API 存在速率限制，连续请求未留冷却间隔；(2) 先前测试创建的 AUTO-D 数据未清理 |
| 解决 | (1) 在 API 阶段后增加 45s 冷却 + 429 指数退避重试逻辑；(2) 在 Cleanup Verification 阶段增加 AUTO-D 自动清理 |

### Build #4～#8 — UI 凭据不一致

| 属性 | 内容 |
|---|---|
| 问题类别 | **凭据管理问题** |
| 现象 | UI 登录测试返回 "Plane login rejected: returned to email step"，手动输入凭据则通过 |
| 根因 | Jenkins 凭据记录中存储的内容与实际 Plane 账号密码不一致（可能包含多余空格、换行符或错误的账号） |
| 定位过程 | (1) 在 Agent 容器内手动执行 `npx playwright test tests/ui/auth.setup.ts --project=setup` → 1 passed，确认 Playwright 和页面对象正常；(2) Jenkins withCredentials 注入后同一测试失败，确认问题在凭据层；(3) 在 Jenkins 中新建 `plane-ui-email-v2` 和 `plane-ui-password-v2`，手动验证后绑定 |
| 解决 | 新建 Jenkins Credentials `plane-ui-email-v2` / `plane-ui-password-v2`，更新 Jenkinsfile 中所有 withCredentials 引用 |

### Build #9 — API ReadTimeout

| 属性 | 内容 |
|---|---|
| 问题类别 | **测试环境问题** |
| 现象 | 单次 API 调用触发 ReadTimeout |
| 根因 | 网络短暂抖动，Plane 服务响应超时 |
| 解决 | 重试机制自动恢复，未修改代码 |

### Build #10 — 完整成功

| 属性 | 内容 |
|---|---|
| 问题类别 | — |
| 现象 | 全部 12 阶段通过 |
| 结果 | **SUCCESS** — all tests green, zero residue |

---

## 问题统计

| 类别 | 次数 | Build |
|---|---|---|
| CI 配置问题 | 1 | #1 |
| 凭据管理问题 | 6 | #2, #4–#8 |
| 测试环境问题 | 2 | #3, #9 |
| 自动化稳定性问题 | 0 | — |
| 产品缺陷 | 0 | — |

---

## Flaky 用例

| 编号 | 描述 | 现象 | 分类 | 处置 |
|---|---|---|---|---|
| UI-007 | Modify created work item and verify persistence | 首次执行超时未找到修改后的工作项；retry #1 通过 | 自动化稳定性观察项 | 当前不修改代码；后续优化等待条件 |

---

## 构建产出

| 产物 | 状态 |
|---|---|
| JUnit XML (API Validation) | ✅ |
| JUnit XML (API Regression) | ✅ |
| JUnit XML (Database) | ✅ |
| JUnit XML (Playwright UI) | ⚠️ 未在原始归档中找到 |
| HTML Reports (API/DB) | ✅ |
| Playwright HTML Report | ✅ |
| 归档 artifacts | ✅ |
| AUTO-D residue | 0 |

### 证据来源

| 证据 | 来源 | 路径 |
|---|---|---|
| 控制台日志 | Jenkins 控制器 qa-jenkins Build #10 log | evidence/jenkins-build-10/jenkins-original/console.log |
| 原始归档 | Jenkins Build #10 archive/ | evidence/jenkins-build-10/jenkins-original/archive/ |
| 本地等同报告 | 本地 pytest/Playwright 运行（仅供参考） | evidence/local-equivalent-reports/ |

> Jenkins Build #10 原始产物通过 `docker cp` 从 qa-jenkins 容器的 `/var/jenkins_home/jobs/plane-qa-pipeline/builds/10/` 提取。原始归档中未发现 `junit-ui.xml`（Playwright UI 的 JUnit 报告可能因 `cp` 路径问题未进入 `archiveArtifacts`）。

---

## 测试统计汇总

| 层级 | 唯一用例 | 通过 | 失败 |
|---|---|---|---|
| API Validation | 8 | 8 | 0 |
| API Regression | 29 | 29 | 0 |
| **API 唯一合计** | **37** | **37** | **0** |
| **Database** | **19** | **19** | **0** |
| **Playwright UI** | **10** | **10** | **0** |
| **唯一业务测试总数** | **66** | **66** | **0** |

> UI Credential Smoke (1) 为 CI 前置校验，不计入唯一业务用例。

---

## 关键学习

1. **凭据是 CI 中最隐蔽的故障点** — 手动测试通过但 Jenkins 失败时，优先检查凭据内容的精确一致性。
2. **API 限流需要主动设计** — 冷却间隔和指数退避是 API 测试流水线的必要组件，不能依赖"碰运气"。
3. **数据清理是 CI 流水线的必要阶段** — 遗留测试数据会污染下次运行，post + always 清理机制不可省略。
4. **Flaky 不等于缺陷** — UI-007 的一次超时是自动化稳定性问题，需要观察频率和模式后再决定是否优化。
