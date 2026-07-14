# Day 1 环境基线

> 所有字段均以 qa-linux 主机上的实际命令输出为准。采集时间：2026-07-12T12:00+00:00。

| 项目 | 实际值 | 证据/备注 |
| --- | --- | --- |
| 日期 | 2026-07-12T12:00+00:00 | 时区 UTC |
| 主机名 | qa-linux | `hostname` |
| Linux 用户 | tester | `whoami` |
| 当前工作目录 | /home/tester/qa-workspace/plane-ai-testing-project | `pwd` |
| 操作系统 | Ubuntu 26.04 LTS | `/etc/os-release` |
| CPU | 12th Gen Intel Core i5-12500H (x86_64), 2 cores | `lscpu`，VMware 虚拟化 |
| 内存 | 总量 7.2 GiB，可用约 5.3 GiB | `free -h` |
| 磁盘 | /dev/sda2 59 GB，已用 14 GB (25%)，可用 43 GB | `df -h /` |
| Docker 版本 | 29.1.3 | `docker --version` |
| Docker Compose 版本 | 2.40.3+ds1-0ubuntu1 | `docker compose version` |
| Node.js 版本 | v22.22.1 | 用于 Playwright 工具链 |
| Python 版本 | 3.14.4 | 用于 pytest 工具链 |
| Git 版本 | 2.53.0 | 用于版本管理 |
| 主机 IP | 192.168.146.132 | `hostname -I`，内部网络 |
| 已占用端口 | 22 (SSH), 53 (systemd-resolved), 3306 (qa-mysql), 6379 (qa-redis), 8080 (qa-nginx), 8081 (qa-jenkins), 8082 (qa-filebrowser), 50000 (qa-jenkins) | `ss -lntp` + `docker ps` |
| Plane 使用端口 | HTTP: 8090, HTTPS: 8443 | 配置于 plane.env，已通过健康检查 |

## 环境检查结论

- ✅ 所有关键端口已确认：8090 和 8443 在部署前空闲，部署后由 Plane proxy 占用。
- ✅ 现有服务（Nginx/Jenkins/FileBrowser/MySQL/Redis）未被修改或停止。
- ✅ 磁盘可用 43 GB (> 20 GB 阈值)，内存可用 5.3 GiB (> 4 GB 阈值)。
- ✅ Docker 29.1.3 + Compose 2.40.3 正常工作，无权限异常。
- ✅ 项目脚本 collect-env.sh 和 health-check.sh 语法通过，可执行。
- ⚠️ 主机配置了 HTTPS_PROXY=http://192.168.146.1:7897，该代理阻断了 GitHub releases 下载，需使用 `--noproxy '*'` 绕过。

证据位置：
- evidence/day1/01-environment-baseline.txt — 完整环境采集输出
- evidence/day1/02-docker-containers.txt — 容器状态记录
