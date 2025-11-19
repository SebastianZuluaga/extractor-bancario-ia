# 🤖 Extractor de Extractos Bancarios con IA

Aplicación moderna con interfaz gráfica para extraer y procesar extractos bancarios PDF usando **Inteligencia Artificial (Gemini 2.0 Flash)**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-cyan)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Linux%20|%20Windows-lightgrey)

---

## ✨ Características

### 🎨 **Interfaz Moderna**
- ✅ Diseño **Dark Mode** minimalista
- ✅ Colores modernos (Cyan + Verde neón)
- ✅ Efectos hover y animaciones
- ✅ Tipografía SF Pro (macOS style)
- ✅ Responsive y centrada

### 🤖 **Inteligencia Artificial**
- ✅ **Gemini 2.0 Flash** (100% Gratuito)
- ✅ Procesamiento página por página
- ✅ Extracción inteligente de tablas
- ✅ Ignora publicidad y encabezados
- ✅ Estructura datos automáticamente

### 🔐 **Seguridad**
- ✅ **Cifrado AES-256** con rotación de claves
- ✅ Uso automático del llavero del sistema (macOS/Windows/Linux compatibles)
- ✅ Permisos reforzados en disco (700/600)
- ✅ Log seguro con rotación y acceso rápido desde la interfaz
- ✅ No sale de tu computadora

### 📊 **Procesamiento**
- ✅ **3 bancos soportados**: Nu, Rappi/Davivienda, Bancolombia
- ✅ PDFs protegidos con contraseña
- ✅ Valores convertidos a números
- ✅ Excel con múltiples hojas
- ✅ Total: **278 transacciones** extraídas

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
2. Inicia sesión con Google
3. Click en "Create API Key"
4. Copia la clave

### 5. Dar permisos de ejecución (macOS/Linux)

```bash
chmod +x EJECUTAR.sh
```

---

## 💻 Uso

### Opción 1: Script ejecutable

```bash
./EJECUTAR.sh
```

### Opción 2: Comando directo

```bash
source venv/bin/activate
python3 app_moderna.py
```

### Opción 3: API HTTP con Docker (recomendada para compartir)

Requiere Docker instalado.

```bash
# Construir imagen
docker build -t extractor-ia .

# Ejecutar (la API queda en http://localhost:8000)
docker run --rm -p 8000:8000 \
  -e GEMINI_API_KEY="tu_api_key" \
  extractor-ia

# Probar salud
curl http://localhost:8000/salud

# Procesar PDFs (múltiples -F files=@...)
curl -X POST "http://localhost:8000/procesar" \
  -F "files=@/ruta/a/tu1.pdf" \
  -F "files=@/ruta/a/tu2.pdf" \
  -F "password=CONTRASEÑA_O_VACIO" \
  --output Extractos_Consolidados.xlsx
```

Notas:
- Puedes definir `GEMINI_API_KEY` como variable de entorno para no enviarla en el request.
- El nombre del archivo de salida incluye timestamp para evitar sobrescritura.

### Opción 4: Doble click

Hacer doble click en `EJECUTAR.sh` desde Finder

---

## 📖 Guía de Uso

### **Primera Vez:**

1. Ejecutar la aplicación
2. Ingresar API Key de Gemini
3. Ingresar contraseña de PDFs
4. Seleccionar carpeta con PDFs
5. Click en **"💾 Guardar Configuración"**
6. Click en **"🚀 PROCESAR EXTRACTOS"**

### **Próximas Veces:**

1. Ejecutar la aplicación (configuración ya cargada)
2. Click en **"🚀 PROCESAR EXTRACTOS"**
3. ¡Listo!

### Opción 5: API con Docker Compose

```bash
# 1) Crear archivo .env (no se sube al repo)
echo "GEMINI_API_KEY=TU_API_KEY" > .env

# 2) Levantar la API
docker compose up -d --build

# 3) Probar salud
curl http://localhost:8000/salud

# 4) Procesar PDFs
curl -X POST "http://localhost:8000/procesar" \
  -F "files=@/ruta/a/tu1.pdf" \
  -F "files=@/ruta/a/tu2.pdf" \
  -F "password=CONTRASEÑA_O_VACIO" \
  --output Extractos_Consolidados.xlsx

# 5) Apagar
docker compose down
```

### **Editar Configuración:**

1. Click en **"✏️ Editar"**
2. Modificar campos necesarios
3. Click en **"💾 Guardar Configuración"**

---

## 📁 Estructura del Proyecto

```
extractor-bancario-ia/
├── 🌙 app_moderna.py              # UI Moderna (Archivo principal)
├── 🔐 config_segura.py            # Módulo de encriptación
├── 🤖 procesador_gemini.py        # Procesador con IA
├── 📋 requirements.txt            # Dependencias Python
├── 🚀 EJECUTAR.sh                 # Script de ejecución
├── 📄 README.md                   # Esta guía
└── .gitignore                     # Archivos excluidos de Git
```

