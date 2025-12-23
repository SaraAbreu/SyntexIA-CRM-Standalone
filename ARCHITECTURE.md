# 🏗️ Arquitectura de SyntexIA CRM Standalone

## Resumen Ejecutivo

**SyntexIA CRM Standalone** es un sistema de gestión de relaciones con clientes (CRM) completamente independiente, diseñado con arquitectura modular y escalable. No tiene dependencias en otros módulos del ecosistema SyntexIA.

## Características de Independencia

### ✅ Completamente Aislado
- ✓ Sin dependencias en módulos de Facturación
- ✓ Sin dependencias en módulos de Documentos
- ✓ Sin dependencias en módulos de Productos
- ✓ Sin dependencias en módulos de Contabilidad
- ✓ Sin dependencias en módulos de Reportes
- ✓ Funciona de forma completamente autónoma

### ✅ Dependencias Mínimas
```python
# Dependencias ONLY:
- FastAPI (API REST)
- Pydantic v2 (Validación de datos)
- SQLite 3 (Base de datos)
- Uvicorn (Servidor ASGI)
- Python 3.9+ (Runtime)
```

## Arquitectura en Capas

```
┌─────────────────────────────────────────────────────┐
│           INTERFACE LAYER (FastAPI)                 │
│    crm_api.py - Endpoints HTTP REST                │
│  • POST   /api/crm/clientes                         │
│  • GET    /api/crm/clientes                         │
│  • PUT    /api/crm/clientes/{id}                    │
│  • DELETE /api/crm/clientes/{id}                    │
│  • ... (actividades, contactos, oportunidades)      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        BUSINESS LOGIC LAYER                         │
│  • Validaciones Pydantic                            │
│  • Reglas de negocio                                │
│  • Transformaciones de datos                        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│       REPOSITORY LAYER (Data Access)                │
│    crm_repository.py - CRUD Operations              │
│  • crear_cliente()                                  │
│  • obtener_cliente()                                │
│  • actualizar_cliente()                             │
│  • eliminar_cliente()                               │
│  • ... (actividades, contactos, oportunidades)      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│       DATA LAYER (Persistence)                      │
│  SQLite Database (crm.db)                           │
│  ├── Tabla: clientes                                │
│  ├── Tabla: contactos                               │
│  ├── Tabla: actividades                             │
│  └── Tabla: oportunidades                           │
└─────────────────────────────────────────────────────┘
```

## Estructura de Directorios

```
SyntexIA-CRM-Standalone/
├── main.py                      # Punto de entrada - FastAPI app
├── quick_start.py               # Script de inicio rápido
├── requirements.txt             # Dependencias Python
├── README.md                    # Documentación principal
├── ARCHITECTURE.md              # Este archivo
├── .gitignore                   # Archivos ignorados
├── .env.example                 # Configuración de ejemplo
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── logger.py            # Configuración de logging
│   │
│   ├── models/                  # Pydantic v2 models
│   │   ├── __init__.py
│   │   └── crm_models.py
│   │       ├── EstadoCliente (Enum)
│   │       ├── EstadoOportunidad (Enum)
│   │       ├── TipoActividad (Enum)
│   │       ├── TipoContacto (Enum)
│   │       ├── ClienteCreate (BaseModel)
│   │       ├── ClienteUpdate (BaseModel)
│   │       ├── Cliente (BaseModel)
│   │       ├── ContactoSchema (BaseModel)
│   │       ├── ActividadSchema (BaseModel)
│   │       ├── OportunidadSchema (BaseModel)
│   │       ├── ResumenCRM (BaseModel)
│   │       └── EstadisticasCliente (BaseModel)
│   │
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   └── crm_repository.py
│   │       └── CRMRepository (clase)
│   │           ├── crear_cliente()
│   │           ├── obtener_cliente()
│   │           ├── listar_clientes()
│   │           ├── actualizar_cliente()
│   │           ├── eliminar_cliente()
│   │           ├── crear_actividad()
│   │           ├── crear_oportunidad()
│   │           └── obtener_resumen_crm()
│   │
│   └── interface/               # API layer (FastAPI routers)
│       ├── __init__.py
│       └── crm_api.py
│           └── router (APIRouter)
│               ├── POST   /api/crm/clientes
│               ├── GET    /api/crm/clientes
│               ├── GET    /api/crm/clientes/{id}
│               ├── PUT    /api/crm/clientes/{id}
│               ├── DELETE /api/crm/clientes/{id}
│               ├── POST   /clientes/{id}/contactos
│               ├── POST   /clientes/{id}/actividades
│               ├── POST   /clientes/{id}/oportunidades
│               └── GET    /resumen
│
├── tests/
│   ├── __init__.py
│   └── test_crm_standalone.py  # Suite de tests
│
├── logs/
│   └── crm.log                 # Archivo de log (creado automáticamente)
│
└── crm.db                      # Base de datos SQLite (creada automáticamente)
```

