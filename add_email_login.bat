@echo off
echo ========================================
echo   Add Email Login Support
echo ========================================
echo.

git add .
git commit -m "Feature: Allow login with username or email"
git push origin main

echo.
echo ========================================
echo DONE! Users can now login with email
echo.
echo New Features:
echo - Login with username OR email
echo - Automatic detection of input type
echo - Updated UI label to show both options
echo.
echo App will redeploy in 2-3 minutes
echo ========================================
pause
