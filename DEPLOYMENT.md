# TinkerTrack Deployment Guide

## Prerequisites
- Docker & Docker Compose installed
- GitHub account with SSH key configured
- Docker Hub account (or private registry)

## Local Setup

1. Clone the repo:
```bash
git clone https://github.com/veersc2007/tinkertrack.git
cd tinkertrack
```

2. Copy `.env.example` to `.env` and update with your values:
```bash
cp .env.example .env
```

3. Start services:
```bash
docker compose up -d
```

Access API at `http://localhost:8000/docs`

## GitHub Actions CI/CD

The workflow automatically builds and pushes to Docker Hub on every push to `main` branch.

### Setup:
1. Go to GitHub repo Settings → Secrets and variables → Actions
2. Add secrets:
   - `DOCKER_USERNAME`: your Docker Hub username (veersc2007)
   - `DOCKER_PASSWORD`: your Docker Hub Personal Access Token

Generate PAT at https://hub.docker.com/settings/security

### Push to trigger build:
```bash
git push origin main
```

## Production Deployment

### On Cloud Server (AWS/DigitalOcean/etc):

1. SSH into server
2. Clone repo:
```bash
git clone https://github.com/veersc2007/tinkertrack.git
cd tinkertrack
```

3. Copy `.env.example` to `.env.prod` and update with production values:
```bash
cp .env.example .env.prod
nano .env.prod
```

4. Use production compose file:
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

5. Verify:
```bash
docker ps
docker compose -f docker-compose.prod.yml logs tinkertrack
```

### With Docker Swarm (multi-node):

1. Initialize swarm:
```bash
docker swarm init
```

2. Deploy stack:
```bash
docker stack deploy -c docker-compose.prod.yml tinkertrack
```

3. Check status:
```bash
docker stack services tinkertrack
docker service logs tinkertrack_tinkertrack
```

### Nginx Reverse Proxy (optional):

Add to production server for HTTPS:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

Check container health:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

View logs:
```bash
docker compose logs -f tinkertrack
docker compose logs -f postgres
```

## Rollback

Pull previous image version:
```bash
docker pull veersc2007/tinkertrack:PREVIOUS_SHA
docker compose set-image tinkertrack=veersc2007/tinkertrack:PREVIOUS_SHA
docker compose up -d
```