## Modelo de Datos

### Tabla: clientes
```sql
CREATE TABLE clientes (
    id TEXT PRIMARY KEY,
    nombre_completo TEXT NOT NULL,
    razon_social TEXT,
    tipo_cliente TEXT,
    email TEXT UNIQUE,
    cif_nif TEXT UNIQUE,
    estado TEXT DEFAULT 'prospecto',
    segmento TEXT,
    sector_industria TEXT,
    website TEXT,
    notas TEXT,
    credito_disponible REAL DEFAULT 0,
    total_facturado REAL DEFAULT 0,
    numero_facturas INTEGER DEFAULT 0,
    promedio_venta REAL DEFAULT 0,
    tasa_pagos_a_tiempo REAL,
    dias_desde_ultimo_contacto INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cliente_email ON clientes(email);
CREATE INDEX idx_cliente_estado ON clientes(estado);
```

### Tabla: contactos
```sql
CREATE TABLE contactos (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL,
    tipo TEXT NOT NULL,  -- email, telefono, movil, direccion
    valor TEXT NOT NULL,
    principal BOOLEAN DEFAULT 0,
    verificado BOOLEAN DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);
```

### Tabla: actividades
```sql
CREATE TABLE actividades (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL,
    tipo TEXT NOT NULL,  -- llamada, email, reunion, tarea, nota
    titulo TEXT NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP NOT NULL,
    completada BOOLEAN DEFAULT 0,
    responsable TEXT,
    notas TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE INDEX idx_actividades_fecha ON actividades(fecha);
```

### Tabla: oportunidades
```sql
CREATE TABLE oportunidades (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    estado TEXT DEFAULT 'inicial',  -- inicial, contacto, propuesta, negociacion, ganada, perdida
    valor_estimado REAL NOT NULL,
    probabilidad_cierre REAL DEFAULT 0,
    fecha_cierre_esperada TIMESTAMP,
    productos TEXT,  -- JSON
    notas TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE INDEX idx_oportunidades_estado ON oportunidades(estado);
```

## Flujos de Datos

### Crear Cliente
```
POST /api/crm/clientes
  ↓
crm_api.crear_cliente()
  ↓ (validación Pydantic)
ClienteCreate model
  ↓
crm_repository.crear_cliente()
  ↓ (SQL INSERT)
SQLite Database (tabla: clientes)
  ↓
Cliente model (respuesta HTTP 201)
```

### Listar Clientes
```
GET /api/crm/clientes?skip=0&limit=50
  ↓
crm_api.listar_clientes()
  ↓
crm_repository.listar_clientes()
  ↓ (SQL SELECT + COUNT)
SQLite Database
  ↓
List[Cliente] model (respuesta HTTP 200)
```

### Crear Actividad
```
POST /api/crm/clientes/{cliente_id}/actividades
  ↓
crm_api.crear_actividad()
  ↓ (validar cliente existe)
crm_repository.crear_actividad()
  ↓ (SQL INSERT)
SQLite Database (tabla: actividades)
  ↓
ActividadSchema model (respuesta HTTP 201)
```

## Patrones Utilizados

### 1. Repository Pattern
```python
class CRMRepository:
    """Encapsula toda la lógica de acceso a datos"""
    def crear_cliente(self, cliente_data: ClienteCreate) -> Cliente:
        # Insertar en base de datos
        # Retornar modelo Cliente
```

