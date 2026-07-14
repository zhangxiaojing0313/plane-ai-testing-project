/**
 * Jenkinsfile - Plane AI Testing Project CI Pipeline
 *
 * Agent: plane-qa-runner (Docker-based Jenkins inbound agent)
 * Mode:  Local Source (read-only mount from /opt/plane-source)
 *        Day 5 will switch to checkout scm from GitHub.
 *
 * Credentials required (defined in Jenkins, NEVER here):
 *   - plane-api-key              : Plane API key
 *   - plane-ui-email-v2          : Plane UI login email
 *   - plane-ui-password-v2       : Plane UI login password
 *
 * All credentials are injected via environment at runtime.
 * The temporary .env file is created in post, used during build,
 * and deleted in post always. It is never archived or printed.
 */
pipeline {
    agent { label 'plane-qa-runner' }

    environment {
        // Non-sensitive env - safe to hardcode
        PLANE_BASE_URL        = 'http://host.docker.internal:8090'
        PLANE_API_BASE_URL    = 'http://host.docker.internal:8090/api/v1'
        PLANE_WORKSPACE_SLUG  = 'qa-lab'
        PLANE_PROJECT_ID      = '0c1cf73f-2d88-430b-812b-2e1c7f010c3c'

        // Agent paths
        QA_VENV               = '/home/jenkins/qa-venv'
        SOURCE_DIR            = '/opt/plane-source'
        PLAYWRIGHT_WORKERS     = '1'
    }

    stages {

        // ================================================================
        stage('1. Checkout / Sync Source') {
            steps {
                script {
                    // Local source mode: copy from read-only mount to workspace
                    sh '''
                        echo "Syncing source from ${SOURCE_DIR} to workspace..."
                        rsync -a --info=stats2 --exclude='.env' --exclude='.venv' \
                            --exclude='node_modules' --exclude='.playwright' \
                            --exclude='reports' --exclude='evidence' \
                            --exclude='test-results' --exclude='playwright-report' \
                            --exclude='__pycache__' --exclude='.pytest_cache' \
                            --exclude='*.pyc' --exclude='.git' \
                            "${SOURCE_DIR}/" "${WORKSPACE}/"
                        echo "Source synced to ${WORKSPACE}"
                    '''
                }
            }
        }

        // ================================================================
        stage('2. Environment Preflight') {
            steps {
                sh '''
                    echo "=== Preflight ==="
                    echo "Host: $(hostname)"
                    echo "User: $(whoami)"
                    echo "Workspace: ${WORKSPACE}"
                    echo "Java: $(java -version 2>&1 | head -1)"
                    echo "Git: $(git --version)"
                    echo "Python: $(${QA_VENV}/bin/python3 --version)"
                    echo "Node: $(node --version)"
                    echo "Docker: $(docker --version)"
                    echo "Plane reachable: $(curl -sI --max-time 10 ${PLANE_BASE_URL} | head -1)"
                '''
            }
        }

        // ================================================================
        stage('3. Python Environment') {
            steps {
                sh '''
                    echo "Setting up Python venv..."
                    rsync -a --info=stats2 --exclude='.git' --exclude='__pycache__' "${QA_VENV}/" "${WORKSPACE}/.venv-ci/"
                    ${WORKSPACE}/.venv-ci/bin/pip install -r requirements.txt --quiet
                '''
            }
        }

        // ================================================================
        stage('4. Node Dependencies') {
            steps {
                sh '''
                    echo "Installing Node dependencies..."
                    npm ci --ignore-scripts
                    npx playwright install chromium
                '''
            }
        }

        // ================================================================
        stage('5. UI Credential Smoke') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'plane-ui-email-v2',
                        variable: 'PLANE_UI_EMAIL'
                    ),
                    string(
                        credentialsId: 'plane-ui-password-v2',
                        variable: 'PLANE_UI_PASSWORD'
                    )
                ]) {
                    sh '''
                        set +x

                        export PLANE_BASE_URL="http://192.168.146.132:8090"
                        export PLANE_WORKSPACE_SLUG="qa-lab"

                        python3 - <<'PY'
import os
import sys

email = os.environ.get("PLANE_UI_EMAIL", "")
password = os.environ.get("PLANE_UI_PASSWORD", "")

errors = []

if email != "admin@test.local":
    errors.append(
        "UI email credential does not exactly match the expected account"
    )

if not password:
    errors.append("UI password credential is empty")

if password != password.strip():
    errors.append(
        "UI password credential contains leading or trailing whitespace"
    )

if "\\r" in password or "\\n" in password:
    errors.append("UI password credential contains CR or LF characters")

if errors:
    for error in errors:
        print(f"Credential validation failed: {error}")
    sys.exit(1)

print("UI credential format validation passed")
PY

                        npx playwright test \
                          tests/ui/auth.setup.ts \
                          --project=setup \
                          --workers=1 \
                          --reporter=list

                        rm -f .playwright/auth-state.json

                        echo "UI credential smoke passed"
                    '''
                }
            }
        }

        // ================================================================
        stage('6. Create Temporary CI Environment') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'plane-api-key',
                        variable: 'CI_PLANE_API_KEY'
                    )
                ]) {
                    sh '''
                        set +x
                        umask 077

                        cat > .env <<EOF
PLANE_BASE_URL=${PLANE_BASE_URL}
PLANE_API_BASE_URL=${PLANE_API_BASE_URL}
PLANE_API_KEY=${CI_PLANE_API_KEY}
PLANE_WORKSPACE_SLUG=${PLANE_WORKSPACE_SLUG}
PLANE_PROJECT_ID=${PLANE_PROJECT_ID}
EOF

                        chmod 600 .env

                        test -s .env
                        grep -q '^PLANE_API_KEY=.' .env

                        echo ".env created with $(wc -l < .env) lines"
                        echo "Required CI variables are present"
                    '''
                }
            }
        }

        // ================================================================
        stage('7. API Validation') {
            steps {
                sh '''
                    ${WORKSPACE}/.venv-ci/bin/pytest tests/api/test_validation.py \
                        -v \
                        --junitxml=reports/junit-api-validation.xml \
                        --html=reports/api-validation.html --self-contained-html
                '''
            }
        }

        // ================================================================
        stage('8. API Regression') {
            steps {
                sh '''
                    ${WORKSPACE}/.venv-ci/bin/pytest tests/api \
                        --ignore=tests/api/test_validation.py \
                        -v \
                        --junitxml=reports/junit-api-regression.xml \
                        --html=reports/api-regression.html --self-contained-html
                '''
            }
        }

        // ================================================================
        stage('9. Rate-Limit Cooldown') {
            steps {
                sh '''
                    echo "Waiting for Plane API rate-limit cooldown..."
                    sleep 45
                '''
            }
        }

        // ================================================================
        stage('10. Database Tests') {
            steps {
                sh '''
                    ${WORKSPACE}/.venv-ci/bin/pytest tests/db \
                        -v \
                        --junitxml=reports/junit-db.xml \
                        --html=reports/db-full.html --self-contained-html
                '''
            }
        }

        // ================================================================
        stage('11. Playwright UI Tests') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'plane-ui-email-v2',
                        variable: 'PLANE_UI_EMAIL'
                    ),
                    string(
                        credentialsId: 'plane-ui-password-v2',
                        variable: 'PLANE_UI_PASSWORD'
                    )
                ]) {
                    sh '''
                        set +x

                        export PLANE_BASE_URL="http://192.168.146.132:8090"
                        export PLANE_WORKSPACE_SLUG="qa-lab"

                        test -n "$PLANE_UI_EMAIL"
                        test -n "$PLANE_UI_PASSWORD"
                        echo "UI credentials injected"

                        npx playwright test tests/ui \
                            --project=chromium \
                            --project=chromium-login \
                            --workers=1 \
                            --reporter=list,html,junit
                        # Move playwright outputs
                        mkdir -p reports/
                        cp playwright-report/results.xml reports/junit-ui.xml 2>/dev/null || true
                        cp -r playwright-report reports/playwright-report 2>/dev/null || true
                    '''
                }
            }
        }

        // ================================================================
        stage('12. Cleanup Verification') {
            steps {
                sh '''
                    echo "=== Cleanup Check ==="
                    ${WORKSPACE}/.venv-ci/bin/python -c "
import requests, os, sys, time
from dotenv import load_dotenv
load_dotenv()
base = os.getenv('PLANE_BASE_URL')
ws = os.getenv('PLANE_WORKSPACE_SLUG')
pid = os.getenv('PLANE_PROJECT_ID')
api_key = os.getenv('PLANE_API_KEY')
hdrs = {'X-API-Key': api_key}
url = f'{base}/api/v1/workspaces/{ws}/projects/{pid}/issues/'

def _retry_request(method, req_url, max_retries=5):
    backoffs = [2, 4, 8, 16, 32]
    for attempt in range(max_retries + 1):
        resp = requests.request(method, req_url, headers=hdrs, timeout=15)
        if resp.status_code != 429:
            return resp
        if attempt >= max_retries:
            return resp
        retry_after = resp.headers.get('Retry-After')
        if retry_after is not None:
            try:
                wait = int(retry_after)
            except (ValueError, TypeError):
                wait = backoffs[attempt]
        else:
            wait = backoffs[attempt]
        print(f'429 retry: attempt={attempt+1}, status=429, wait={wait}s')
        time.sleep(wait)
    return resp

resp = _retry_request('GET', url)
data = resp.json()
issues = data.get('results', data) if isinstance(data, dict) else data
auto = [i for i in (issues if isinstance(issues, list) else []) if 'AUTO-D' in str(i.get('name',''))]
print(f'Total issues: {len(issues) if isinstance(issues, list) else \"N/A\"}')
print(f'AUTO-D residue: {len(auto)}')
for i in auto:
    print(f'  LEFTOVER: {i[\"name\"]}')
    del_url = f'{url}{i[\"id\"]}/'
    dr = _retry_request('DELETE', del_url)
    print(f'  Delete attempt: {dr.status_code}')
# Re-fetch to confirm cleanup
time.sleep(1)
resp2 = _retry_request('GET', url)
data2 = resp2.json()
issues2 = data2.get('results', data2) if isinstance(data2, dict) else data2
auto2 = [i for i in (issues2 if isinstance(issues2, list) else []) if 'AUTO-D' in str(i.get('name',''))]
assert len(auto2) == 0, f'Leftover AUTO-D items: {len(auto2)}'
print('Cleanup: PASS')
"
                '''
            }
        }
    }

    // ====================================================================
    post {
        always {
            script {
                sh '''
                    echo "=== POST: Publish Reports ==="
                    mkdir -p archive/reports archive/evidence
                    cp -r reports/*.html archive/reports/ 2>/dev/null || true
                    cp -r reports/*.xml archive/reports/ 2>/dev/null || true
                    cp -r evidence archive/ 2>/dev/null || true
                    cp -r playwright-report archive/reports/ 2>/dev/null || true
                    echo "Reports staged for archival"
                '''
            }
            junit testResults: 'reports/junit-*.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'archive/**/*', fingerprint: true, allowEmptyArchive: true
            script {
                sh '''
                    echo "=== POST: Cleanup ==="
                    # Remove temporary .env
                    rm -f "${WORKSPACE}/.env" 2>/dev/null || true
                    # Remove auth state
                    rm -f "${WORKSPACE}/.playwright/auth-state.json" 2>/dev/null || true
                    # Remove CI venv
                    rm -rf "${WORKSPACE}/.venv-ci" 2>/dev/null || true
                    echo "Post-cleanup complete"
                '''
            }
        }
        failure {
            echo 'Pipeline FAILED - check reports and evidence for details.'
        }
        success {
            echo 'Pipeline PASSED - all tests green, zero residue.'
        }
    }
}
