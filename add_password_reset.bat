@echo off
echo ========================================
echo   Adding Password Reset Feature
echo ========================================
echo.

git add .
git commit -m "Feature: Add password reset via email with Gmail integration"
git push origin main

echo.
echo ========================================
echo DONE! Password reset feature added
echo.
echo New Features:
echo - Forgot Password button on login
echo - Email-based password reset
echo - Secure token system
echo - Beautiful HTML emails
echo - 1-hour token expiration
echo.
echo Next Steps:
echo 1. Add Gmail credentials to Streamlit secrets
echo 2. See EMAIL_SETUP.md for instructions
echo.
echo App will redeploy in 2-3 minutes
echo ========================================
pause
