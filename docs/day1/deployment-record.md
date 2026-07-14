# Day 1 Plane 部署记录

> 本文档基于 2026-07-12 在 qa-linux 上的实际部署操作记录。

| 项目 | 记录 |
| --- | --- |
| 部署目录 | /home/tester/qa-workspace/plane-selfhost |
| Plane 版本 | v1.3.1 (Stable, Community Edition) |
| 安装来源 | https://github.com/makeplane/plane/releases/tag/v1.3.1 |
| 安装方式 | 官方 setup.sh 脚本 + 手动下载 docker-compose.yaml 和 variables.env（因代理阻断脚本自动下载） |
| 安装脚本 SHA-256 | 466b2e0d6137f72b577e10bd8af20a1f5c11268fc1294445fed7571c99d40031 |
| CPU 架构 | amd64 (x86_64) |
| Compose 文件位置 | /home/tester/qa-workspace/plane-selfhost/plane-app/docker-compose.yaml |
| 环境变量文件 | /home/tester/qa-workspace/plane-selfhost/plane-app/plane.env |
| 关键配置项 | LISTEN_HTTP_PORT=8090, LISTEN_HTTPS_PORT=8443, WEB_URL=http://192.168.146.132:8090, CORS_ALLOWED_ORIGINS=http://192.168.146.132:8090 |
| 页面访问地址 | http://192.168.146.132:8090 |
| 健康检查结果 | ✅ HTTP 200 OK — 通过 |

## 容器列表

| 容器名称 | 镜像 | 状态 |
| --- | --- | --- |
| plane-app-proxy-1 | makeplane/plane-proxy:v1.3.1 | Up (0.0.0.0:8090->80, 0.0.0.0:8443->443) |
| plane-app-web-1 | makeplane/plane-frontend:v1.3.1 | Up (healthy) |
| plane-app-space-1 | makeplane/plane-space:v1.3.1 | Up (healthy) |
| plane-app-admin-1 | makeplane/plane-admin:v1.3.1 | Up (healthy) |
| plane-app-live-1 | makeplane/plane-live:v1.3.1 | Up |
| plane-app-api-1 | makeplane/plane-backend:v1.3.1 | Up |
| plane-app-worker-1 | makeplane/plane-backend:v1.3.1 | Up |
| plane-app-beat-worker-1 | makeplane/plane-backend:v1.3.1 | Up |
| plane-app-migrator-1 | makeplane/plane-backend:v1.3.1 | Exited (0) — 迁移成功 |
| plane-app-plane-db-1 | postgres:15.7-alpine | Up |
| plane-app-plane-redis-1 | valkey/valkey:7.2.11-alpine | Up |
| plane-app-plane-mq-1 | rabbitmq:3.13.6-management-alpine | Up |
| plane-app-plane-minio-1 | minio/minio:latest | Up |

**容器状态**：12 个运行中，1 个已退出（migrator，退出码 0，迁移完成）。无重启循环，无 unhealthy 状态。

## 异常与处理记录

### 异常 1：setup.sh checkLatestRelease 因代理 TLS 错误失败

- **原始错误**：`curl: (35) TLS connect error: error:0A000126:SSL routines::unexpected eof while reading`
- **根因**：主机 HTTPS_PROXY (http://192.168.146.1:7897) 阻断了 GitHub API 和 releases 的 HTTPS 连接。且 checkLatestRelease 在 subshell `$()` 中执行，`exit 1` 仅退出 subshell 导致 APP_RELEASE 为空，后续 download 构造出错误的 `//docker-compose.yml` URL。
- **处理**：使用 `curl --noproxy '*'` 手动下载 docker-compose.yaml 和 variables.env（v1.3.1），手动设置 APP_RELEASE=v1.3.1。

### 异常 2：setup.sh 启动时重新读取 APP_RELEASE

- **处理**：在 plane.env 中预先写入 APP_RELEASE=v1.3.1，避免脚本回退到 "stable" 标签。

## 健康检查详情

- `curl -I http://127.0.0.1:8090` → HTTP 200 OK
- `curl -I http://192.168.146.132:8090` → HTTP 200 OK
- `health-check.sh` 输出 → PASS（无 unhealthy/restarting 容器）
- 反向代理：Caddy → Nginx，响应头正常

## 敏感信息脱敏说明

- 真实 .env、数据库密码、密钥、Cookie、Token 和私有镜像凭据不得写入本文档。
- 命令输出如出现敏感值，应使用 [REDACTED] 替换后再归档。
- 记录配置时仅保留变量名、服务角色、端口和非敏感状态信息。
