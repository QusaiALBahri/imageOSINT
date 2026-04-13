@echo off
REM ImageOSINT GitHub Push Script

echo Navigating to project directory...
cd /d C:\Users\qusai\Downloads\work\python\image_osint

echo.
echo Checking git status...
git status

echo.
echo Configuring git user (if not already configured)...
git config --local user.name "Qusai Al Bahri"
git config --local user.email "qusai@example.com"

echo.
echo Initializing git repository...
git init

echo.
echo Adding all files...
git add .

echo.
echo Creating initial commit...
git commit -m "chore: Initial commit - Production ready ImageOSINT v1.0.0

- Complete FastAPI backend with 30+ endpoints
- PostgreSQL database with 7 models
- Celery async task queue with 6 tasks
- Redis caching layer
- JWT + Bcrypt authentication
- Docker containerization (6 services)
- Gradio web interface
- Comprehensive documentation (10 files)
- Security best practices
- Production-ready architecture"

echo.
echo Setting branch to main...
git branch -M main

echo.
echo Adding GitHub remote...
git remote add origin https://github.com/QusaiALBahri/imageOSINT.git

echo.
echo Pushing to GitHub...
echo Note: You may be prompted to authenticate with GitHub
echo If using HTTPS, you may need a personal access token
echo.
git push -u origin main

echo.
echo Push complete!
echo Repository URL: https://github.com/QusaiALBahri/imageOSINT
pause
