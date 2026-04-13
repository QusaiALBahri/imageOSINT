# Backend Architecture & Implementation

## Overview

The backend has been completely rebuilt with a production-ready architecture featuring:

### Core Components

1. **FastAPI Server** (`backend/server.py`)
   - RESTful API endpoints
   - JWT authentication
   - Rate limiting and error handling
   - OpenAPI/Swagger documentation

2. **Database Layer** (`database/`)
   - SQLAlchemy ORM models
   - PostgreSQL, MySQL, or SQLite support
   - User management
   - Job tracking and result storage
   - Search history and caching

3. **Async Task Queue** (`tasks/`)
   - Celery worker pool
   - Distributed image analysis
   - Background processing
   - Scheduled maintenance tasks

4. **Caching System** (`core/cache.py`)
   - Redis-based result caching
   - In-memory fallback
   - Hit rate tracking

5. **Frontend** (`app_backend.py`)
   - Gradio interface communicating with backend API
   - User authentication
   - Job submission and monitoring

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Browser                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Gradio Frontend (port 7860)                               │
│  - Login/Register                                           │
│  - Submit Analysis                                          │
│  - Check Status                                             │
│  - View Results                                             │
│                                                              │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────┐
│          FastAPI Backend (port 8000)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /api/auth  - User authentication                          │
│  /api/analyze - Job submission                             │
│  /api/search - Reverse image search                        │
│  /api/location - Location analysis                         │
│  /api/stats - User statistics                              │
│                                                              │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┼────────┐
        │        │        │
        ▼        ▼        ▼
    PostgreSQL  Redis   Celery Workers
    Database    Cache   (port 5555 - Flower)
```

## Database Schema

### Users Table
- id (UUID)
- email, username
- password_hash
- created_at, updated_at
- is_active, is_admin

### AnalysisJobs Table
- job_id (UUID unique)
- user_id (foreign key)
- file_path, filename
- analysis_types
- status (pending/processing/completed/failed)
- progress, results
- processing_time

### SearchHistory Table
- id
- user_id (foreign key)
- image_filename
- search_engines
- created_at

### CachedResults Table
- id
- cache_key (unique)
- result_type
- result_data (JSON)
- hit_count, expires_at

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Analysis
- `POST /api/analyze` - Submit image analysis
- `GET /api/analyze/{job_id}` - Get job status
- `GET /api/analyze/{job_id}/results` - Get results

### Search
- `POST /api/search/reverse` - Reverse image search
- `GET /api/search/history` - Search history

### Location
- `POST /api/location/analyze` - Analyze GPS coordinates
- `POST /api/maps/nearby` - Get nearby places

### Tasks
- `GET /api/tasks/{task_id}` - Celery task status
- `GET /api/tasks/{task_id}/results` - Task results

### Cache & Stats
- `GET /api/cache/stats` - Cache statistics
- `DELETE /api/cache` - Clear cache
- `GET /api/stats` - User statistics

## Installation

### Option 1: Docker Compose (Recommended)

```bash
# Production
docker-compose up -d

# Development
docker-compose -f docker-compose.dev.yml up
```

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements-backend.txt

# 2. Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# 3. Start PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=osint_password \
  postgres:15-alpine

# 4. Initialize database
python -c "from database.init_db import init_db; init_db()"

# 5. Start services (in separate terminals)
# Terminal 1
uvicorn backend.server:app --reload

# Terminal 2
celery -A tasks.celery worker

# Terminal 3
celery -A tasks.celery beat

# Terminal 4
python app_backend.py
```

## Configuration Files

### `.env` - Environment Variables
All configuration is managed through environment variables:
- Database credentials
- Redis URL
- Celery broker settings
- JWT secrets
- API keys

### `docker-compose.yml` - Production
- PostgreSQL database
- Redis cache
- FastAPI server
- Celery workers and beat
- Gradio frontend
- Flower monitoring

### `docker-compose.dev.yml` - Development
- Lightweight setup
- Debug mode enabled
- Live code reloading
- Verbose logging

## Celery Tasks

Located in `tasks/celery_tasks.py`:

1. **process_image_analysis** - Complete pipeline
2. **extract_metadata_task** - EXIF extraction
3. **reverse_image_search_task** - Multi-engine search
4. **location_analysis_task** - GPS to address
5. **maps_scraping_task** - Nearby places
6. **cleanup_old_files** - Daily maintenance
7. **cleanup_expired_cache** - Cache maintenance

## Performance Characteristics

- **Metadata Extraction**: ~100ms
- **Reverse Search**: 2-3 seconds per engine
- **Location Analysis**: 1-2 seconds
- **Maps Scraping**: 2-3 seconds
- **Total Pipeline**: 8-12 seconds

With Celery workers, multiple jobs run in parallel.

## Monitoring

### Built-in Tools
- **Flower** (Celery monitoring): http://localhost:5555
- **FastAPI Docs**: http://localhost:8000/api/docs
- **FastAPI ReDoc**: http://localhost:8000/api/redoc

### Logs
- API logs: `docker-compose logs api`
- Worker logs: `docker-compose logs worker`
- All services: `docker-compose logs`

## Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- API rate limiting
- Request validation with Pydantic
- CORS configuration
- SQL injection protection (SQLAlchemy ORM)
- Secure headers with FastAPI

## Scaling Options

1. **Horizontal Scaling**
   - Multiple Celery workers
   - Load balancer for API
   - Database replication

2. **Caching**
   - Redis cluster for distributed cache
   - Multi-level caching strategy

3. **CDN**
   - CloudFront for static assets
   - Distributed geographic presence

## Development Workflow

1. **Setup**: `docker-compose -f docker-compose.dev.yml up`
2. **Code**: Edit files (auto-reload enabled)
3. **Test**: Access http://localhost:7860
4. **Debug**: Check logs with `docker-compose logs -f`
5. **Monitor**: View Flower at http://localhost:5555

## Deployment

See `DEPLOYMENT.md` for:
- Production setup
- SSL/HTTPS configuration
- Backup and restore procedures
- Performance tuning
- Monitoring solutions
- Security checklist

## Troubleshooting

### Services Won't Start
```bash
docker-compose logs
# Check error messages

# Check if ports are in use
lsof -i :8000
lsof -i :5432
lsof -i :6379
```

### Database Connection Issues
```bash
# Test PostgreSQL
psql -h localhost -U osint_user -d osint_db

# Test Redis
redis-cli ping

# Recreate database
python -c "from database.init_db import reset_db; reset_db()"
```

### Worker Not Processing
```bash
# Check Celery status
celery -A tasks.celery inspect active

# View pending tasks
celery -A tasks.celery inspect scheduled

# Check worker health
celery -A tasks.celery inspect ping
```

## Next Steps

1. Configure your `.env` file
2. Start services with `docker-compose up`
3. Create account via Gradio frontend
4. Submit image for analysis
5. Monitor progress in Flower (port 5555)
6. Retrieve results when complete

---

**Full Backend Stack Ready!** 🚀
