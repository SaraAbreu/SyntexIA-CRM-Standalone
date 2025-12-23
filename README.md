# 📊 SyntexIA CRM Standalone

Sistema de Gestión de Relaciones con Clientes (CRM) completamente independiente basado en FastAPI.

## ✨ Características

- ✅ **Gestión de Clientes**: CRUD completo (Crear, Leer, Actualizar, Eliminar)
- ✅ **Contactos**: Manejo de múltiples tipos de contacto por cliente
- ✅ **Actividades**: Seguimiento de interacciones y tareas
- ✅ **Oportunidades**: Gestión de ventas potenciales
- ✅ **Estadísticas**: Resumen ejecutivo del CRM
- ✅ **Base de datos SQLite**: Sin dependencias externas
- ✅ **API REST**: Documentación Swagger automática
- ✅ **CORS habilitado**: Compatible con frontends web

## 📋 Requisitos Previos

- Python 3.9+
- pip (gestor de paquetes Python)
- Opcional: Virtual Environment (recomendado)

## 🚀 Instalación Rápida

### 1. Clonar o descargar el repositorio
```bash
# Si lo tienes en una carpeta local, solo navega a ella
cd SyntexIA-CRM-Standalone
```

### 2. Crear un entorno virtual (recomendado)
```bash
# En Windows
python -m venv .venv
.venv\Scripts\activate

# En macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar el servidor
```bash
python main.py
```

La salida debería ser:
```
✅ SyntexIA CRM Standalone iniciado
📍 Documentación disponible en: http://localhost:8000/docs
```

## 🌐 Acceso a la API

### Swagger UI (Documentación Interactiva)
```
http://localhost:8000/docs
```
Aquí puedes:
- Ver todos los endpoints disponibles
- Probar requests sin código
- Ver respuestas esperadas

### ReDoc (Documentación Alternativa)
```
http://localhost:8000/redoc
```

### Health Check
```
http://localhost:8000/health
```

## 📚 Endpoints Principales

### Clientes
```
POST   /api/crm/clientes               - Crear cliente
GET    /api/crm/clientes               - Listar clientes (con filtros)
GET    /api/crm/clientes/{id}          - Obtener cliente por ID
PUT    /api/crm/clientes/{id}          - Actualizar cliente
DELETE /api/crm/clientes/{id}          - Eliminar cliente
```

### Contactos
```
POST   /api/crm/clientes/{id}/contactos      - Agregar contacto
GET    /api/crm/clientes/{id}/contactos      - Listar contactos
```

### Actividades
```
POST   /api/crm/clientes/{id}/actividades    - Crear actividad
GET    /api/crm/clientes/{id}/actividades    - Listar actividades
```

### Oportunidades
```
POST   /api/crm/clientes/{id}/oportunidades  - Crear oportunidad
GET    /api/crm/clientes/{id}/oportunidades  - Listar oportunidades
```

### Estadísticas
```
GET    /api/crm/resumen                      - Resumen ejecutivo
```

## 📝 Ejemplos de Uso

### Crear un Cliente
```bash
curl -X POST "http://localhost:8000/api/crm/clientes" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_completo": "Acme Corporation",
    "email": "info@acme.com",
    "cif_nif": "ES12345678A",
    "tipo_cliente": "empresa",
    "estado": "prospecto"
  }'
```

### Listar Clientes
```bash
curl "http://localhost:8000/api/crm/clientes?skip=0&limit=10"
```

### Obtener Cliente por ID
```bash
curl "http://localhost:8000/api/clientes/cli_abc123456789"
```

### Obtener Resumen CRM
```bash
curl "http://localhost:8000/api/crm/resumen"
```

## 🗂️ Estructura del Proyecto

```
SyntexIA-CRM-Standalone/
├── main.py                        # Punto de entrada (ejecutar esto)
├── requirements.txt               # Dependencias Python
├── README.md                      # Este archivo
├── .gitignore                     # Archivos ignorados en Git
├── crm.db                         # Base de datos SQLite (se crea automáticamente)
├── logs/                          # Logs de la aplicación
│   └── crm.log                    # Archivo de log
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── logger.py              # Configuración de logging
│   ├── models/
│   │   ├── __init__.py
│   │   └── crm_models.py          # Modelos Pydantic (Cliente, Contacto, etc.)
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── crm_repository.py      # Capa de datos (SQLite)
│   └── interface/
│       ├── __init__.py
│       └── crm_api.py             # Endpoints FastAPI
└── tests/
    ├── __init__.py
    └── test_crm_standalone.py     # Tests unitarios
```

## 🔧 Configuración

### Logger
El logging se configura en `src/config/logger.py`. Los logs se guardan en `logs/crm.log`.

### Base de Datos
- **Ubicación**: `crm.db` en la raíz del proyecto
- **Motor**: SQLite 3
- **Creación**: Automática al primer inicio
- **Tablas creadas automáticamente**: clientes, contactos, actividades, oportunidades

### CORS
La API acepta requests desde cualquier origen. En producción, modifica `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # Especificar tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Testing

### Tests Incluidos
```bash
python -m pytest tests/ -v
```

### Test Manual de Endpoints
Ver sección "Ejemplos de Uso" arriba, o usar Swagger UI en `/docs`.

## 🐛 Troubleshooting

### Error: "Port 8000 already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Error: "ModuleNotFoundError"
Asegúrate de:
1. Estar en el directorio correcto: `cd SyntexIA-CRM-Standalone`
2. Estar en el entorno virtual activado
3. Haber instalado dependencias: `pip install -r requirements.txt`

### Base de datos corrupta
Si `crm.db` se corrompe, simplemente:
```bash
rm crm.db
python main.py  # Se recreará automáticamente
```

## 📈 Mejoras Futuras

- [ ] Autenticación JWT
- [ ] Integración con correo electrónico
- [ ] Exportar reportes (PDF, Excel)
- [ ] Webhooks para integraciones
- [ ] Dashboard web
- [ ] Sincronización con servicios externos
- [ ] Búsqueda avanzada y filtros
- [ ] Campos personalizados

## 📄 Licencia

Propietario - Todos los derechos reservados

## 👨‍💻 Autor

**SyntexIA**
- Web: https://syntexia.io
- Email: info@syntexia.io

## 🤝 Soporte

Para problemas o preguntas:
1. Revisa esta documentación
2. Consulta los logs en `logs/crm.log`
3. Accede a Swagger UI para ver documentación interactiva
4. Contacta al equipo de desarrollo

## 🚀 Próximos Pasos

1. **Crear tu primer cliente**: POST a `/api/crm/clientes`
2. **Agregar contactos**: POST a `/api/crm/clientes/{id}/contactos`
3. **Registrar actividades**: POST a `/api/crm/clientes/{id}/actividades`
4. **Crear oportunidades**: POST a `/api/crm/clientes/{id}/oportunidades`
5. **Consultar resumen**: GET a `/api/crm/resumen`

---

**¡Gracias por usar SyntexIA CRM Standalone!** 🎉
