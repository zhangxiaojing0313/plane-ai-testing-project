# Jenkins Environment Assessment — Day 4 Phase 1

**Date:** 2026-07-13  
**Host:** qa-linux  
**Container:** qa-jenkins  
**Image:** jenkins/jenkins:lts-jdk17  

---

## 1. Current Jenkins Environment

| Item | Value |
|------|-------|
| Container | `qa-jenkins` |
| Image | `jenkins/jenkins:lts-jdk17` |
| Status | Up 12 hours |
| Ports | 8081→8080 (HTTP), 50000 (JNLP) |
| User | `jenkins` |
| Home | `/var/jenkins_home` |
| Disk | 19G used / 59G total (38G free) |

## 2. Installed Tools

| Tool | Status | Version/Notes |
|------|--------|---------------|
| Java | ✅ OpenJDK 17.0.18 Temurin | `JAVA_HOME=/opt/java/openjdk` is set but `/opt/java/openjdk/bin` NOT in PATH. Full path required: `/opt/java/openjdk/bin/java`. This is a **PATH issue, not missing JDK.** |
| Git | ✅ | 2.47.3 |
| Python 3 | ❌ NOT FOUND | |
| pip3 | ❌ NOT FOUND | |
| Node.js | ❌ NOT FOUND | |
| npm | ❌ NOT FOUND | |
| Docker CLI | ❌ NOT FOUND | |
| curl | ✅ | Available |
| wget | Likely available | Standard in Jenkins image |

**Note (updated Phase 2):** Java IS installed at `/opt/java/openjdk/bin/java` (OpenJDK 17.0.18 Temurin). The `jenkins` user's PATH (`/usr/local/bin:/usr/bin:/bin`) does NOT include the JDK bin directory. Shell scripts must use `$JAVA_HOME/bin/java` or the full path. The Jenkins process itself runs Java via `-jar /usr/share/jenkins/jenkins.war` without needing the `java` CLI on PATH.

## 3. Network Access

| Target | Result |
|--------|--------|
| Plane (http://192.168.146.132:8090) | ✅ 200 OK |
| GitHub (https://github.com) | ✅ 200 OK |
| qa-linux host | Via Docker network |

## 4. Volumes & Workspace

- **Workspace:** `/var/jenkins_home/workspace/` exists, writable
- **Existing jobs:** `env-smoke-check`, `pipeline-smoke-check`
- **Docker socket:** NOT mounted (`/var/run/docker.sock` does not exist)
- **No Docker-in-Docker capability**

## 5. Docker Capability

- Docker CLI: NOT installed
- Docker socket: NOT accessible
- **Jenkins CANNOT build/run Docker containers directly**
- **Jenkins CANNOT execute `docker exec` to access Plane DB**

## 6. Architecture Comparison

### A. Jenkins Controller Container Direct Execution

| Dimension | Assessment |
|-----------|------------|
| Security | ⚠️ LOW — modifies controller, risks pipeline state |
| Complexity | MEDIUM — need to install Python, Node, Playwright in controller |
| Python/Node/Playwright | ❌ NOT available — would need full install |
| Docker/DB access | ❌ No Docker socket |
| Impact on Jenkins | HIGH — packages, disk usage, potential conflicts |
| Interview value | LOW — pollutes controller |

### B. qa-linux Host as Jenkins Agent

| Dimension | Assessment |
|-----------|------------|
| Security | ⚠️ MEDIUM — agent has host access |
| Complexity | HIGH — requires SSH/JNLP agent setup, user management |
| Python/Node/Playwright | ✅ Already available on host |
| Docker/DB access | ✅ Full access |
| Impact on Jenkins | MEDIUM — adds agent configuration |
| Interview value | MEDIUM — shows agent architecture |

### C. Independent QA Runner Container (Recommended)

| Dimension | Assessment |
|-----------|------------|
| Security | ✅ HIGH — isolated container, no shared state |
| Complexity | LOW — single Dockerfile, standard image |
| Python/Node/Playwright | ✅ Install in dedicated image |
| Docker/DB access | ✅ Via docker exec and host network |
| Impact on Jenkins | ✅ NONE — Jenkins only triggers |
| Interview value | ✅ HIGH — clean CI/CD architecture, reusable |

## 7. Recommended Architecture: Option C — Independent QA Runner

**Rationale:**
1. Jenkins controller is a bare `jenkins/jenkins:lts-jdk17` without Python, Node, Docker
2. Installing tools into controller pollutes it and risks instability
3. No Docker socket access from Jenkins (Docker-out-of-Docker not available)
4. Independent runner container keeps test dependencies isolated
5. QA Runner can be rebuilt from Dockerfile, ensuring reproducibility

**Proposed flow:**
```
Jenkins (trigger only)
  → SSH or docker exec on qa-linux host
    → QA Runner container
      → pytest tests/api
      → npx playwright test tests/ui
      → pytest tests/db
      → Collect reports → Archive
```

## 8. Day 4 Phase 2 Implementation Steps

1. Create `Dockerfile.qa-runner` with Python 3.12+, Node 22+, Playwright, pytest, requests
2. Build image: `docker build -f Dockerfile.qa-runner -t qa-runner:latest .`
3. Create Jenkins Pipeline (Jenkinsfile) that:
   - Checks out project (or mounts volume)
   - Runs API tests (`pytest tests/api -v`)
   - Runs UI tests (`npx playwright test tests/ui`)
   - Runs DB tests (`pytest tests/db -v`)
   - Archives HTML reports and evidence
4. Configure Jenkins job to trigger QA Runner container
5. Add quality gate thresholds (pass rate, no regressions)

## 9. Risks & Rollback

| Risk | Mitigation |
|------|------------|
| QA Runner image build fails | Pre-build and test manually |
| Docker exec from runner to Plane DB | Test connectivity first |
| Playwright browser deps missing | Include in Dockerfile |
| Jenkins job can't trigger host commands | Use SSH key or Docker API |
| Disk space | Clean up old runner containers |

**Rollback:** QA Runner is independent — stop container, no Jenkins or Plane impact.

---

## 10. Current Readiness Score

| Capability | Ready? |
|------------|--------|
| Plane API accessible | ✅ |
| Plane DB accessible (from host) | ✅ |
| Playwright on host | ✅ |
| pytest on host | ✅ |
| Jenkins triggers possible | ⚠️ Phase 2 |
| QA Runner container | ⚠️ Phase 2 |
| CI Pipeline | ⚠️ Phase 2 |
