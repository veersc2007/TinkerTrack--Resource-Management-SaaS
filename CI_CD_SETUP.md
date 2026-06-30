# GitHub Actions CI/CD Setup Guide

## What's Automated

Your GitHub Actions workflow now does:

1. **Test** — Runs pytest on every push/PR
2. **Lint** — Checks code quality with flake8 and black
3. **Build** — Builds Docker image on `main` branch
4. **Push** — Pushes to Docker Hub automatically
5. **Security Scan** — Trivy vulnerability scanning
6. **Deploy Ready** — Notifies when ready for production

## Setup Steps

### 1. Create GitHub Repository

```bash
cd ~/tinkertrack
git init
git add .
git commit -m "Initial commit: Dockerized TinkerTrack API"
git branch -M main
git remote add origin https://github.com/veersc2007/tinkertrack.git
git push -u origin main
```

### 2. Add Docker Hub Credentials to GitHub

1. Go to **GitHub repo** → Settings → Secrets and variables → Actions
2. Click **New repository secret**
3. Add two secrets:

   **Secret 1:**
   - Name: `DOCKER_USERNAME`
   - Value: `veersc2007`

   **Secret 2:**
   - Name: `DOCKER_PASSWORD`
   - Value: (Your Docker Hub Personal Access Token)

**To get Docker Hub PAT:**
- Go to https://hub.docker.com/settings/security
- Click "New Access Token"
- Name it "github-ci"
- Give it "Read, Write" permissions
- Copy and paste into GitHub secret

### 3. Verify Workflow

1. Go to GitHub repo → **Actions** tab
2. You should see the workflow running automatically
3. Watch the build progress in real-time

## What Happens on Each Push

### On Push to `main` Branch:
```
✅ Tests run (pytest)
✅ Code linting (flake8, black)
✅ Docker image built
✅ Pushed to Docker Hub as:
   - veersc2007/tinkertrack:latest
   - veersc2007/tinkertrack:main-<sha>
✅ Security scan (Trivy)
✅ Ready for deployment
```

### On Pull Request:
```
✅ Tests run
✅ Code linting
✅ Docker image built (NOT pushed)
```

## Deployment on Production Server

Once GitHub Actions builds successfully:

```bash
# SSH into production server
ssh user@your-server

# Navigate to project
cd tinkertrack

# Pull latest image
docker pull veersc2007/tinkertrack:latest

# Deploy using production compose file
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Verify
docker ps
```

## Test Locally Before Pushing

```bash
# Install dev dependencies
pip install pytest pytest-cov black flake8

# Run tests
pytest tests/ -v

# Check code style
black app --check
flake8 app

# Build image
docker build -t tinkertrack:test .

# Test image
docker run --rm tinkertrack:test python -m pytest tests/
```

## Monitoring Workflow

- **See build status**: GitHub repo → Actions
- **See logs**: Click on workflow run → Click job → See logs
- **See image on Docker Hub**: https://hub.docker.com/r/veersc2007/tinkertrack

## Common Issues

### "Build failed: Docker Hub authentication"
- Check `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are correct
- Verify PAT has "Read, Write" permissions

### "Tests failing in CI but pass locally"
- Likely missing test dependency
- Add to `requirements_lite.txt`: `pytest`, `pytest-cov`

### "Image not pushed to Docker Hub"
- Make sure you pushed to `main` branch (not `develop`)
- Check GitHub Actions logs for errors

## Next Steps

1. Enable branch protection: Settings → Branches → Add rule
   - Require status checks to pass before merging
   - Require tests pass on PRs

2. Enable auto-deployment: Add deploy step to `.github/workflows/docker-build.yml`
   - SSH to production server
   - Pull latest image
   - Restart containers

3. Monitor with GitHub health checks or webhooks
