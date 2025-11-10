@echo off
echo ========================================
echo   AdSnap Studio - Deployment Helper
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit - AdSnap Studio"
    git branch -M main
    echo Git repository initialized!
) else (
    echo Git repository already exists.
)

echo.
echo Choose deployment option:
echo 1. Commit and push to GitHub
echo 2. Run locally for testing
echo 3. Build Docker image
echo 4. View deployment guide
echo.

set /p choice="Enter option (1-4): "

if "%choice%"=="1" (
    echo.
    set /p repo="Enter GitHub repository URL: "
    git remote add origin %repo% 2>nul || git remote set-url origin %repo%
    git add .
    set /p msg="Enter commit message: "
    git commit -m "%msg%"
    git push -u origin main
    echo.
    echo ========================================
    echo Code pushed to GitHub!
    echo.
    echo Next steps:
    echo 1. Go to https://share.streamlit.io/
    echo 2. Click 'New app'
    echo 3. Select your repository
    echo 4. Set main file: app.py
    echo 5. Add BRIA_API_KEY in secrets
    echo 6. Click Deploy!
    echo ========================================
)

if "%choice%"=="2" (
    echo.
    echo Starting local server...
    streamlit run app.py
)

if "%choice%"=="3" (
    echo.
    echo Building Docker image...
    docker build -t adsnap-studio .
    echo.
    echo Docker image built!
    echo Run with: docker run -p 8501:8501 -e BRIA_API_KEY=your_key adsnap-studio
)

if "%choice%"=="4" (
    echo.
    echo Opening deployment guide...
    start QUICKSTART_DEPLOY.md
)

echo.
echo Done!
pause
