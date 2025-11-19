@echo off
echo ==============================
echo   Cleaning temporary files...
echo ==============================
echo.

:: Delete Windows temp files
del /s /f /q %temp%\*.*
rd /s /q %temp%

:: Delete Prefetch files
del /s /f /q C:\Windows\Prefetch\*.*

:: Delete Windows temp folder
del /s /f /q C:\Windows\Temp\*.*

:: Clear recycle bin
rd /s /q C:\$Recycle.Bin

echo.
echo ==============================
echo   Cleaning finished!
echo ==============================
pause
