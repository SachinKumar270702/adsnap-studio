@echo off
echo ========================================
echo   Making Welcome Dashboard Buttons Work
echo ========================================
echo.

git add .
git commit -m "Fix: Make welcome dashboard feature buttons navigate to correct pages"
git push origin main

echo.
echo ========================================
echo DONE! Buttons will now work properly
echo.
echo The buttons will now:
echo - Start Creating -^> Generate Image page
echo - Try Now -^> Lifestyle Shot page  
echo - Explore -^> Image Editing page
echo.
echo App will redeploy in 2-3 minutes
echo ========================================
pause
