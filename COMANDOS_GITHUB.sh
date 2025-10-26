#!/bin/bash
# 🚀 Comandos para subir a GitHub - SebastianZuluaga

echo "🎯 PASO 1: Crear repositorio en GitHub"
echo "======================================"
echo ""
echo "Ve a: https://github.com/new"
echo ""
echo "Configuración:"
echo "  - Repository name: extractor-bancario-ia"
echo "  - Description: 🤖 Extractor de extractos bancarios con IA usando Gemini 2.0 Flash"
echo "  - Visibility: Public (o Private si prefieres)"
echo "  - ⚠️  NO marques: README, .gitignore, License"
echo ""
echo "Presiona Enter cuando hayas creado el repositorio..."
read

echo ""
echo "🔗 PASO 2: Conectar y subir el código"
echo "======================================"
echo ""

cd "/Users/sebas/Desktop/Python/App gastos"

# Verificar que estamos en el directorio correcto
if [ ! -d ".git" ]; then
    echo "❌ Error: No estás en el directorio del proyecto"
    exit 1
fi

# Agregar remote
echo "📡 Conectando con GitHub..."
git remote add origin https://github.com/SebastianZuluaga/extractor-bancario-ia.git

# Verificar rama
echo "🌿 Verificando rama main..."
git branch -M main

# Mostrar estado
echo ""
echo "📊 Estado del repositorio:"
git log --oneline -3
echo ""

echo "🚀 PASO 3: Subir el código"
echo "======================================"
echo ""
echo "Ejecutando: git push -u origin main"
echo ""
echo "GitHub te pedirá credenciales:"
echo "  - Username: SebastianZuluaga"
echo "  - Password: [Usa un Personal Access Token]"
echo ""
echo "Para obtener tu token: https://github.com/settings/tokens"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡ÉXITO! Proyecto subido a GitHub"
    echo ""
    echo "🌐 Tu repositorio está en:"
    echo "   https://github.com/SebastianZuluaga/extractor-bancario-ia"
    echo ""
    echo "🎉 Próximos pasos sugeridos:"
    echo "   1. Agregar Topics: python, gemini, ai, pdf-extractor"
    echo "   2. Agregar screenshot de la UI"
    echo "   3. Invitar colaboradores si quieres"
else
    echo ""
    echo "❌ Error al subir. Posibles soluciones:"
    echo ""
    echo "1. Si dice 'remote origin already exists':"
    echo "   git remote remove origin"
    echo "   git remote add origin https://github.com/SebastianZuluaga/extractor-bancario-ia.git"
    echo ""
    echo "2. Si es problema de autenticación:"
    echo "   - Obtén un token en: https://github.com/settings/tokens"
    echo "   - O instala GitHub CLI: brew install gh && gh auth login"
    echo ""
    echo "3. Si necesitas ayuda, revisa: GUIA_GITHUB.md"
fi

