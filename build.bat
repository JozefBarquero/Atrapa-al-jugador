@echo off
title Empaquetador Atrapa al Jugador (Windows)
color 0B
echo ===================================================
echo   Iniciando proceso de empaquetado para Windows
echo ===================================================
echo.

:: 1. Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta agregado al PATH.
    pause
    exit /b
)

:: 2. Crear y activar entorno virtual
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
)
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

:: 3. Instalar dependencias y PyInstaller
echo.
echo Instalando dependencias del proyecto y PyInstaller...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

:: 4. Limpiar compilaciones anteriores
echo.
echo Limpiando archivos temporales anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Atrapa-Al-Jugador-WINDOWS.spec" del /q "Atrapa-Al-Jugador-WINDOWS.spec"

:: 5. Empaquetar con PyInstaller
echo.
echo Empaquetando el juego (esto puede tardar un momento)...
echo Por favor espera...


set "GTK_PATH=C:\Program Files\GTK3-Runtime Win64\bin"
set "PATH=%GTK_PATH%;%PATH%"


pyinstaller --noconfirm --clean --onefile --windowed ^
    --name "Atrapa-Al-Jugador-WINDOWS" ^
    --add-data "assets;assets" ^
    --collect-all cairosvg ^
    main.py

:: 6. Comprobar resultado
echo.
if exist "dist\Atrapa-Al-Jugador-WINDOWS.exe" (
    color 0A
    echo ===================================================
    echo   ¡Empaquetado completado con exito!
    echo ===================================================
    echo.
    echo Tu ejecutable esta en: dist\Atrapa-Al-Jugador-WINDOWS.exe
) else (
    color 0C
    echo [ERROR] Hubo un problema durante el empaquetado.
    echo Revisa los mensajes anteriores para encontrar el fallo.
)

echo.
pause