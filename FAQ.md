# Frequently Asked Questions (FAQ)

## Installation & Setup

### Q1: What are the system requirements?

**A:** ImageOSINT requires:
- Python 3.9 or higher
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL 15+ (recommended) or SQLite (development)
- Redis 7+ (for caching)
- 2GB+ RAM minimum
- Stable internet connection

### Q2: Can I use SQLite instead of PostgreSQL?

**A:** Yes! Set `DATABASE_TYPE=sqlite` in `.env`. SQLite is great for development and small deployments. For production, PostgreSQL is recommended.

### Q3: Do I need to install Docker?

**A:** Not required, but highly recommended. For manual setup, you'll need to install and manage PostgreSQL, Redis, and Celery separately.

### Q4: How do I set up the development environment?

**A:** 
```bash
git clone https://github.com/QusaiALBahri/imageOSINT.git
cd imageOSINT
pip install -r requirements-backend.txt
docker-compose -f docker-compose.dev.yml up -d
python -c "from database.init_db import init_db; init_db()"
```

---

## Usage & Features

### Q5: How do I use the API programmatically?

**A:** See the [API Examples](README.md#-api-examples) section in README. Quick example:

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
})
token = response.json()["access_token"]

# Submit analysis
response = requests.post(
    f"{BASE_URL}/api/analyze",
    headers={"Authorization": f"Bearer {token}"},
    files={"file": open("image.jpg", "rb")}
)
```

### Q6: What image formats are supported?

**A:** Currently supported formats:
- JPEG / JPG
- PNG
- GIF
- WebP
- BMP

Maximum file size: 100MB (configurable in `.env`)

### Q7: How accurate is the geolocation?

**A:** Accuracy depends on image metadata quality:
- Excellent: If image has GPS coordinates (±10 meters)
- Good: If image has partial EXIF data (±100 meters)
- Fair: If reverse geocoding from address (±500 meters)
- Poor: If no metadata present

### Q8: Can I process multiple images at once?

**A:** Currently, submit one image per job. For batch processing, implement a loop:

```python
for image_file in os.listdir("images/"):
    # Submit each image
    requests.post(f"{BASE_URL}/api/analyze", ...)
```

Batch API is planned for v1.1.

### Q9: How long does analysis take?

**A:** Typical timing:
- **Metadata extraction**: ~100ms
- **Reverse search**: 2-3s per engine (3 engines = parallel)
- **Location analysis**: 1-2s
- **Maps scraping**: 2-3s
- **Total**: 8-12 seconds (parallelized)
- **Cached result**: <100ms

---

## Performance & Scaling

### Q10: Can I scale to handle more requests?

**A:** Yes! ImageOSINT is built for horizontal scaling:

1. **Add more workers**:
   ```bash
   docker-compose up -d --scale worker=4 # 4 workers
   ```

2. **Use load balancer** (Nginx):
   ```nginx
   upstream api {
       server api:8000;
   }
   ```

3. **Enable Redis clustering** for production

4. **Use database replication**

See [DEPLOYMENT.md](DEPLOYMENT.md) for details.

### Q11: How do I monitor performance?

**A:** Use the Flower dashboard:

```
http://localhost:5555
```

Features:
- Task execution monitoring
- Worker status
- Performance metrics
- Real-time statistics

### Q12: What's the cache hit rate I can expect?

**A:** Depends on usage patterns:
- **Identical images**: ~90%+ hit rate (cache hit <100ms)
- **Similar images**: ~30% hit rate
- **Unique images**: 0% hit rate

Configure cache TTL in `.env`:
- Search results: 24 hours
- Location/maps: 7 days

---

## Security & Authentication

### Q13: How do I create API keys for programmatic access?

**A:** Use the admin panel or API:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bot@example.com",
    "username": "bot",
    "password": "StrongPassword123!"
  }'
```

Then use the returned token as Bearer token.

### Q14: How do I change the JWT secret for production?

**A:** Update `.env`:

```env
JWT_SECRET=your_new_super_secret_key_min_32_chars
JWT_ALGORITHM=HS256
TOKEN_EXPIRY=1800  # 30 minutes
```

Restart services:
```bash
docker-compose down
docker-compose up -d
```

### Q15: Is my data encrypted?

