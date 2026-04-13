@echo off
REM Verify ImageOSINT Repository Files
color 0A
echo.
echo ========================================
echo   ImageOSINT - Verification Script
echo ========================================
echo.

cd /d C:\Users\qusai\Downloads\work\python\image_osint

echo [*] Checking if directory exists...
if not exist "." (
    color 0C
    echo [ERROR] Directory not found!
    pause
    exit /b 1
)
color 0A
echo [✓] Directory exists and accessible
echo.

echo [*] Counting files and directories...
for /f %%A in ('dir /b /s 2^>nul ^| find /c "."') do set FILE_COUNT=%%A
echo [✓] Total items: %FILE_COUNT%
echo.

echo [*] Checking for critical files...
echo.

set COUNT=0

if exist "README.md" (
    echo [✓] README.md
    set /a COUNT+=1
) else (
    echo [✗] README.md - MISSING
)

if exist "CONTRIBUTING.md" (
    echo [✓] CONTRIBUTING.md
    set /a COUNT+=1
) else (
    echo [✗] CONTRIBUTING.md - MISSING
)

if exist "SECURITY.md" (
    echo [✓] SECURITY.md
    set /a COUNT+=1
) else (
    echo [✗] SECURITY.md - MISSING
)

if exist "CODE_OF_CONDUCT.md" (
    echo [✓] CODE_OF_CONDUCT.md
    set /a COUNT+=1
) else (
    echo [✗] CODE_OF_CONDUCT.md - MISSING
)

if exist "LICENSE" (
    echo [✓] LICENSE
    set /a COUNT+=1
) else (
    echo [✗] LICENSE - MISSING
)

if exist "CHANGELOG.md" (
    echo [✓] CHANGELOG.md
    set /a COUNT+=1
) else (
    echo [✗] CHANGELOG.md - MISSING
)

if exist "FAQ.md" (
    echo [✓] FAQ.md
    set /a COUNT+=1
) else (
    echo [✗] FAQ.md - MISSING
)

if exist "backend\server.py" (
    echo [✓] backend/server.py
    set /a COUNT+=1
) else (
    echo [✗] backend/server.py - MISSING
)

if exist "database\models.py" (
    echo [✓] database/models.py
    set /a COUNT+=1
) else (
    echo [✗] database/models.py - MISSING
)

if exist "docker-compose.yml" (
    echo [✓] docker-compose.yml
    set /a COUNT+=1
) else (
    echo [✗] docker-compose.yml - MISSING
)

if exist "Dockerfile" (
    echo [✓] Dockerfile
    set /a COUNT+=1
) else (
    echo [✗] Dockerfile - MISSING
)

if exist "requirements-backend.txt" (
    echo [✓] requirements-backend.txt
    set /a COUNT+=1
) else (
    echo [✗] requirements-backend.txt - MISSING
)

if exist ".gitignore" (
    echo [✓] .gitignore
    set /a COUNT+=1
) else (
    echo [✗] .gitignore - MISSING
)

if exist "PUSH_NOW.bat" (
    echo [✓] PUSH_NOW.bat
    set /a COUNT+=1
) else (
    echo [✗] PUSH_NOW.bat - MISSING
)

echo.
echo [*] Critical files found: %COUNT%/14
echo.

if %COUNT%==14 (
    color 0A
    echo [✓✓✓] ALL FILES ARE PRESENT AND READY TO PUSH!
    echo.
    echo [*] To push to GitHub, run:
    echo.
    echo    PUSH_NOW.bat
    echo.
    echo    or double-click the file in Windows Explorer
    echo.
) else (
    color 0E
    echo [!] Some files are missing
)

echo.
echo [*] Current directory: %CD%
echo.
dir /b | head -20
echo.

pause
