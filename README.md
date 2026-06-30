# 🏢 TinkerTrack - Smart Resource Management System

A modern, fully containerized FastAPI backend system for managing shared resources like rooms, equipment, and facilities.

## ✨ Features

- 📅 **Smart Reservation System** with conflict detection
- ⏳ **Waitlist Management** with auto-promotion
- 🔔 **Real-time Notifications** system
- 📊 **Analytics Dashboard** for resource usage
- 🔐 **Role-based Access Control** (Admin/User)
- 🐳 **100% Dockerized** - runs on any PC/server
- 🚀 **Automated CI/CD** with GitHub Actions
- 🧪 **Automated Testing** with pytest
- 🛡️ **Security Scanning** with Trivy

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (https://www.docker.com/products/docker-desktop)
- Git (optional, if cloning from GitHub)

### Run Locally (30 seconds)

```bash
# Clone repo
git clone https://github.com/veersc2007/tinkertrack.git
cd tinkertrack

# Start all services
docker compose up -d

# Access API
open http://localhost:8000/docs
```

That's it! No Python installation needed.

### Stop Services

```bash
docker compose down
```

## 📖 Documentation

- **[API Docs](http://localhost:8000/docs)** - Interactive Swagger UI (when running)
- **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment instructions
- **[CI/CD Setup](./CI_CD_SETUP.md)** - GitHub Actions configuration
- **[Checklist](./CHECKLIST.md)** - Progress tracking

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     FastAPI (Uvicorn)               │
│     Port 8000                       │
│  ├─ Authentication (JWT)            │
│  ├─ Resource Management             │
│  ├─ Reservations                    │
│  ├─ Waitlist                        │
│  └─ Analytics                       │
└──────────┬──────────────────────────┘
           │
           │ (SQL)
           ▼
┌─────────────────────────────────────┐
│     PostgreSQL Database             │
│     Port 5432                       │
│     tinkertrack_db                  │
└─────────────────────────────────────┘
```

## 🔧 Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements_lite.txt

# Install dev tools
pip install pytest pytest-cov black flake8

# Run tests
pytest tests/ -v

# Check code style
black app
flake8 app

# Run locally (without Docker)
uvicorn app.main:app --reload --port 8000
```

### Run Tests in Docker

```bash
docker compose exec tinkertrack python -m pytest tests/ -v
```

## 🐳 Docker Commands

```bash
# View running containers
docker ps

# View logs
docker logs tinkertrack-api
docker logs tinkertrack-db

# Connect to database
docker exec -it tinkertrack-db psql -U tinkertrack_user -d tinkertrack_db

# Rebuild image
docker compose build --no-cache

# Remove everything and start fresh
docker compose down -v
docker compose up -d
```

## 📦 Deployment

### Production Deployment

```bash
# Copy to server
scp -r tinkertrack/ user@server:/home/

# On server
cd tinkertrack
cp .env.example .env.prod
# Edit .env.prod with production values
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Deploy to Cloud

See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- AWS EC2
- DigitalOcean Droplet
- Azure App Service
- Google Cloud Run
- Docker Swarm
- Kubernetes

## 🚀 CI/CD Pipeline

Automated with GitHub Actions:

1. **Test** - pytest on every push
2. **Lint** - Code quality checks (flake8, black)
3. **Build** - Docker image creation
4. **Push** - Uploaded to Docker Hub
5. **Security** - Trivy vulnerability scan
6. **Deploy Ready** - Ready for production

### Setup CI/CD

See [CI_CD_SETUP.md](./CI_CD_SETUP.md) for step-by-step GitHub Actions setup.

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Resources
- `GET /resources` - List all resources
- `POST /resources` - Create new resource
- `GET /resources/{id}` - Get resource details
- `PUT /resources/{id}` - Update resource
- `DELETE /resources/{id}` - Delete resource

### Reservations
- `GET /reservations` - List reservations
- `POST /reservations` - Create reservation
- `GET /reservations/{id}` - Get reservation details
- `PUT /reservations/{id}` - Update reservation
- `DELETE /reservations/{id}` - Cancel reservation

### More endpoints
See interactive docs at `http://localhost:8000/docs`

## 🛡️ Security

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ Role-based access control
- ✅ Environment variables for secrets
- ✅ HTTPS-ready (use reverse proxy in production)
- ✅ Automated security scanning (Trivy)

**⚠️ Important:** Change `SECRET_KEY` in production!

```bash
# Generate new secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📝 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
POSTGRES_USER=tinkertrack_user
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DB=tinkertrack_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
DEBUG=False
```

## 🐛 Troubleshooting

### API not responding
```bash
docker ps  # Check if containers are running
docker logs tinkertrack-api  # Check logs
```

### Database connection error
```bash
docker logs tinkertrack-db  # Check database logs
docker compose down -v && docker compose up -d  # Restart everything
```

### Port already in use
Change ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead
```

## 📈 Performance

- **Image size**: ~450MB (Python 3.11 slim + dependencies)
- **Startup time**: ~5 seconds
- **Build time**: ~30 seconds (first build), ~5 seconds (cached)
- **Database**: PostgreSQL 16 Alpine (~180MB)

## 📚 Tech Stack

- **Framework**: FastAPI (modern, fast)
- **Server**: Uvicorn (ASGI)
- **Database**: PostgreSQL (reliable, powerful)
- **Auth**: JWT + Bcrypt
- **Testing**: pytest
- **CI/CD**: GitHub Actions
- **Container**: Docker & Docker Compose
- **Cloud**: AWS/Azure/GCP ready

## 🤝 Contributing

1. Fork repo
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

All tests must pass and code style must be checked.

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

**Adityaveer Singh Chauhan**
- GitHub: [@veersc2007](https://github.com/veersc2007)
- Docker Hub: [@veersc2007](https://hub.docker.com/u/veersc2007)

## 🆘 Support

- 📖 [Documentation](./DEPLOYMENT.md)
- 🐛 [GitHub Issues](https://github.com/veersc2007/tinkertrack/issues)
- 💬 [Discussions](https://github.com/veersc2007/tinkertrack/discussions)

---

**Made with ❤️ by TinkerTrack Team**
