@echo off
setlocal EnableExtensions

cd /d "%~dp0"

title Instalacion - Sistema de Gestion de Laboratorio

echo ============================================================
echo   INSTALACION DEL SISTEMA DE GESTION DE LABORATORIO
echo ============================================================
echo.

if not exist "app.py" (
    echo [ERROR] No se encontro app.py en esta carpeta.
    echo.
    echo Coloca este archivo instalar.bat dentro de la carpeta principal del proyecto,
    echo en el mismo nivel donde estan app.py, requirements.txt, static y templates.
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo [ERROR] No se encontro requirements.txt.
    echo.
    echo El archivo requirements.txt es necesario para instalar las dependencias.
    echo.
    pause
    exit /b 1
)

set "PYTHON_CMD="

call :probar_python "py -3"
if defined PYTHON_CMD goto python_encontrado

call :probar_python "py"
if defined PYTHON_CMD goto python_encontrado

call :probar_python "python"
if defined PYTHON_CMD goto python_encontrado

echo [ERROR] No se encontro Python 3.10 o superior.
echo.
echo Instala Python desde:
echo https://www.python.org/downloads/
echo.
echo IMPORTANTE: durante la instalacion marca la opcion:
echo "Add Python to PATH"
echo.
echo Luego cierra esta ventana, abre una nueva y vuelve a ejecutar instalar.bat.
echo.
pause
exit /b 1

:python_encontrado
echo [OK] Python compatible encontrado: %PYTHON_CMD%
echo.

if exist "venv\Scripts\python.exe" (
    echo [INFO] Ya existe un entorno virtual en la carpeta venv.
    echo [INFO] Se reutilizara el entorno existente.
) else (
    echo [INFO] Creando entorno virtual...
    %PYTHON_CMD% -m venv venv

    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo crear el entorno virtual.
        echo.
        echo Posibles causas:
        echo - Python no esta instalado correctamente.
        echo - La instalacion de Python no incluye venv.
        echo - La carpeta del proyecto no tiene permisos de escritura.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Verificando pip dentro del entorno virtual...
"venv\Scripts\python.exe" -m ensurepip --upgrade >nul 2>&1

"venv\Scripts\python.exe" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip no esta disponible dentro del entorno virtual.
    echo.
    echo Intenta reinstalar Python y asegurate de incluir pip durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo [OK] pip disponible.
echo.

echo [INFO] Actualizando pip...
"venv\Scripts\python.exe" -m pip install --upgrade pip

if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] No se pudo actualizar pip, pero se intentara continuar.
    echo.
)

echo.
echo [INFO] Instalando dependencias desde requirements.txt...
"venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudieron instalar las dependencias.
    echo.
    echo Posibles causas:
    echo - No hay conexion a internet.
    echo - requirements.txt esta incompleto o danado.
    echo - La version de Python no es compatible.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   INSTALACION COMPLETADA CORRECTAMENTE
echo ============================================================
echo.
echo Para iniciar el sistema, ejecuta:
echo iniciar.bat
echo.
pause
exit /b 0

:probar_python
set "CANDIDATO=%~1"
%CANDIDATO% -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=%CANDIDATO%"
)
exit /b 0
