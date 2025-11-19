#!/bin/zsh

cd "/Users/sebas/Desktop/Python/App gastos" || exit 1

if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

# Ejecutar la app (intenta python3 y luego python)
if command -v python3 >/dev/null 2>&1; then
  exec python3 app_moderna.py
else
  exec python app_moderna.py
fi


