@echo off
REM ===========================================
REM ImageOSINT - Complete GitHub Push Script
REM ===========================================
REM This script will push your repository to GitHub

setlocal enabledelayedexpansion

color 0A
echo.
echo =========================================
echo      ImageOSINT GitHub Push Script
echo =========================================
echo.

REM Set project directory
set PROJECT_DIR=C:\Users\qusai\Downloads\work\python\image_osint

echo [*] Project Directory: %PROJECT_DIR%
echo.

REM Check if directory exists
if not exist "%PROJECT_DIR%" (
    color 0C
    echo [ERROR] Project directory not found!
    echo [ERROR] Directory: %PROJECT_DIR%
    pause
    exit /b 1
)

cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    color 0C
    echo [ERROR] Could not change to project directory!
    pause
    exit /b 1
)

color 0A
echo [✓] Successfully navigated to project directory
echo.

REM Check git installation
echo [*] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Git is not installed or not in PATH!
    echo [INFO] Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)
color 0A
echo [✓] Git is installed
echo.

REM Configure git
echo [*] Configuring Git...
git config --local user.name "Qusai Al Bahri" 2>nul
git config --local user.email "qusai@example.com" 2>nul
color 0A
echo [✓] Git configured
echo.

REM Initialize repository if needed
if not exist ".git" (
    echo [*] Initializing Git repository...
    git init
    color 0A
    echo [✓] Repository initialized
) else (
    color 0A
    echo [✓] Repository already initialized
)
echo.

REM Add all files
echo [*] Adding files to Git...
git add .
if errorlevel 1 (
    color 0C
    echo [ERROR] Failed to add files!
    pause
    exit /b 1
)
color 0A
echo [✓] Files added
echo.

REM Check for changes
set CHANGES_EXIST=0
git diff --cached --quiet
if errorlevel 1 set CHANGES_EXIST=1

REM Commit if there are changes
if %CHANGES_EXIST%==1 (
    echo [*] Creating commit...
    git commit -m "chore: Initial commit - Production ready ImageOSINT v1.0.0

- Complete FastAPI backend with 30+ API endpoints
- PostgreSQL database with 7 SQLAlchemy models
- Celery async task queue with 6 distributed tasks
- Redis caching layer with automatic fallback
- JWT + Bcrypt authentication system
- Docker containerization (6 services)
- Gradio web interface with API integration
- 10 professional documentation files
- Security best practices implemented
- Production-ready architecture"
    if errorlevel 1 (
        color 0C
        echo [ERROR] Failed to create commit!
        pause
        exit /b 1
    )
    color 0A
    echo [✓] Commit created
) else (
    color 0A
    echo [✓] No changes to commit
)
echo.

REM Ensure main branch
echo [*] Setting up main branch...
git branch -M main 2>nul
color 0A
echo [✓] Main branch configured
echo.

REM Check for existing remote
echo [*] Checking GitHub remote...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [*] Adding GitHub remote...
    git remote add origin https://github.com/QusaiALBahri/imageOSINT.git
    if errorlevel 1 (
        color 0C
        echo [ERROR] Failed to add remote!
        pause
        exit /b 1
    )
) else (
    echo [✓] Remote already exists
)
color 0A
echo [✓] GitHub remote configured
echo.

REM Display repository info
echo [*] Repository Information:
git remote -v
echo.

REM Attempt to push
color 0B
echo =========================================
echo      Pushing to GitHub...
echo =========================================
echo.
echo [!] Note: You may be prompted to authenticate
echo [!] If using HTTPS, provide GitHub credentials or Personal Access Token
echo [!] If using SSH, ensure SSH key is added to GitHub
echo.
echo Repository: https://github.com/QusaiALBahri/imageOSINT
echo.

color 0A
git push -u origin main
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] Push failed!
    echo.
    echo [INFO] Troubleshooting:
    echo   1. Check your internet connection
    echo   2. Verify GitHub Repository exists: https://github.com/QusaiALBahri/imageOSINT
    echo   3. Authenticate with GitHub:
    echo      - Using GitHub CLI: run 'gh auth login'
    echo      - Using HTTPS: provide personal access token
    echo      - Using SSH: ensure SSH key is added to GitHub
    echo.
    pause
    exit /b 1
)

color 0A
echo.
echo =========================================
echo      Push Successful!
echo =========================================
echo.
echo [✓] Repository pushed to GitHub
echo [✓] Repository URL: https://github.com/QusaiALBahri/imageOSINT
echo.
echo [*] Next Steps:
echo    1. Visit: https://github.com/QusaiALBahri/imageOSINT
echo    2. Add topics (Settings ^> Topics):
echo       - osint
echo       - image-search
echo       - geolocation
echo       - fastapi
echo       - python
echo       - docker
echo    3. Add description: Enterprise-grade OSINT image analysis platform
echo.
color 02
echo [✓] All Done! Your repository is now on GitHub!
echo.
pause
