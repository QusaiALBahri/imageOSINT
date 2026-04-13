# Production Deployment Guide

## OSINT Image Tool - Backend Stack Deployment

### Architecture Overview

```
User Browser
    ↓
Gradio Frontend (7860)
    ↓
FastAPI API Server (8000)
    ↓
PostgreSQL Database
    ↓
Redis Cache & Message Broker
    ↓
Celery Worker Pool
```

## Prerequisites

- Docker & Docker Compose installed
- Python 3.9+ (for local development)
- 4GB RAM minimum
- PostgreSQL driver available

## Quick Start - Docker Compose

### Production Deployment

```bash
# 1. Clone/navigate to project
cd osint-image-tool

# 2. Create environment file
cp .env.example .env
# Edit .env with production settings

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f api
```

**Access the application:**
- Frontend: http://localhost:7860
- API Docs: http://localhost:8000/api/docs
- API Redoc: http://localhost:8000/api/redoc

### Development Deployment

```bash
docker-compose -f docker-compose.dev.yml up
```

## Manual Installation

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install requirements
pip install -r requirements-backend.txt
```

### 2. Setup PostgreSQL

```bash
# Option A: Using Docker
docker run -d \
  --name osint-postgres \
  -e POSTGRES_DB=osint_db \
  -e POSTGRES_USER=osint_user \
  -e POSTGRES_PASSWORD=osint_password \
  -p 5432:5432 \
  postgres:15-alpine

# Option B: Using local PostgreSQL
# Create database and user manually
```

### 3. Setup Redis

```bash
# Using Docker
docker run -d \
  --name osint-redis \
  -p 6379:6379 \
  redis:7-alpine

# Or using local Redis
redis-server
```

### 4. Initialize Database

```bash
python -c "from database.init_db import init_db; init_db()"
```

### 5. Start Services

**Terminal 1 - API Server:**
```bash
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
celery -A tasks.celery worker --loglevel=info --concurrency=4
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
celery -A tasks.celery beat --loglevel=info
```

**Terminal 4 - Gradio Frontend:**
```bash
python app_backend.py
```

## Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=osint_user
DB_PASSWORD=osint_password
DB_NAME=osint_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER=redis://localhost:6379/1
CELERY_BACKEND=redis://localhost:6379/2

# Security
SECRET_KEY=your-production-secret-key
JWT_SECRET=your-jwt-secret-key
DEBUG=False

# API
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO

# File Upload
MAX_UPLOAD_SIZE=104857600  # 100MB
```

## Database Management

### Create Tables

```bash
python -c "from database.init_db import init_db; init_db()"
```

### Drop Tables (Development Only)

```bash
python -c "from database.init_db import drop_db; drop_db()"
```

### Reset Database

```bash
python -c "from database.init_db import reset_db; reset_db()"
```

### Run Migrations (with Alembic)

```bash
alembic upgrade head
```

## Monitoring & Logs

### Docker Logs

```bash
# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f worker

# All logs
docker-compose logs -f
```

### Database Management

```bash
# Access PostgreSQL
docker exec -it osint-postgres psql -U osint_user -d osint_db

# Redis CLI
docker exec -it osint-redis redis-cli
```

### Celery Monitoring (Flower)

Flower is included in docker-compose on port 5555:

```
http://localhost:5555
```

## Performance Tuning

### Worker Concurrency

Edit `docker-compose.yml`:
```yaml
worker:
  command: celery -A tasks.celery worker --loglevel=info --concurrency=8
```

### Redis Persistence

Edit `docker-compose.yml`:
```yaml
redis:
  command: redis-server --appendonly yes
```

### Database Connection Pool

Edit `database/session.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=30,  # Increase for more connections
    max_overflow=60,
)
```

## SSL/HTTPS Setup

### Using Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name osint.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /api {
        proxy_pass http://localhost:8000/api;
    }
}
```

## Backup & Restore

### Backup Database

```bash
docker exec osint-postgres pg_dump -U osint_user osint_db > backup.sql
```

### Restore Database

```bash
docker exec -i osint-postgres psql -U osint_user osint_db < backup.sql
```

### Backup Uploads

```bash
docker run --rm -v osint_uploads:/data -v $(pwd):/backup \
  alpine tar czf /backup/uploads.tar.gz -C /data .
```

## Scaling

### Horizontal Scaling - Multiple Workers

```yaml
worker-1:
  service: worker
  instance: 1

worker-2:
  service: worker
  instance: 2

worker-3:
  service: worker
  instance: 3
```

### Load Balancing

Use Nginx or HAProxy to load balance across multiple API instances.

## Troubleshooting

### API Won't Start

```bash
# Check Python imports
python -c "import backend.server"

# Check port availability
lsof -i :8000

# Check logs
docker-compose logs api
```

### Worker Won't Connect

```bash
# Test Redis connection
redis-cli ping

# Test Celery connection
celery -A tasks.celery inspect active
```

### Database Connection Issues

```bash
# Test connection
psql -h localhost -U osint_user -d osint_db

# Check connection limit
docker exec osint-postgres psql -U osint_user -c "SHOW max_connections"
```

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use strong passwords for database
- [ ] Enable SSL/HTTPS
- [ ] Use environment variables for secrets
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Monitor logs for errors
- [ ] Set up rate limiting (nginx)
- [ ] Use strong JWT tokens
- [ ] Regular security updates

## Monitoring Solutions

### Option 1: Built-in Tools
- Flower (Celery monitoring)
- FastAPI docs at `/api/docs`

### Option 2: Third-party (Production)
- Sentry (error tracking)
- DataDog (monitoring)
- New Relic (performance)

Configure in `.env`:
```env
SENTRY_DSN=https://...@....ingest.sentry.io/...
PROMETHEUS_ENABLED=True
```

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
psql -h localhost -U osint_user -c "SELECT 1"

# Redis health
redis-cli ping
```

## Cleanup & Maintenance

### Remove old uploads (daily)

```bash
# Runs automatically via Celery Beat
# Or manually:
celery -A tasks.celery call tasks.cleanup_old_files
```

### Clear cache (manual)

```bash
redis-cli FLUSHDB
```

## Support & Troubleshooting

For issues:
1. Check logs: `docker-compose logs`
2. Check health: `curl http://localhost:8000/health`
3. Verify database: `docker exec osint-postgres psql -U osint_user -d osint_db -c "SELECT 1"`
4. Check Redis: `redis-cli ping`

---

**Deployment Complete!** 🚀
