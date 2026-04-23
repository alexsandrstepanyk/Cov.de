# Oracle Cloud Deploy

This project runs best on Oracle Cloud as a small Ubuntu VM with Docker and `docker compose`.

## Why this setup

- Oracle Cloud Always Free can keep a small VM running continuously.
- This bot uses Telegram polling, so it does not need a public HTTP port.
- Persisted bot state should live on the VM filesystem, not inside the container.

## Recommended Oracle setup

- Image: `Canonical Ubuntu 22.04` or newer
- Shape: `VM.Standard.A1.Flex` if available in your home region
- Public subnet: enabled
- Public IP: ephemeral is fine, reserved IP is optional if you want a stable address
- Ingress rule: allow `TCP 22` from your IP for SSH

You do not need to open `80`, `443`, or `5000` for the Telegram polling bot.

## Create the VM

1. In OCI, create a compute instance.
2. Upload your SSH public key during creation.
3. Wait until the instance is `Running`.
4. Connect with SSH:

```bash
ssh -i ~/.ssh/<your_private_key> ubuntu@<your_public_ip>
```

Oracle notes that Linux instances use SSH keys, and that the key must be provided during instance creation. Oracle also documents that the default security list typically includes TCP 22 for SSH, and that Always Free resources are available for the life of the account in the home region.

## Prepare the server

On the VM:

```bash
sudo apt-get update
sudo apt-get install -y git
curl -fsSL https://get.docker.com | sudo sh
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
newgrp docker
```

Or run the repo bootstrap script after cloning:

```bash
sudo bash deploy/oracle/bootstrap.sh
```

## Deploy the bot

```bash
sudo mkdir -p /opt/govde
sudo chown -R ubuntu:ubuntu /opt/govde
cd /opt/govde
git clone https://github.com/alexsandrstepanyk/Cov.de.git .
cp .env.oracle.example .env.oracle
mkdir -p storage/pdf_letters logs
nano .env.oracle
docker compose -f docker-compose.oracle.yml up -d --build
```

Inside `.env.oracle`, set at least:

```env
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
```

## Useful commands

```bash
cd /opt/govde
docker compose -f docker-compose.oracle.yml logs -f
docker compose -f docker-compose.oracle.yml ps
docker compose -f docker-compose.oracle.yml up -d --build
docker compose -f docker-compose.oracle.yml pull
git pull
docker compose -f docker-compose.oracle.yml up -d --build
```

## Persistence

- `./storage/users.db` stores user and letter history
- `./storage/uploads/` stores uploaded files
- `./storage/pdf_letters/` stores generated PDFs
- `./logs/` stores logs from the host side

## Notes

- If `OLLAMA_BASE_URL` is not set, LLM features that depend on Ollama may be unavailable, but the bot can still start.
- If you want a static public IP, create and assign a reserved public IP in OCI after the VM is up.

## References

- Oracle Cloud Free Tier: https://www.oracle.com/cloud/free/
- Always Free resources: https://docs.oracle.com/iaas/Content/FreeTier/resourceref.htm
- Launching an instance: https://docs.oracle.com/iaas/Content/Compute/Tasks/launchinginstance.htm
- Reserved public IPs: https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/reserved-public-ip-create.htm
- Assign reserved public IP: https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/reserved-public-ip-assign.htm
