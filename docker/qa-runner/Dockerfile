# QA Runner Agent for Plane AI Testing Project
#
# Purpose: Dedicated Jenkins inbound agent for running Plane test suites.
# Base:     jenkins/inbound-agent:jdk17 (official Jenkins agent with JDK 17)
# Security: Non-root user, no credentials baked in, .env never copied.
#
# Build:
#   docker build -t plane-qa-runner:day4 -f docker/qa-runner/Dockerfile .
#
FROM jenkins/inbound-agent:jdk17

USER root

# ── System dependencies ──────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    bash \
    rsync \
    ca-certificates \
    python3 \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# ── Node.js 22.x (from NodeSource) ───────────────────────────────
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ── Docker CLI (standalone, no daemon) ───────────────────────────
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.3.1.tgz \
    | tar -xz -C /usr/local/bin --strip-components=1 docker/docker \
    && chmod +x /usr/local/bin/docker

# ── Playwright Chromium system dependencies ──────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0t64 \
    libatk-bridge2.0-0t64 \
    libcups2t64 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2t64 \
    libatspi2.0-0t64 \
    fonts-liberation \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# ── Switch back to Jenkins agent user ────────────────────────────
USER jenkins

# ── Python virtual environment (pre-created for tests) ───────────
ENV QA_VENV=/home/jenkins/qa-venv
RUN python3 -m venv $QA_VENV

# ── Install Python test dependencies ─────────────────────────────
COPY --chown=jenkins:jenkins requirements.txt /tmp/requirements.txt
RUN $QA_VENV/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# ── Install Node test dependencies ───────────────────────────────
COPY --chown=jenkins:jenkins package.json package-lock.json /tmp/npm-deps/
WORKDIR /tmp/npm-deps
RUN npm install --ignore-scripts

# ── Install Playwright Chromium ──────────────────────────────────
RUN npx playwright install chromium

# ── Verify installations ─────────────────────────────────────────
RUN echo "=== Java ===" && java -version 2>&1 \
    && echo "=== Git ===" && git --version \
    && echo "=== Python ===" && $QA_VENV/bin/python3 --version \
    && echo "=== pip ===" && $QA_VENV/bin/pip --version \
    && echo "=== Node ===" && node --version \
    && echo "=== npm ===" && npm --version \
    && echo "=== Docker CLI ===" && docker --version \
    && echo "=== Playwright ===" && npx playwright --version

# ── Cleanup temp files ───────────────────────────────────────────
RUN rm -rf /tmp/npm-deps /tmp/requirements.txt

WORKDIR /home/jenkins
