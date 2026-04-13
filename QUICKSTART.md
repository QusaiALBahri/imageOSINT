# OSINT Image Search & Google Maps Scraper

## Quick Start Commands

### Windows

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Or use the startup script
python run.py
```

### macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 app.py

# Or use the startup script
python3 run.py
```

### Access Application
- Open browser and go to: **http://localhost:7860**
- The Gradio interface will be ready to use

## Troubleshooting Startup

### Port Already in Use
If port 7860 is already in use, edit `app.py`:
```python
demo.launch(
    server_port=7861,  # Change to available port
    ...
)
```

### Permission Denied (macOS/Linux)
```bash
chmod +x run.py
./run.py
```

### Import Errors
Re-install dependencies:
```bash
pip install --force-reinstall -r requirements.txt
```

## First Run Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] No port conflicts (7860 is free)
- [ ] Internet connection available
- [ ] Directories created (uploads/, outputs/, modules/)

## Common Issues

**Issue: "ModuleNotFoundError"**
- Solution: Make sure virtual environment is activated

**Issue: "Connection refused"**
- Solution: Make sure port 7860 is not in use

**Issue: "Image download failed"**
- Solution: Check internet connection and image URL validity

## Need Help?

1. Check the README.md file for detailed documentation
2. Review the documentation tab in the Gradio interface
3. Check error messages in the console output
4. Try individual analysis tabs instead of Quick Analysis

---

**Happy Investigating! 🔍**
