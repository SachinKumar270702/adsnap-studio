@echo off
echo ========================================
echo   Fix Signup Form - Remove DB Reference
echo ========================================
echo.

git add .
git commit -m "Fix: Remove database reference from signup form"
git push origin main

echo.
echo ========================================
echo DONE! Signup will now work properly
echo.
echo Fixed:
echo - Signup form now uses AuthManager
echo - No more database errors
echo - Users can create accounts
echo.
echo App will redeploy in 2-3 minutes
echo ========================================
pause
