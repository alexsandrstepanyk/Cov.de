#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y ca-certificates curl git

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

systemctl enable --now docker

if id ubuntu >/dev/null 2>&1; then
  usermod -aG docker ubuntu || true
fi

mkdir -p /opt/govde
mkdir -p /opt/govde/storage/pdf_letters
mkdir -p /opt/govde/logs

echo "Bootstrap complete. Clone the repo into /opt/govde and continue with docker compose."

