@echo off
title Actualizando Portal de Alta Forthing...
echo.
echo ================================================
echo   PORTAL DE ALTA - Actualizacion automatica
echo ================================================
echo.
echo Subiendo cambios a GitHub...
cd /d "%~dp0"
"C:\Program Files\Git\bin\git.exe" add .
"C:\Program Files\Git\bin\git.exe" commit -m "Actualizacion automatica %date% %time%"
"C:\Program Files\Git\bin\git.exe" push
echo.
echo ================================================
echo  Listo! Railway actualizara el sistema en ~2 min
echo  Revisa tu panel de control de Railway para ver la URL publica.
echo ================================================
echo.
pause
