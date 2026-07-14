# Day 1 系统初步分析

> 本文档基于 2026-07-12 在 qa-linux 上实际部署的 Plane v1.3.1 Community Edition 分析。

| 分析项 | 当前记录 | 取证方式 |
| --- | --- | --- |
| 系统定位 | Plane Community Edition v1.3.1 — 开源项目管理平台（Issues/Cycles/Modules/Pages/Views），自托管部署 | 部署记录、docker-compose.yaml、页面标题 |
| 主要业务模块 | Issues（议题）、Cycles（迭代周期）、Modules（模块）、Pages（文档页面）、Views（自定义视图）、Analytics（分析） | 实际页面导航推断，待 Day 2 探索确认 |
| 前端服务 (web) | makeplane/plane-frontend:v1.3.1 — Next.js 前端，端口 80/3000，healthy | Docker Compose、容器状态 |
| Space 服务 (space) | makeplane/plane-space:v1.3.1 — 工作空间前端，端口 3000，healthy | Docker Compose、容器状态 |
| Admin 服务 (admin) | makeplane/plane-admin:v1.3.1 — 管理后台前端，端口 80/3000，healthy | Docker Compose、容器状态 |
| Live 服务 (live) | makeplane/plane-live:v1.3.1 — 实时协作服务，端口 3000 | Docker Compose、容器状态 |
| API 服务 (api) | makeplane/plane-backend:v1.3.1 — Django + Gunicorn + Uvicorn，端口 8000 | Compose、容器日志（gunicorn 启动日志已确认） |
| Worker (worker) | makeplane/plane-backend:v1.3.1 — Celery Worker，端口 8000 | Compose、后台任务队列 |
| Beat Worker (beat-worker) | makeplane/plane-backend:v1.3.1 — Celery Beat 定时任务调度器，端口 8000 | Compose、django-celery-beat 迁移已确认 |
| Migrator (migrator) | makeplane/plane-backend:v1.3.1 — Django 数据库迁移（一次性），已成功退出（ExitCode 0） | Compose、容器日志（django_celery_beat、license、sessions 等迁移已应用） |
| PostgreSQL (plane-db) | postgres:15.7-alpine — 数据库，端口 5432（内部） | Compose、migrator 迁移成功 |
| Redis/Valkey (plane-redis) | valkey/valkey:7.2.11-alpine — 缓存/队列后端，端口 6379（内部） | Compose、API 配置确认 |
| RabbitMQ (plane-mq) | rabbitmq:3.13.6-management-alpine — 消息队列，端口 5672（内部） | Compose、Celery 依赖 |
| 对象存储 (plane-minio) | minio/minio:latest — S3 兼容对象存储，端口 9000（内部），bucket "uploads" 已自动创建 | Compose、API 日志（"Bucket 'uploads' created successfully"） |
| 反向代理 (proxy) | makeplane/plane-proxy:v1.3.1 — Caddy 反向代理，HTTP→80, HTTPS→443，实际端口映射 8090→80, 8443→443 | 端口映射、响应头（Via: 1.1 Caddy） |
| 数据流初步分析 | 用户 → Caddy (:8090) → Web/Space/Admin/Live 前端 → API (Gunicorn :8000) → PostgreSQL/Redis/MinIO；Worker 通过 RabbitMQ 消费异步任务；Beat Worker 通过 django-celery-beat 调度定时任务 | 请求链路推断（基于 Compose 配置 + 容器日志 + 迁移记录），待 Day 2 抓包/接口验证 |
| 后续可测试点 | ① 用户注册/登录流程 ② Workspace/Project CRUD ③ Issue 生命周期（创建→分配→状态流转→关闭） ④ Cycle 和 Module 管理 ⑤ API 接口认证与授权 ⑥ 文件上传（MinIO/S3） ⑦ 实时协作（Live 服务） ⑧ 分析接口权限校验 ⑨ Webhook SSRF 防护 ⑩ 后台任务正确性 | 基于 v1.3.1 release notes 中的安全修复项和系统架构确定 |
| 实际容器与官方架构差异 | 官方 Compose 定义的日志服务（logs_api, logs_worker, logs_beat-worker, logs_migrator）未在运行容器中出现 — 可能是 profile-based 或条件启动，需 Day 2 进一步确认 | 对比 docker-compose.yaml 定义 vs 实际 `docker compose ps -a` 输出 |

## 系统架构（基于实际部署）

```
                         ┌──────────────────────────┐
                         │   Caddy Proxy (:8090)     │
                         │   makeplane/plane-proxy   │
                         └──────┬──────────┬────────┘
                                │          │
              ┌─────────────────┼──────────┼─────────────────┐
              ▼                 ▼          ▼                 ▼
      ┌──────────┐    ┌──────────┐  ┌──────────┐    ┌──────────┐
      │  Web     │    │  Space   │  │  Admin   │    │  Live    │
      │Frontend  │    │ Frontend │  │ Frontend │    │ Frontend │
      └────┬─────┘    └────┬─────┘  └────┬─────┘    └────┬─────┘
           │               │             │               │
           └───────────────┴──────┬──────┴───────────────┘
                                  │
                                  ▼
                      ┌───────────────────┐
                      │   API (Gunicorn)  │
                      │ plane-backend     │
                      │   :8000           │
                      └──┬──────┬─────┬───┘
                         │      │     │
              ┌──────────┼──────┼─────┼──────────┐
              ▼          ▼      ▼     ▼          ▼
        ┌─────────┐ ┌──────┐ ┌──────┐ ┌──────────┐
        │PostgreSQL│ │Valkey│ │MinIO │ │RabbitMQ  │
        │ :5432   │ │:6379 │ │:9000 │ │  :5672   │
        └─────────┘ └──────┘ └──────┘ └────┬─────┘
                                            │
                               ┌────────────┼────────────┐
                               ▼            ▼            │
                        ┌──────────┐ ┌──────────┐        │
                        │ Worker   │ │  Beat    │        │
                        │ (Celery) │ │ (Celery) │        │
                        └──────────┘ └──────────┘        │
                                                          │
                          ┌───────────────────────────────┘
                          │ (一次性)
                          ▼
                    ┌──────────┐
                    │ Migrator │  ExitCode 0
                    │ (Django) │
                    └──────────┘
```

## 分析结论

- ✅ Plane v1.3.1 Community Edition 已成功部署在 qa-linux，12 个服务运行正常。
- ✅ 数据库迁移已全部成功应用（含 django_celery_beat、license、sessions 等）。
- ✅ 反向代理（Caddy）正确将 8090/8443 映射到内部服务。
- ✅ MinIO bucket "uploads" 已自动创建。
- ⚠️ 官方 docker-compose.yaml 定义了 logs_api/logs_worker/logs_beat-worker/logs_migrator 等服务，但实际未启动 — 待 Day 2 分析是否通过 profile 条件启用。
- 📋 Day 2 可基于实际部署开展接口探索、用户注册、Issue CRUD、权限验证等测试。

证据路径：
- evidence/day1/01-environment-baseline.txt
- evidence/day1/02-docker-containers.txt
- evidence/day1/06-health-check.txt
- evidence/day1/07-sanitized-logs.txt
