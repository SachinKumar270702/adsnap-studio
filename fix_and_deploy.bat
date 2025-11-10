@echo off
echo ========================================
echo   Final Fix - AdSnap Studio Deployment
echo ========================================
echo.

echo Staging all changes...
git add .

echo.
echo Committing fixes...
git commit -m "Fix: Use Python 3.11 and update package versions for compatibility"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Done! Streamlit Cloud will auto-redeploy
echo.
echo This fix includes:
echo - Python 3.11 (instead of 3.13)
echo - Updated numpy to 1.26+ (compatible)
echo - Updated Pillow to 10.3+ (compatible)
echo - Flexible version constraints
echo.
echo Check your app at:
echo https://sachinkumar270702-adsnap-studio-ayyxuecxj8c3put2ojgrqj.streamlit.app
echo.
echo Wait 2-3 minutes for deployment to complete
echo ========================================
echo.

pause