**A:** 
- **In transit**: Configure HTTPS/TLS
- **At rest**: Use encrypted database connections
- **Passwords**: Bcrypt hashing with salt
- **Database**: Data stored unencrypted by default (configure encryption as needed)

See [SECURITY.md](SECURITY.md) for complete security info.

### Q16: How do I set up HTTPS?

**A:** Configure Nginx reverse proxy with Let's Encrypt:

See [DEPLOYMENT.md](DEPLOYMENT.md#ssl--https-setup) for detailed steps.

---

## Troubleshooting

### Q17: "Connection refused" error

**A:** Ensure services are running:

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Restart services
docker-compose restart
```

### Q18: "Database connection error"

**A:** Verify database is running:

```bash
# Check PostgreSQL
docker-compose ps postgres

# Test connection
psql -U osint_user -d osint_db -h localhost
```

### Q19: Tasks are stuck/not processing

**A:** Check Celery workers:

```bash
# View workers
celery -A tasks.celery inspect active

# Check queue length
celery -A tasks.celery inspect reserved

# Monitor with Flower
http://localhost:5555
```

### Q20: "Permission denied" for uploads

**A:** Fix directory permissions:

```bash
chmod -R 755 uploads/
chmod -R 755 outputs/
```

Or use Docker (handles automatically).

### Q21: High CPU/Memory usage

**A:** Optimize worker configuration:

```env
# In .env
WORKERS_COUNT=2  # Reduce from 4
CELERY_WORKER_CONCURRENCY=2
```

Then restart:
```bash
docker-compose restart worker
```

---

## Deployment & Operations

### Q22: How do I backup my data?

**A:** 
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U osint_user osint_db > backup.sql

# Redis backup
docker-compose exec redis redis-cli BGSAVE

# File backups
tar -czf uploads_backup.tar.gz uploads/
```

### Q23: How do I restore from backup?

**A:** 
```bash
# PostgreSQL restore
docker-compose exec postgres psql -U osint_user osint_db < backup.sql

# Redis restore
docker-compose cp dump.rdb redis:/data/
docker-compose restart redis
```

### Q24: Can I use this in production?

**A:** Yes! Production checklist:

- [ ] Change all default passwords
- [ ] Update JWT_SECRET to 32+ char random string
- [ ] Enable SSL/TLS
- [ ] Configure proper CORS origins
- [ ] Set up log aggregation
- [ ] Configure monitoring and alerts
- [ ] Set up automated backups
- [ ] Enable rate limiting
- [ ] Use strong database passwords
- [ ] Enable Redis authentication

See [DEPLOYMENT.md](DEPLOYMENT.md) for production guide.

### Q25: How do I update ImageOSINT?

**A:** 
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements-backend.txt --upgrade

# Restart services
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Integration & Plugins

### Q26: Can I integrate with other tools?

**A:** Yes! Use the REST API:

```python
import requests

api_client = requests.session()
api_client.headers.update({
    "Authorization": f"Bearer {your_token}",
    "Content-Type": "application/json"
})

# Use any endpoint on http://localhost:8000/api/*
```

### Q27: Can I add custom analysis modules?

**A:** Yes! Create a module in `modules/`:

```python
# modules/custom_analyzer.py
class CustomAnalyzer:
    def analyze(self, image_path):
        # Your custom logic
        return results
```

Then add a Celery task for it.

### Q28: Can I modify the UI?

**A:** Absolutely! Edit `app_backend.py`:

```python
# Add your own Gradio interfaces
# Deploy to frontend port 7860
```

---

## Contributing & Development

### Q29: How do I contribute?

**A:** See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines. Quick start:

1. Fork repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

### Q30: Where can I report bugs?

**A:** 
- **Security issues**: [SECURITY.md](SECURITY.md)
- **Regular bugs**: [GitHub Issues](https://github.com/QusaiALBahri/imageOSINT/issues)
- **Questions**: [GitHub Discussions](https://github.com/QusaiALBahri/imageOSINT/discussions)

---

## More Questions?

- 📖 Read [README.md](README.md)
- 📚 Check [DEPLOYMENT.md](DEPLOYMENT.md)
- 🏗️ Review [BACKEND_SETUP.md](BACKEND_SETUP.md)
- 💬 Open [GitHub Discussion](https://github.com/QusaiALBahri/imageOSINT/discussions)
- 📧 Contact maintainers

**Last Updated**: April 13, 2024
