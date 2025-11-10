@echo off
echo ========================================
echo   URGENT FIX - Removing Database Code
echo ========================================
echo.

git add .
git commit -m "Fix: Remove database dependencies for deployment"
git push origin main

echo.
echo ========================================
echo DONE! App will redeploy in 2-3 minutes
echo.
echo Your app will be live at:
echo https://sachinkumar270702-adsnap-studio-ayyxuecxj8c3put2ojgrqj.streamlit.app
echo ========================================
pause