**Nota:** Los PDFs de usuario y Excel generados están excluidos de Git por seguridad (.gitignore).

---

## 🔒 Seguridad

### **¿Dónde se guardan las credenciales?**

```
~/.extractor_bancario/
├── config.enc   ← Configuración cifrada (AES-256)
├── key.key      ← Solo si el llavero del sistema no está disponible
└── extractor.log← Historial de actividad con rotación automática
```

### **¿Es seguro?**

- ✅ **Cifrado nivel bancario** (AES-256) con rotación desde la UI
- ✅ **Llavero del sistema** como almacén primario cuando existe
- ✅ **Permisos estrictos** en archivos sensibles (solo tu usuario)
- ✅ **Logs auditables** sin exponer credenciales
- ✅ **100% local** (no se envía a internet)
- ✅ **No reversible** sin tu usuario

---

## 📊 Excel Generado

### **Formato de Salida:**

```
Extractos_Consolidados.xlsx
├── Hoja 1: Nu_2025-11-03 (39 transacciones)
│   ├── fecha
│   ├── descripcion
│   ├── valor (número)
│   ├── cuotas
│   ├── valor_del_mes (número)
│   ├── interes_mes (número)
│   ├── total_pagar (número)
│   └── restante (número)
│
├── Hoja 2: Rappi/Davivienda (31 transacciones)
│   ├── tarjeta
│   ├── fecha
│   ├── descripcion
│   ├── valor_transaccion (número)
│   ├── capital_facturado (número)
│   ├── cuotas
│   ├── capital_pendiente (número)
│   ├── tasa_mv (número)
│   └── tasa_ea (número)
│
└── Hoja 3: Bancolombia (208 transacciones)
    ├── fecha
    ├── descripcion
    ├── sucursal
    ├── dcto
    ├── valor (número)
    └── saldo (número)
```

### **Valores Numéricos:**

Todos los valores monetarios están convertidos a **números** (float64) para que puedas:
- ✅ Sumar directamente en Excel
- ✅ Crear gráficos
- ✅ Aplicar fórmulas
- ✅ Análisis de datos

---

## 🛠️ Dependencias

```
pandas >= 2.2.0          # Manejo de datos
openpyxl >= 3.1.2        # Excel
pikepdf >= 9.0.0         # Desbloqueo PDFs
pymupdf >= 1.26.0        # Conversión PDF → Imagen
google-generativeai      # Gemini AI
cryptography >= 46.0.0   # Encriptación
Pillow >= 10.1.0         # Procesamiento imágenes
```

---

## 🎯 Atajos de Teclado

- **Cmd+V** (macOS) / **Ctrl+V** (Windows): Pegar en campos
- **Enter**: Ejecutar acción del botón enfocado
- **Tab**: Navegar entre campos

---

## 🔄 Próximas Funcionalidades

- [ ] 📊 Análisis automático de gastos
- [ ] 💰 Integración con Excel de sueldos
- [ ] 🧾 Cálculo de impuestos
- [ ] 📈 Comparación ingresos vs gastos
- [ ] 📅 Reportes mensuales/anuales
- [ ] 🎯 Categorización automática
- [ ] 💾 Exportar a otros formatos

---

## ❓ Preguntas Frecuentes

### **¿Es realmente gratis?**
✅ Sí, 100%. Gemini 2.0 Flash tiene un tier gratuito generoso (15 requests/min, 1,500/día).

### **¿Necesito internet?**
✅ Solo para procesar con Gemini. La configuración es local y offline.

### **¿Mis datos salen de mi computadora?**
⚠️ Solo los PDFs se envían a Gemini para procesamiento. Las credenciales NUNCA salen.

### **¿Puedo usar en Windows/Linux?**
✅ Sí, el código es multiplataforma. Solo cambia `EJECUTAR.sh` por `EJECUTAR.bat` (Windows).

### **¿Qué pasa si cambio de computadora?**
⚠️ Deberás ingresar la configuración nuevamente (está encriptada para este equipo).

---

## 🤝 Contribuir

¿Quieres mejorar el proyecto? ¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📧 Soporte

Si encuentras algún problema:

1. Verifica que tengas Python 3.10+
2. Revisa que el entorno virtual esté activado
3. Confirma que tengas todas las dependencias instaladas
4. Verifica tu API Key de Gemini
5. Abre un issue en GitHub con detalles del problema

---

## 📄 Licencia

MIT License - Libre para uso personal y comercial

---

## 🙏 Créditos

- **IA**: Google Gemini 2.0 Flash
- **UI**: Diseño custom con Tkinter
- **Encriptación**: cryptography (Fernet)
- **PDF Processing**: PyMuPDF + pikepdf

---

**Hecho con Cursor usando Python 3.13 y Gemini AI**
