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

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🚀 Iniciando Extractor Bancario Web..."
echo "🌐 Abre http://localhost:8000 en tu navegador"
uvicorn app.main:app --reload --port 8000

echo ""
echo "✅ Aplicación cerrada"
