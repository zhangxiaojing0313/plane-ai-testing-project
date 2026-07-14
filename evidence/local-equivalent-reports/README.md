# Local Equivalent Reports

## 说明

本目录中的报告文件由**本地等同测试套件**生成，覆盖与 Jenkins Build #10 相同的测试范围。

## 来源

- 运行环境：qa-linux (tester)
- 测试套件：pytest API/DB 测试 + Playwright UI 测试
- 生成时间：2026-07-13 (Day 4)

## 文件

| 文件 | 对应测试 | 说明 |
|---|---|---|
| api-validation.html | API Validation (8 条) | 本地 pytest 运行 |
| api-regression.html | API Regression (29 条) | 本地 pytest 运行 |
| db-full.html | Database Tests (19 条) | 本地 pytest 运行 |
| playwright-index.html | Playwright UI Tests (10 条) | 本地 npx playwright test 运行 |

## 重要声明

⚠️ **这些报告不属于 Jenkins Build #10 原始归档。**

- Jenkins Build #10 原始证据位于：`evidence/jenkins-build-10/jenkins-original/`
  - 控制台日志：`evidence/jenkins-build-10/jenkins-original/console.log`
  - 原始归档：`evidence/jenkins-build-10/jenkins-original/archive/`

- 本地等同报告仅作为补充参考。任何涉及 Build #10 的结论均应基于 `jenkins-original/` 中的原始产物。
- 若 Jenkins 原始归档中缺少某类报告，此处文件可作为同类测试运行参考，但不得标注为 Build #10 原始产物。
