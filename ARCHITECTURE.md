# Project Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Gradio Web Interface                     │
│           (localhost:7860 - User-Facing Dashboard)          │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐          ┌──────────┐        ┌──────────┐
   │ Metadata │          │  Image   │        │ Location │
   │Extractor │          │  Search  │        │Extractor │
   └────┬────┘          └────┬─────┘        └────┬─────┘
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────────────────────────────────────────────┐
   │           Core Processing Pipeline              │
   │  - EXIF Parsing  - Web Scraping - Geocoding    │
   └──────────────────┬──────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Google   │  │  Bing    │  │  Yandex  │
   │ Images   │  │ Images   │  │ Images   │
   └──────────┘  └──────────┘  └──────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
   ┌──────────────┐         ┌──────────────────┐
   │ Google Maps  │         │ Nominatim/OpenSM│
   │ Scraper      │         │ Geocoding        │
   └──────────────┘         └──────────────────┘
        │                            │
        └────────────┬───────────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │   Results Compiler  │
          │   & Formatter       │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  Output Files/JSON  │
          │  Reports & Logs     │
          └─────────────────────┘
```

## Data Flow

### Image Processing Pipeline

```
User Input (Image/URL)
    │
    ├─→ File Validation
    │   - Format check
    │   - Size validation
    │
    ├─→ Metadata Extraction
    │   ├─ EXIF parsing
    │   ├─ GPS extraction
    │   └─ Camera info
    │
    ├─→ Reverse Geocoding
    │   ├─ GPS → Address
    │   └─ Confidence scoring
    │
    ├─→ Reverse Image Search
    │   ├─ Google Images
    │   ├─ Bing Images
    │   └─ Yandex Images
    │
    ├─→ Maps Scraping
    │   ├─ Nearby places
    │   ├─ Street View
    │   └─ Business listings
    │
    └─→ Results Compilation
        ├─ Data merging
        ├─ JSON formatting
        └─ Report generation
```

## Module Dependencies

```
app.py (Main Application)
├── gradio
├── config.py
│   └── Settings & constants
├── modules/
│   ├── metadata_extractor.py
│   │   ├── PIL
│   │   └── exifread
│   ├── location_extractor.py
│   │   └── geopy
│   ├── image_search.py
│   │   ├── requests
│   │   └── beautifulsoup4
│   ├── maps_scraper.py
│   │   ├── requests
│   │   └── beautifulsoup4
│   └── utils.py
│       ├── requests
│       └── fake-useragent
```

## Request Flow

```
User Browser
    │
    ├─ HTTP GET/POST
    │
    ▼
Gradio Server (FastAPI)
    │
    ├─ Route handler: /api/predict
    │
    ▼
Python Function
    │
    ├─ Load image
    ├─ Run analysis
    ├─ Gather results
    │
    ▼
JSON Response
    │
    ├─ HTTP Response
    │
    ▼
User Interface Update
    │
    └─ Display results
```

## Configuration Hierarchy

```
Global Defaults (config.py)
    │
    ├─ .env file (override)
    │   └─ Environment-specific settings
    │
    └─ Runtime parameters
        └─ User-provided inputs
```

## Error Handling Flow

```
Operation
    │
    ├─ Try operation
    │
    ├─ Catch exception
    │   ├─ Log error
    │   ├─ Check if recoverable
    │   ├─ Retry if appropriate
    │   └─ Return user-friendly message
    │
    └─ User notification
```

## File Organization

```
osint-image-tool/
│
├── Core Application
│   ├── app.py                 # Main Gradio interface
│   ├── config.py              # Configuration
│   ├── run.py                 # Startup script
│   └── setup_dirs.py          # Directory initialization
│
├── Processing Modules
│   └── modules/
│       ├── __init__.py
│       ├── utils.py           # Utility functions
│       ├── metadata_extractor.py
│       ├── location_extractor.py
│       ├── image_search.py
│       └── maps_scraper.py
│
├── Data Directories
│   ├── uploads/               # Uploaded/downloaded images
│   ├── outputs/               # Generated reports
│   └── logs/                  # Application logs
│
└── Documentation
    ├── README.md              # Full documentation
    ├── QUICKSTART.md          # Quick start guide
    ├── examples.py            # Code examples
    ├── ARCHITECTURE.md        # This file
    ├── requirements.txt       # Dependencies
    └── .env.example           # Environment template
```

## Security Considerations

```
┌────────────────────────────────────────┐
│        Input Validation Layer          │
├────────────────────────────────────────┤
│ - File type validation                 │
│ - File size limits                     │
│ - URL validation                       │
└────────────────────────────────────────┘
              ▼
┌────────────────────────────────────────┐
│      Rate Limiting & Throttling        │
├────────────────────────────────────────┤
│ - 1-2 second delay between requests    │
│ - User-Agent rotation                  │
│ - Request timeout handling             │
└────────────────────────────────────────┘
              ▼
┌────────────────────────────────────────┐
│      Error Handling & Logging          │
├────────────────────────────────────────┤
│ - Try-catch blocks                     │
│ - Detailed error logging               │
│ - User-friendly messages               │
└────────────────────────────────────────┘
              ▼
┌────────────────────────────────────────┐
│      Ethical Scraping Practices        │
├────────────────────────────────────────┤
│ - Respect robots.txt                   │
│ - Realistic user agents                │
│ - Rate limiting                        │
│ - No credential harvesting             │
└────────────────────────────────────────┘
```

## Performance Optimization

```
Metadata Extraction
  └─ Parallel EXIF parsing: ~100ms

Image Search (Parallel)
  ├─ Google Images: ~2-3s
  ├─ Bing Images: ~2-3s
  └─ Yandex Images: ~2-3s
  
Location Processing
  ├─ GPS extraction: ~50ms
  ├─ Reverse geocoding: ~1-2s
  └─ Maps scraping: ~2-3s

Total Average Time: ~8-12 seconds
```

## Scalability Considerations

### For Production Deployment

1. **Database Backend**
   - Cache results for repeated queries
   - Store historical analyses
   - Improve response times

2. **Queue System**
   - Use Celery/RQ for async processing
   - Handle long-running tasks
   - Support batch processing

3. **Load Balancing**
   - Multiple Gradio instances
   - Reverse proxy (Nginx)
   - Distributed request handling

4. **Caching Layer**
   - Redis for result caching
   - Rate limit tracking
   - Session management

5. **Monitoring**
   - Prometheus metrics
   - Error tracking (Sentry)
   - Performance monitoring

## API Endpoints (Future REST API)

```
POST /api/analyze
  - Input: image file or URL
  - Output: comprehensive analysis JSON
  
POST /api/metadata
  - Input: image file
  - Output: metadata JSON
  
POST /api/reverse-search
  - Input: image file
  - Output: search results
  
POST /api/location
  - Input: GPS coordinates or address
  - Output: location analysis
  
POST /api/maps
  - Input: latitude, longitude
  - Output: nearby places
```

---

**Last Updated:** January 2024
