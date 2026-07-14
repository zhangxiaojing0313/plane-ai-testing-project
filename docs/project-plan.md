# Plane AI Testing Project 五天计划

## 项目边界

被测系统为 Plane Community Edition。本计划以 Linux 测试主机 qa-linux 为目标环境，计划测试项目路径为 /home/tester/qa-workspace/plane-ai-testing-project，Plane 计划部署目录为 /home/tester/qa-workspace/plane-selfhost。以上为项目目标信息，实际状态必须通过执行记录确认。

## Day 1：项目初始化、部署、环境基线、系统分析

- 初始化项目结构、Python 与 Playwright 配置、环境变量示例和安全忽略规则。
- 在获授权的 Linux 主机上采集环境基线，并归档真实命令输出。
- 部署 Plane 或记录实际部署过程、版本、容器状态和访问结果。
- 根据实际容器、页面和接口信息完成系统初步分析。

## Day 2：需求分析、测试用例设计、API 探索

- 梳理真实业务流程、角色与验收条件。
- 设计可追溯的功能、边界、异常与权限测试用例。
- 探索实际 API、认证方式、请求参数与响应规则，并记录证据。

## Day 3：接口自动化、Playwright 核心流程、权限测试

- 实现基于 pytest 与 requests 的核心 API 自动化。
- 实现基于 Playwright 与 TypeScript 的核心 UI 流程。
- 覆盖实际角色权限和越权风险场景；测试数据与账号必须隔离。

## Day 4：数据库断言、异常测试、Jenkins Pipeline

- 使用 PostgreSQL 只读或经授权的验证方式检查关键数据结果。
- 补充异常、错误处理与数据一致性场景。
- 建立 Jenkins Pipeline，保存报告、日志与失败证据。

## Day 5：回归、缺陷报告、测试报告、GitHub 和面试包装

- 执行经确认范围的回归并如实记录结果。
- 输出可复现的缺陷报告、测试报告与证据索引。
- 完成敏感信息扫描、GitHub 项目整理和面试材料提炼。

## 当前状态

Day 1 初始化进行中。本计划不代表任何部署、测试或验收已经完成。
