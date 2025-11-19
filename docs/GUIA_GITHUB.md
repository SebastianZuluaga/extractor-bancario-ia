# 📤 Guía para Subir a GitHub

## ✅ Estado Actual

Tu proyecto ya está preparado y listo para GitHub:
- ✅ Git inicializado
- ✅ Commit inicial realizado
- ✅ `.gitignore` configurado (protege PDFs, Excel, credenciales)
- ✅ LICENSE MIT agregada
- ✅ README completo y profesional

---

## 🚀 Pasos para Subir a GitHub

### 1️⃣ Crear Repositorio en GitHub

1. Ve a: https://github.com/new
2. Completa:
   - **Repository name:** `extractor-bancario-ia` (o el nombre que prefieras)
   - **Description:** "🤖 Extractor de extractos bancarios con IA usando Gemini 2.0 Flash"
   - **Visibility:** Elige `Public` o `Private`
   - ⚠️ **NO marques** "Add a README file" (ya lo tienes)
   - ⚠️ **NO marques** "Add .gitignore" (ya lo tienes)
   - ⚠️ **NO marques** "Choose a license" (ya lo tienes)
3. Click en **"Create repository"**

---

### 2️⃣ Conectar tu Repositorio Local con GitHub

Después de crear el repo, GitHub te mostrará comandos. Usa estos:

```bash
cd "/Users/sebas/Desktop/Python/App gastos"

# Conectar con GitHub (reemplaza TU_USUARIO con tu nombre de usuario)
git remote add origin https://github.com/TU_USUARIO/extractor-bancario-ia.git

# Renombrar rama a main (si es necesario)
git branch -M main

# Subir el código
git push -u origin main
```

**Ejemplo real:**
```bash
# Si tu usuario es "sebas123"
git remote add origin https://github.com/sebas123/extractor-bancario-ia.git
git branch -M main
git push -u origin main
```

---

### 3️⃣ Autenticación

GitHub te pedirá autenticarte. Tienes dos opciones:

#### Opción A: Personal Access Token (Recomendado)

1. Ve a: https://github.com/settings/tokens
2. Click en **"Generate new token (classic)"**
3. Selecciona:
   - `repo` (acceso completo a repositorios)
   - Expiration: 90 días o más
4. Copia el token
5. Cuando hagas `git push`, usa:
   - **Username:** tu usuario de GitHub
   - **Password:** el token (NO tu contraseña normal)

#### Opción B: GitHub CLI (Más fácil)

```bash
# Instalar GitHub CLI
brew install gh

# Autenticarte
gh auth login

# Ahora puedes hacer push sin problemas
git push -u origin main
```

---

### 4️⃣ Verificar que Subió Correctamente

1. Ve a: `https://github.com/TU_USUARIO/extractor-bancario-ia`
2. Deberías ver:
   - ✅ README bonito con badges
   - ✅ 8 archivos
   - ✅ NO PDFs ni Excel (protegidos por .gitignore)
   - ✅ Tu commit inicial

---

## 🔒 Seguridad: ¿Qué NO se sube?

Tu `.gitignore` protege información sensible:

```
❌ *.pdf                    # Tus extractos bancarios
❌ *.xlsx                   # Excel generado
❌ venv/                    # Entorno virtual
❌ config.enc, *.key        # Configuración encriptada
❌ .DS_Store                # Archivos de macOS
❌ __pycache__/             # Cache de Python
```

**Solo se suben:**
✅ Código fuente (.py)
✅ Documentación (README, LICENSE)
✅ Dependencias (requirements.txt)
✅ Script de ejecución (EJECUTAR.sh)

---

## 📝 Configurar Git (Recomendado)

Antes de tu primer push, configura tu identidad:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu_email@ejemplo.com"
```

---

## 🔄 Actualizaciones Futuras

Cuando hagas cambios al proyecto:

```bash
# Ver cambios
git status

# Agregar archivos modificados
git add .

# Hacer commit
git commit -m "Descripción de los cambios"

# Subir a GitHub
git push
```

---

## 🎨 Mejorar el README en GitHub

Una vez subido, considera agregar:

1. **Screenshot de la UI:**
   - Toma captura de la aplicación
   - Súbela a GitHub en un issue
   - Copia la URL de la imagen
   - Agrégala al README:
   ```markdown
   ![Screenshot](URL_DE_LA_IMAGEN)
   ```

2. **Demo GIF:**
   - Usa QuickTime para grabar la pantalla
   - Convierte a GIF con https://ezgif.com
   - Agrega al README

3. **Badges adicionales:**
   ```markdown
   ![Stars](https://img.shields.io/github/stars/TU_USUARIO/extractor-bancario-ia)
   ![Forks](https://img.shields.io/github/forks/TU_USUARIO/extractor-bancario-ia)
   ```

---

## 🏷️ Agregar Topics en GitHub

En tu repo de GitHub:
1. Click en el ⚙️ (Settings del repo)
2. En "Topics" agrega:
   - `python`
   - `gemini`
   - `ai`
   - `pdf-extractor`
   - `banking`
   - `tkinter`
   - `excel`
   - `automation`

---

## ❓ Problemas Comunes

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/extractor-bancario-ia.git
```

### Error: "failed to push some refs"
```bash
git pull origin main --rebase
git push -u origin main
```

### Error: "Permission denied"
- Verifica tu autenticación (token o GitHub CLI)
- Asegúrate de que el repo existe en GitHub

---

## 🎉 ¡Listo!

Una vez subido, tu repositorio será:
- ✅ Público/Privado según tu elección
- ✅ Con documentación profesional
- ✅ Seguro (sin datos sensibles)
- ✅ Listo para compartir o colaborar

**Tu repo estará en:**
`https://github.com/TU_USUARIO/extractor-bancario-ia`

---

## 🌟 Siguiente Nivel

Considera:
- 📊 Agregar GitHub Actions (CI/CD)
- 📈 Configurar GitHub Pages para documentación
- 🏆 Publicar en PyPI como paquete
- 💬 Habilitar Discussions para comunidad
- 🐛 Configurar Issue Templates

