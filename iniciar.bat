@echo off
setlocal EnableExtensions

cd /d "%~dp0"

title Inicio - Sistema de Gestion de Laboratorio

echo ============================================================
echo   INICIO DEL SISTEMA DE GESTION DE LABORATORIO
echo ============================================================
echo.

if not exist "app.py" (
    echo [ERROR] No se encontro app.py en esta carpeta.
    echo.
    echo Coloca iniciar.bat dentro de la carpeta principal del proyecto.
    echo.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual venv.
    echo.
    echo Primero ejecuta instalar.bat para preparar el sistema.
    echo.
    pause
    exit /b 1
)

echo [INFO] Iniciando servidor local...
echo.
echo Cuando el sistema termine de iniciar, abre el navegador en:
echo http://127.0.0.1:5000
echo.
echo Para detener el sistema, regresa a esta ventana y presiona CTRL + C.
echo.

start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

"venv\Scripts\python.exe" app.py

echo.
echo [INFO] El servidor se ha detenido.
echo.
pause
exit /b 0
