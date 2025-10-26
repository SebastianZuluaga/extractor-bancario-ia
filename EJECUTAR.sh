#!/bin/bash

# 🚀 Extractor de Extractos Bancarios con IA
# Script de ejecución rápida

clear

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║        🤖  EXTRACTOR DE EXTRACTOS BANCARIOS IA           ║"
echo "║                                                           ║"
echo "║              Interfaz Moderna • Dark Mode                 ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "🔄 Iniciando aplicación..."
echo ""

cd "$(dirname "$0")"

# Activar entorno virtual
source venv/bin/activate

# Ejecutar app moderna
python3 app_moderna.py

echo ""
echo "✅ Aplicación cerrada"
