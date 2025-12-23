# 📤 INSTRUCCIONES: CÓMO SUBIR A GITHUB

## 🎯 Objetivo
Subir el repositorio CRM Standalone a GitHub para que tu amiga pueda clonarlo.

## ✅ Estado Actual

El repositorio LOCAL está listo:
```
C:\Users\Usuario\Downloads\SyntexIA-CRM-Standalone\
```

Con 2 commits iniciales:
- Commit 1: Initial commit con todo el código
- Commit 2: Integration guide

## 📋 PASOS PARA SUBIRLO A GITHUB

### PASO 1️⃣: Crear Repositorio en GitHub

1. **Ir a** https://github.com/new

2. **Rellenar el formulario:**
   - Repository name: `SyntexIA-CRM-Standalone`
   - Description: `Independent CRM system built with FastAPI, Pydantic v2, and SQLite`
   - Public (para que otros lo clonem)
   - ⚠️ **NO** seleccionar "Add a README" (ya lo tenemos)

3. **Click en "Create repository"**

4. **Copiar la URL que aparece**, será algo como:
   ```
   https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git
   ```

### PASO 2️⃣: Conectar Local con GitHub

**Ejecuta esto en PowerShell:**

```powershell
cd "C:\Users\Usuario\Downloads\SyntexIA-CRM-Standalone"

# Agregar remote origin
git remote add origin https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git

# Cambiar rama a main
git branch -M main

# Pushear a GitHub
git push -u origin main
```

**Ejemplo real:**
```powershell
cd "C:\Users\Usuario\Downloads\SyntexIA-CRM-Standalone"
git remote add origin https://github.com/Susana471978/SyntexIA-CRM-Standalone.git
git branch -M main
git push -u origin main
```

### PASO 3️⃣: Ingresar Credenciales de GitHub

GitHub pedirá tus credenciales. Opciones:

#### Opción A: Personal Access Token (Recomendado)

1. Ir a GitHub → Settings → Developer settings → Personal access tokens
2. Click en "Generate new token"
3. Nombre: `git-push-token`
4. Seleccionar scopes: `repo`, `write:repo_hook`
5. Click "Generate token"
6. **Copiar el token** (aparece solo una vez)

7. Cuando Git pida contraseña:
   - Username: `tu-usuario-github`
   - Password: **pegar el token**

#### Opción B: GitHub CLI (Más fácil)

```powershell
# Instalar GitHub CLI (si no lo tienes)
choco install gh

# Autenticarse
gh auth login

# Ya está listo para pushear
```

### PASO 4️⃣: Verificar que Subió

**En tu navegador:**
1. Ir a https://github.com/tu-usuario/SyntexIA-CRM-Standalone
2. Deberías ver:
   - ✅ Todos los archivos
   - ✅ README.md visible
   - ✅ 2 commits

**En terminal:**
```powershell
cd "C:\Users\Usuario\Downloads\SyntexIA-CRM-Standalone"
git log --oneline
```

Deberías ver algo como:
```
919c0c8 docs: Add comprehensive integration guide for billing systems
f20c4d3 Initial commit: SyntexIA CRM Standalone - Complete independent CRM system
```

---

## 🔐 Dar Acceso a tu Amiga

### Opción 1: Repositorio Público (Recomendado)
El repositorio es público, así que tu amiga puede clonarlo directamente:

```bash
git clone https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git
```

**Ventajas:** Fácil, sin autenticación
**Desventajas:** Cualquiera puede verlo

### Opción 2: Invitar como Colaborador
Si quieres que tu amiga pueda hacer cambios:

1. GitHub → Repository Settings → Collaborators
2. Click "Add people"
3. Buscar por email/usuario de GitHub
4. Click "Invite"

Tu amiga recibirá una invitación por email.

---

## 📥 PARA TU AMIGA: CÓMO CLONAR

Una vez que esté en GitHub, tu amiga hace esto:

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git

# 2. Entrar a la carpeta
cd SyntexIA-CRM-Standalone

# 3. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar servidor
python main.py

# 6. Abrir documentación
# http://localhost:8000/docs
```

---

## 🔄 FUTURAS ACTUALIZACIONES

Si quieres pushear cambios nuevos:

```powershell
cd "C:\Users\Usuario\Downloads\SyntexIA-CRM-Standalone"

# Ver cambios
git status

# Agregar cambios
git add .

# Hacer commit
git commit -m "descripción del cambio"

# Pushear a GitHub
git push origin main
```

---

## 🛠️ TROUBLESHOOTING

### Error: "fatal: remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git
```

### Error: "fatal: You are not currently on a branch"
```powershell
git checkout -b main
git push -u origin main
```

### Error: "fatal: 'origin' does not appear to be a 'git' repository"
```powershell
git remote -v  # Ver si origin está configurado
```

### La URL es incorrecta
```powershell
git remote set-url origin https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git
git push origin main
```

---

## 📊 VERSIONES Y RELEASES

Después de subir, puedes crear releases en GitHub:

1. Ir a GitHub → Releases → Draft a new release
2. Tag: `v1.0.0`
3. Title: `SyntexIA CRM Standalone v1.0.0`
4. Description: Incluir features principales
5. Publish release

Esto permite que otros descarguen ZIP directamente sin Git.

---

## ✨ PRÓXIMOS PASOS

Una vez en GitHub:

- [ ] Compartir URL con tu amiga
- [ ] Tu amiga clona el repositorio
- [ ] Tu amiga ejecuta `python main.py`
- [ ] Tu amiga accede a http://localhost:8000/docs
- [ ] Tu amiga lee INTEGRATION_GUIDE.md para integrar con su facturación
- [ ] Tu amiga implementa `conectar_con_crm.py` en su código

---

## 💬 RESUMEN PARA TU AMIGA

**URL para clonar:**
```
https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git
```

**Qué es:**
- CRM completamente independiente
- Basado en FastAPI + SQLite
- Documentación automática en `/docs`
- Listo para integrar con sistemas de facturación

**Cómo usarlo:**
1. Clonar
2. `python main.py`
3. Abrir `http://localhost:8000/docs`
4. Ver INTEGRATION_GUIDE.md para implementación

**Características:**
- ✅ CRUD Clientes
- ✅ Contactos, Actividades, Oportunidades
- ✅ Estadísticas y Resumen Ejecutivo
- ✅ API REST documentada
- ✅ Tests incluidos

---

¡Listo! Ahora tu amiga puede clonar y usar el CRM. 🎉
