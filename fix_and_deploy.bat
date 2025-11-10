@echo off
echo ========================================
echo   Fixing and Redeploying AdSnap Studio
echo ========================================
echo.

echo Staging all changes...
git add .

echo.
echo Committing fixes...
git commit -m "Fix deployment: remove unused dependencies and database imports"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Done! Streamlit Cloud will auto-redeploy
echo.
echo Check your app at:
echo https://sachinkumar270702-adsnap-studio-ayyxuecxj8c3put2ojgrqj.streamlit.app
echo.
echo Wait 2-3 minutes for deployment to complete
echo ========================================
echo.

pause