**Beneficios:**
- Separación de responsabilidades
- Facilita testing
- Cambiar BD sin tocar la API

### 2. Dependency Injection
```python
def get_crm_repo():
    """Inyector de dependencia"""
    return crm_repo

@router.post("/clientes")
def crear_cliente(repo: CRMRepository = Depends(get_crm_repo)):
    return repo.crear_cliente(cliente_data)
```

**Beneficios:**
- Código más testeable
- Fácil inyectar mocks
- Mejor separación de capas

### 3. Validación con Pydantic v2
```python
class ClienteCreate(BaseModel):
    nombre_completo: str  # Requerido
    email: str
    cif_nif: Optional[str] = None  # Opcional
    
    model_config = ConfigDict(
        validate_assignment=True,
        strict=True
    )
```

**Beneficios:**
- Validación automática
- Documentación automática (OpenAPI)
- Type hints completos

## Patrones de Seguridad

### 1. SQLite Thread Safety
```python
conn = sqlite3.connect(
    db_path,
    check_same_thread=False,  # ✅ Permitir acceso cross-thread
    timeout=30                 # ✅ Timeout para evitar deadlocks
)
```

### 2. SQL Injection Protection
```python
# ❌ INSEGURO
cursor.execute(f"SELECT * FROM clientes WHERE id = {cliente_id}")

# ✅ SEGURO (parameterizado)
cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
```

### 3. Input Validation
```python
# Pydantic valida automáticamente todos los inputs
class ClienteCreate(BaseModel):
    email: EmailStr  # Validación de email
    nombre_completo: str  # No vacío
```

## Performance Optimizations

### 1. Database Indexes
```sql
CREATE INDEX idx_cliente_email ON clientes(email);
CREATE INDEX idx_cliente_estado ON clientes(estado);
CREATE INDEX idx_actividades_fecha ON actividades(fecha);
```

### 2. Connection Pooling (futuro)
```python
# TODO: Implementar con SQLAlchemy
from sqlalchemy import create_engine
engine = create_engine(
    "sqlite:///crm.db",
    pool_pre_ping=True,
    pool_size=10
)
```

### 3. Paginación en Listados
```python
@router.get("/clientes")
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    # Evita traer todos los registros
```

## Escalabilidad Futura

### Migración a PostgreSQL (sin cambios de código)
```python
# Hoy: SQLite
db_path = "crm.db"

# Mañana: PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/crm"
```

### Agregar Caché
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def obtener_cliente(cliente_id: str):
    return repo.obtener_cliente(cliente_id)
```

### Agregar Queue para Operaciones Asíncronas
```python
from celery import Celery

@app.task
def procesar_contacto_csv(archivo: str):
    # Procesar en background
```

## Despliegue

### Desarrollo Local
```bash
python main.py
# http://localhost:8000
```

### Producción (Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Producción (Nginx Reverse Proxy)
```nginx
server {
    listen 80;
    server_name crm.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

## Testing

### Tipos de Tests
- **Unit Tests**: Funciones individuales
- **Integration Tests**: Endpoints HTTP
- **Database Tests**: Operaciones SQLite

### Cobertura Mínima
- API endpoints: 100%
- Repository methods: 100%
- Models: 80%

## Monitoreo

### Logs
```
logs/crm.log
- ERROR: Problemas críticos
- WARNING: Situaciones inusuales
- INFO: Eventos normales
- DEBUG: Información de troubleshooting
```

### Health Checks
```
GET /health
GET /api/version
GET /api/crm/resumen
```

## Roadmap

- [ ] Autenticación JWT
- [ ] Encriptación de datos sensibles
- [ ] Sincronización con calendarios (Google, Outlook)
- [ ] Integración de correo electrónico
- [ ] Reportes avanzados (PDF, Excel)
- [ ] Dashboard web interactivo
- [ ] Mobile app (React Native)
- [ ] Webhooks para integraciones

---

**Última actualización:** $(date)
**Versión:** 1.0.0
**Autor:** SyntexIA Team
