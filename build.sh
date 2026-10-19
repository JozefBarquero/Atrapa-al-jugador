#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' 

echo -e "${BLUE}=== Iniciando proceso de empaquetado para Linux ===${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 no está instalado. Por favor, instálalo primero.${NC}"
    exit 1
fi


if [ ! -d ".venv" ]; then
    echo -e "${BLUE}Creando entorno virtual...${NC}"
    python3 -m venv .venv
fi
source .venv/bin/activate


echo -e "${BLUE}Instalando dependencias del proyecto y PyInstaller...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller


echo -e "${BLUE}Limpiando archivos temporales anteriores...${NC}"
rm -rf build dist Atrapa-Al-Estudiante-LINUX.spec


echo -e "${BLUE}Empaquetando el juego (esto puede tardar un momento)...${NC}"

pyinstaller --noconfirm --clean --onefile --windowed \
    --name "Atrapa-Al-Estudiante-LINUX" \
    --add-data "assets:assets" \
    main.py


if [ -f "dist/Atrapa-Al-Estudiante-LINUX" ]; then
    echo -e "${GREEN}=== ¡Empaquetado completado con éxito! ===${NC}"
    echo -e "Puedes encontrar tu ejecutable en: ${GREEN}dist/Atrapa-Al-Estudiante-LINUX${NC}"
    echo -e "Puedes copiar este archivo a cualquier otra PC con Linux y ejecutarlo dando doble clic."
    
    chmod +x dist/Atrapa-Al-Estudiante-LINUX
else
    echo -e "${RED}Hubo un error durante el empaquetado.${NC}"
fi