# 🤖 Extractor de Extractos Bancarios con IA

Aplicación web moderna para extraer, procesar y visualizar extractos bancarios PDF usando **Inteligencia Artificial (Gemini 2.0 Flash)**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-cyan)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Linux%20|%20Windows-lightgrey)

---

## ✨ Características

### 🎨 **Nueva Interfaz Web (Desktop First)**
- ✅ **Dashboard Completo**: Visualiza balance, ingresos, gastos y metas en una sola pantalla.
- ✅ **Diseño Neon Dark**: Estética moderna y profesional.
- ✅ **Gráficos Interactivos**: Doughnut charts para desglose de gastos (Chart.js).
- ✅ **Metas Dinámicas**: Crea y sigue tus propios objetivos de ahorro.
- ✅ **Sidebar Navigation**: Navegación fluida entre Dashboard, Carga de Datos y Metas.

### 🤖 **Inteligencia Artificial Avanzada**
- ✅ **Gemini 2.0 Flash**: Análisis rápido y preciso.
- ✅ **Analista Financiero**: Recibe consejos accionables y detección de "gastos hormiga".
- ✅ **Procesamiento Paralelo**: Carga múltiples PDFs y procésalos simultáneamente.
- ✅ **Clasificación Inteligente**: Categorización automática de transacciones.

### 🔐 **Seguridad y Privacidad**
- ✅ **Procesamiento Local**: Tu data se procesa en memoria y se guarda localmente.
- ✅ **API Key Segura**: Tu llave de Gemini se guarda en tu navegador (localStorage).
- ✅ **Sin Base de Datos Externa**: Todo queda en tu máquina.

### 📊 **Soporte Multi-Banco**
- ✅ **Bancos Soportados**: Nu, Rappi/Davivienda, Bancolombia.
- ✅ **PDFs Encriptados**: Soporte para archivos con contraseña.
- ✅ **Excel Consolidado**: Genera un reporte detallado en Excel.

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/SebastianZuluaga/extractor-bancario-ia.git
cd extractor-bancario-ia
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Obtener API Key de Gemini (GRATIS)

1. Ve a: https://makersuite.google.com/app/apikey
2. Crea una clave gratuita.

---

## 💻 Uso

### 1. Iniciar la Aplicación

```bash
uvicorn app.main:app --reload
```

### 2. Abrir en el Navegador

Ve a: [http://localhost:8000](http://localhost:8000)

### 3. Flujo de Trabajo

1.  **Cargar Datos**: Arrastra tus PDFs al área de carga.
2.  **Credenciales**: Ingresa tu Gemini API Key (se guarda para la próxima) y la contraseña del PDF si la tiene.
3.  **Procesar**: Click en "Process Statements".
4.  **Analizar**: Revisa el Dashboard con tus gráficas, balance y recomendaciones de IA.

---

## 📁 Estructura del Proyecto

```
extractor-bancario-ia/
├── app/
│   ├── main.py              # Backend FastAPI
│   ├── core/                # Configuración y Logs
│   ├── services/            # Lógica de IA (Gemini)
│   └── static/              # Frontend (HTML, CSS, JS)
├── data/                    # Carpeta para PDFs y Excel (ignorada por git)
├── scripts/                 # Scripts de utilidad
├── requirements.txt         # Dependencias
└── README.md                # Documentación
```

---

## 🛠️ Tecnologías

-   **Backend**: FastAPI, Python 3.10+
-   **Frontend**: HTML5, CSS3 (Variables), JavaScript (Vanilla), Chart.js
-   **IA**: Google Gemini 2.0 Flash
-   **Procesamiento PDF**: PyMuPDF, PikePDF
-   **Data**: Pandas, OpenPyXL

---

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

---

**Hecho con ❤️ y mucha IA**
