# 📋 Guía: Extender Módulo Cliente de SmartBilling con CRM Integrado

**Objetivo:** Transformar el módulo cliente vacío de SmartBilling en un **módulo cliente + CRM unificado** que capture la relación comercial completa.

---

## 🎯 Situación Actual vs Propuesta

### ❌ Situación Actual (Módulo Cliente Vacío)
```
CLIENTE EN SMARTBILLING
├─ ID
├─ Nombre
├─ Email
├─ Teléfono
├─ Dirección
├─ CIF/NIF
└─ [NADA MÁS]
```

**Problema:** Solo datos administrativos. Cero inteligencia comercial.

---

### ✅ Situación Propuesta (Cliente + CRM)
```
CLIENTE EN SMARTBILLING MEJORADO
├─ 📇 DATOS BÁSICOS
│  ├─ ID
│  ├─ Nombre empresa
│  ├─ Sector/Industria
│  ├─ Tamaño empresa
│  └─ CIF/NIF
│
├─ 📞 CONTACTOS (múltiples personas)
│  ├─ Contacto 1: Juan (Director)
│  ├─ Contacto 2: María (Contable)
│  └─ Contacto 3: Pedro (Técnico)
│
├─ 📧 HISTORIAL COMUNICACIONES
│  ├─ 23/12: Email con presupuesto
│  ├─ 20/12: Llamada de seguimiento
│  ├─ 18/12: Reunión inicial (1h 30min)
│  └─ 15/12: Primer contacto WhatsApp
│
├─ 💼 OPORTUNIDADES
│  ├─ Proyecto A (€5.000) - En negociación
│  ├─ Proyecto B (€2.000) - Propuesta enviada
│  └─ Proyecto C (€10.000) - Lead inicial
│
├─ 📊 SALUD DEL CLIENTE
│  ├─ Riesgo de impago: BAJO (historial perfecto)
│  ├─ Días para pagar: 20 (muy rápido)
│  ├─ Monto promedio por factura: €1.850
│  ├─ Frecuencia: Cada 2 semanas
│  └─ Próxima factura esperada: 28/12
│
├─ 📈 INTELIGENCIA COMERCIAL
│  ├─ LTV (lifetime value): €45.000
│  ├─ Potencial de crecimiento: ALTO (sector en expansión)
│  ├─ Cliente más valioso: SÍ (Top 5%)
│  └─ Riesgo de pérdida: BAJO
│
└─ 💰 HISTORIAL ECONÓMICO
   ├─ Facturas totales: 24
   ├─ Ingresos generados: €44.400
   ├─ Último pago: 22/12 (a tiempo)
   └─ Facturas impagadas: 0
```

---

## 🏗️ Arquitectura: Cómo Extender

### Opción 1: **EXPANSIÓN IN-SITU** (RECOMENDADA)

Expandes directamente la tabla/modelo `Cliente` de SmartBilling:

```
BD SMARTBILLING (ANTES)
├─ tabla_clientes
│  ├─ id
│  ├─ nombre
│  ├─ email
│  ├─ telefono
│  ├─ direccion
│  └─ cif

BD SMARTBILLING (DESPUÉS)
├─ tabla_clientes
│  ├─ id
│  ├─ nombre ◄── YA EXISTE
│  ├─ email ◄── YA EXISTE
│  ├─ telefono ◄── YA EXISTE
│  ├─ direccion ◄── YA EXISTE
│  ├─ cif ◄── YA EXISTE
│  ├─ 🆕 sector (manufacturing, retail, servicios, etc.)
│  ├─ 🆕 tamaño_empresa (pequeña, mediana, grande)
│  ├─ 🆕 estado (prospecto, activo, inactivo, bloqueado)
│  ├─ 🆕 ltv (lifetime value calculado)
│  ├─ 🆕 riesgo_impago (bajo, medio, alto)
│  └─ 🆕 fecha_primera_factura
│
├─ tabla_contactos (NUEVA)
│  ├─ id
│  ├─ cliente_id (FK)
│  ├─ nombre
│  ├─ rol
│  ├─ email
│  ├─ telefono
│  ├─ principal (bool)
│  └─ fecha_creacion
│
├─ tabla_actividades (NUEVA)
│  ├─ id
│  ├─ cliente_id (FK)
│  ├─ tipo (llamada, email, reunion, tarea, nota)
│  ├─ titulo
│  ├─ descripcion
│  ├─ fecha
│  ├─ responsable
│  └─ completada (bool)
│
├─ tabla_oportunidades (NUEVA)
│  ├─ id
│  ├─ cliente_id (FK)
│  ├─ nombre_proyecto
│  ├─ descripcion
│  ├─ monto_estimado
│  ├─ estado (inicial, contacto, propuesta, negociacion, ganada, perdida)
│  ├─ fecha_creacion
│  ├─ fecha_cierre_esperada
│  └─ probabilidad (%)
│
└─ tabla_salud_cliente (NUEVA)
   ├─ id
   ├─ cliente_id (FK)
   ├─ dias_para_pagar_promedio
   ├─ historial_pagos_a_tiempo (%)
   ├─ monto_promedio_factura
   ├─ frecuencia_compra_dias
   ├─ ultima_factura_date
   ├─ proxima_factura_esperada
   └─ riesgo_pérdida_score (0-100)
```

### Ventajas Opción 1:
✅ Una sola BD (SmartBilling)  
✅ Una sola interfaz  
✅ Datos integrados desde el inicio  
✅ Fácil de usar para tu amiga

---

## 💻 Implementación Paso a Paso

### PASO 1: Expandir Modelo Cliente

**Archivo:** `src/models/cliente_models.py` (crear o extender)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EstadoCliente(str, Enum):
    PROSPECTO = "prospecto"
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    BLOQUEADO = "bloqueado"

class RiesgoImpago(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"

class TamañoEmpresa(str, Enum):
    PEQUEÑA = "pequeña"
    MEDIANA = "mediana"
    GRANDE = "grande"

# ✅ MODELO EXPANDIDO
class ClienteSchema(BaseModel):
    # Datos originales de SmartBilling
    id: Optional[str] = None
    nombre: str
    email: str
    telefono: str
    direccion: str
    cif: str
    
    # 🆕 Datos nuevos CRM
    sector: Optional[str] = None  # manufacturing, retail, servicios, etc.
    tamaño_empresa: Optional[TamañoEmpresa] = None
    estado: EstadoCliente = EstadoCliente.PROSPECTO
    ltv: Optional[float] = 0.0  # Lifetime Value
    riesgo_impago: RiesgoImpago = RiesgoImpago.BAJO
    fecha_primera_factura: Optional[datetime] = None
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Empresa XYZ",
                "email": "info@xyz.com",
                "telefono": "+34 91 123 4567",
                "direccion": "Calle Principal 123, Madrid",
                "cif": "A12345678",
                "sector": "manufacturing",
                "tamaño_empresa": "mediana",
                "estado": "activo",
                "riesgo_impago": "bajo"
            }
        }

class ContactoSchema(BaseModel):
    id: Optional[str] = None
    cliente_id: str
    nombre: str
    rol: str  # Director, Contable, Técnico, etc.
    email: Optional[str] = None
    telefono: Optional[str] = None
    principal: bool = False
    fecha_creacion: datetime = Field(default_factory=datetime.now)

class ActividadSchema(BaseModel):
    id: Optional[str] = None
    cliente_id: str
    tipo: str  # llamada, email, reunion, tarea, nota
    titulo: str
    descripcion: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.now)
    responsable: Optional[str] = None
    completada: bool = False

class OportunidadSchema(BaseModel):
    id: Optional[str] = None
    cliente_id: str
    nombre_proyecto: str
    descripcion: Optional[str] = None
    monto_estimado: float
    estado: str  # inicial, contacto, propuesta, negociacion, ganada, perdida
    probabilidad: int = 30  # 0-100
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_cierre_esperada: Optional[datetime] = None
```

---

### PASO 2: Expandir Repositorio (BD)

**Archivo:** `src/repositories/cliente_repository.py`

```python
import sqlite3
from typing import List, Optional, Dict
from src.models.cliente_models import (
    ClienteSchema, ContactoSchema, ActividadSchema, OportunidadSchema
)
from datetime import datetime

class ClienteRepository:
    def __init__(self, db_path="smartbilling.db"):
        self.db_path = db_path
        self.crear_tablas()
    
    def crear_tablas(self):
        """Crear/actualizar estructura de BD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1️⃣ TABLA CLIENTES EXPANDIDA
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefono TEXT,
                direccion TEXT,
                cif TEXT UNIQUE,
                sector TEXT,
                tamaño_empresa TEXT,
                estado TEXT DEFAULT 'prospecto',
                ltv REAL DEFAULT 0.0,
                riesgo_impago TEXT DEFAULT 'bajo',
                fecha_primera_factura DATETIME,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2️⃣ TABLA CONTACTOS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contactos (
                id TEXT PRIMARY KEY,
                cliente_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                rol TEXT,
                email TEXT,
                telefono TEXT,
                principal BOOLEAN DEFAULT 0,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        
        # 3️⃣ TABLA ACTIVIDADES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id TEXT PRIMARY KEY,
                cliente_id TEXT NOT NULL,
                tipo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                fecha DATETIME NOT NULL,
                responsable TEXT,
                completada BOOLEAN DEFAULT 0,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        
        # 4️⃣ TABLA OPORTUNIDADES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oportunidades (
                id TEXT PRIMARY KEY,
                cliente_id TEXT NOT NULL,
                nombre_proyecto TEXT NOT NULL,
                descripcion TEXT,
                monto_estimado REAL NOT NULL,
                estado TEXT NOT NULL,
                probabilidad INTEGER DEFAULT 30,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_cierre_esperada DATETIME,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        
        # 5️⃣ TABLA SALUD CLIENTE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salud_cliente (
                id TEXT PRIMARY KEY,
                cliente_id TEXT UNIQUE NOT NULL,
                dias_para_pagar_promedio INTEGER,
                historial_pagos_a_tiempo REAL,
                monto_promedio_factura REAL,
                frecuencia_compra_dias INTEGER,
                ultima_factura_date DATETIME,
                proxima_factura_esperada DATETIME,
                riesgo_perdida_score INTEGER,
                ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # MÉTODOS CRUD BÁSICOS
    def crear_cliente(self, cliente: ClienteSchema) -> ClienteSchema:
        """Crear cliente con datos CRM"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO clientes (
                    id, nombre, email, telefono, direccion, cif,
                    sector, tamaño_empresa, estado, ltv, riesgo_impago
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(hash(cliente.email)),  # ID simple
                cliente.nombre,
                cliente.email,
                cliente.telefono,
                cliente.direccion,
                cliente.cif,
                cliente.sector,
                cliente.tamaño_empresa,
                cliente.estado,
                cliente.ltv,
                cliente.riesgo_impago
            ))
            conn.commit()
            return cliente
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error creando cliente: {e}")
        finally:
            conn.close()
    
    def obtener_cliente(self, cliente_id: str) -> Optional[Dict]:
        """Obtener cliente completo (datos + contactos + actividades + oportunidades)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Datos básicos
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            return None
        
        # Contactos
        cursor.execute("SELECT * FROM contactos WHERE cliente_id = ?", (cliente_id,))
        contactos = cursor.fetchall()
        
        # Actividades recientes
        cursor.execute("""
            SELECT * FROM actividades 
            WHERE cliente_id = ? 
            ORDER BY fecha DESC LIMIT 10
        """, (cliente_id,))
        actividades = cursor.fetchall()
        
        # Oportunidades abiertas
        cursor.execute("""
            SELECT * FROM oportunidades 
            WHERE cliente_id = ? AND estado != 'ganada' AND estado != 'perdida'
        """, (cliente_id,))
        oportunidades = cursor.fetchall()
        
        # Salud
        cursor.execute("SELECT * FROM salud_cliente WHERE cliente_id = ?", (cliente_id,))
        salud = cursor.fetchone()
        
        conn.close()
        
        return {
            "cliente": cliente,
            "contactos": contactos,
            "actividades": actividades,
            "oportunidades": oportunidades,
            "salud": salud
        }
    
    def agregar_actividad(self, actividad: ActividadSchema) -> ActividadSchema:
        """Registrar interacción con cliente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO actividades (
                    id, cliente_id, tipo, titulo, descripcion, fecha, responsable
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(hash(str(datetime.now()))),
                actividad.cliente_id,
                actividad.tipo,
                actividad.titulo,
                actividad.descripcion,
                actividad.fecha,
                actividad.responsable
            ))
            conn.commit()
            return actividad
        finally:
            conn.close()
    
    def crear_oportunidad(self, oportunidad: OportunidadSchema) -> OportunidadSchema:
        """Registrar oportunidad/proyecto potencial"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO oportunidades (
                    id, cliente_id, nombre_proyecto, descripcion, monto_estimado, 
                    estado, probabilidad, fecha_cierre_esperada
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(hash(str(datetime.now()))),
                oportunidad.cliente_id,
                oportunidad.nombre_proyecto,
                oportunidad.descripcion,
                oportunidad.monto_estimado,
                oportunidad.estado,
                oportunidad.probabilidad,
                oportunidad.fecha_cierre_esperada
            ))
            conn.commit()
            return oportunidad
        finally:
            conn.close()
```

---

### PASO 3: APIs REST (FastAPI Router)

**Archivo:** `src/interface/cliente_api.py`

```python
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from src.repositories.cliente_repository import ClienteRepository
from src.models.cliente_models import (
    ClienteSchema, ContactoSchema, ActividadSchema, OportunidadSchema
)

router = APIRouter(prefix="/api/clientes", tags=["Clientes + CRM"])
repo = ClienteRepository(db_path="smartbilling.db")

# =====================================================
# ENDPOINTS CLIENTES
# =====================================================

@router.post("/", response_model=ClienteSchema, status_code=201)
def crear_cliente(cliente: ClienteSchema):
    """
    Crear cliente NUEVO (con datos CRM)
    
    Automáticamente registra:
    - Datos básicos
    - Estado inicial (prospecto)
    - Riesgo evaluado
    """
    return repo.crear_cliente(cliente)

@router.get("/{cliente_id}")
def obtener_cliente_completo(cliente_id: str):
    """
    Obtener PERFIL COMPLETO del cliente:
    - Datos básicos
    - Contactos (múltiples personas)
    - Historial de actividades
    - Oportunidades abiertas
    - Salud del cliente (riesgo, métricas)
    """
    cliente = repo.obtener_cliente(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# =====================================================
# ENDPOINTS CONTACTOS (Múltiples personas por empresa)
# =====================================================

@router.post("/{cliente_id}/contactos", response_model=ContactoSchema)
def agregar_contacto(cliente_id: str, contacto: ContactoSchema):
    """
    Agregar persona de contacto en la empresa
    (No solo un email, sino TODAS las personas clave)
    """
    contacto.cliente_id = cliente_id
    return repo.crear_contacto(contacto)

# =====================================================
# ENDPOINTS ACTIVIDADES (Historial de comunicación)
# =====================================================

@router.post("/{cliente_id}/actividades", response_model=ActividadSchema)
def registrar_actividad(cliente_id: str, actividad: ActividadSchema):
    """
    Registrar interacción con cliente:
    - Llamada: "Seguimiento, cliente interesado en plan pro"
    - Email: "Envío presupuesto para proyecto X"
    - Reunión: "Junta con directivos, decidieron contratar"
    - Nota: "Cliente menciona que tiene problemas de cash flow"
    
    Esto crea el HISTORIAL COMERCIAL completo
    """
    actividad.cliente_id = cliente_id
    return repo.agregar_actividad(actividad)

@router.get("/{cliente_id}/actividades")
def obtener_historial(cliente_id: str, limit: int = 20):
    """Obtener últimas N interacciones con cliente"""
    return repo.obtener_actividades(cliente_id, limit)

# =====================================================
# ENDPOINTS OPORTUNIDADES (Pipeline de ventas)
# =====================================================

@router.post("/{cliente_id}/oportunidades", response_model=OportunidadSchema)
def crear_oportunidad(cliente_id: str, oportunidad: OportunidadSchema):
    """
    Registrar OPORTUNIDAD DE VENTA:
    - Nombre: "Proyecto de transformación digital"
    - Monto: €45.000
    - Estado: "propuesta"
    - Probabilidad: 60% de cerrar
    
    Esto permite PREDECIR ingresos futuros
    """
    oportunidad.cliente_id = cliente_id
    return repo.crear_oportunidad(oportunidad)

@router.get("/{cliente_id}/oportunidades")
def obtener_pipeline(cliente_id: str):
    """Obtener todas las oportunidades abiertas con este cliente"""
    return repo.obtener_oportunidades(cliente_id)

# =====================================================
# ENDPOINT SALUD CLIENTE (INTELIGENCIA)
# =====================================================

@router.get("/{cliente_id}/salud")
def evaluar_salud_cliente(cliente_id: str):
    """
    INDICADORES clave del cliente:
    - Riesgo de impago (bajo/medio/alto)
    - Días promedio para pagar
    - Monto medio por factura
    - Riesgo de pérdida (score 0-100)
    - Próxima factura esperada
    
    Te dice si está SANO o en PELIGRO
    """
    salud = repo.obtener_salud(cliente_id)
    if not salud:
        raise HTTPException(status_code=404, detail="No hay datos de salud")
    return salud

# =====================================================
# ENDPOINT RECOMENDACIONES
# =====================================================

@router.get("/{cliente_id}/recomendaciones")
def obtener_recomendaciones(cliente_id: str):
    """
    Sistema INTELIGENTE que sugiere acciones:
    
    Ejemplos:
    - "ALERTA: Cliente en riesgo de impago (45 días sin pagar)"
    - "OPORTUNIDAD: Cliente está pagando rápido, subir monto de crédito"
    - "VENTA: Cliente con 3 meses inactivos, enviar propuesta nueva"
    - "RIESGO: Oportunidad de €50k, probabilidad baja, necesita seguimiento"
    """
    return repo.generar_recomendaciones(cliente_id)
```

---

## 🔗 Integración con Facturas

### Automatización: Cuando se emite factura → Actualizar CRM

**Archivo:** `src/interface/factura_api.py` (agregar hook)

```python
@router.post("/facturas")
def crear_factura(factura_data: FacturaSchema):
    """Crear factura Y actualizar CRM automáticamente"""
    
    # 1️⃣ Crear factura (original)
    factura = factura_repo.crear_factura(factura_data)
    
    # 2️⃣ 🆕 ACTUALIZAR CRM AUTOMÁTICAMENTE
    cliente_id = factura_data.cliente_id
    
    # Registrar actividad
    actividad = ActividadSchema(
        cliente_id=cliente_id,
        tipo="venta",
        titulo=f"Factura #{factura.numero}",
        descripcion=f"Factura por €{factura.total}",
        fecha=datetime.now(),
        responsable="Sistema"
    )
    cliente_repo.agregar_actividad(actividad)
    
    # Actualizar salud (próxima factura esperada, LTV, etc.)
    cliente_repo.actualizar_salud(cliente_id, factura)
    
    # Registrar en historial
    logger.info(f"✅ Factura #{factura.numero} + CRM actualizado para cliente {cliente_id}")
    
    return factura
```

---

## 📊 Dashboard/Vista del Cliente

**Cómo vería tu amiga un cliente en SmartBilling mejorado:**

```
╔═══════════════════════════════════════════════════╗
║ CLIENTE: EMPRESA XYZ S.L.                         ║
║ CIF: A12345678 | Estado: ACTIVO                   ║
╚═══════════════════════════════════════════════════╝

┌─ 📇 INFORMACIÓN
│  Email: contacto@xyz.com
│  Teléfono: +34 91 123 4567
│  Sector: Manufacturing
│  Tamaño: Mediana empresa
│  Desde: 15/06/2024 (1 año 6 meses)
│
├─ 📞 CONTACTOS (3 personas)
│  ✓ Juan García (Director) - juan@xyz.com
│  ✓ María López (Contable) - maria@xyz.com
│  ○ Pedro Martín (Técnico) - pedro@xyz.com
│
├─ 🟢 SALUD DEL CLIENTE
│  ✅ Riesgo de impago: BAJO (100% puntual)
│  ✅ Días para pagar: 15 (muy rápido)
│  ✅ Última interacción: Hace 3 días (email)
│  ✅ Riesgo de pérdida: BAJO
│
├─ 💰 ECONÓMICO
│  Total generado: €44.400
│  Facturas: 24
│  Promedio por factura: €1.850
│  Frecuencia: Cada 2 semanas
│  Próxima factura esperada: 28/12/2025
│
├─ 📧 ÚLTIMAS ACTIVIDADES
│  23/12: Email - Presupuesto proyecto especial
│  20/12: Llamada - Cliente solicita cambios en contrato
│  18/12: Reunión (1h) - Revisión trimestral positiva
│  15/12: Email - Acuse recibo factura nº 23
│
├─ 💼 OPORTUNIDADES (2 abiertas)
│  🔵 Proyecto Transformación Digital
│     Monto: €45.000 | Estado: En propuesta | Prob: 65%
│  🟢 Ampliación de servicios
│     Monto: €8.500 | Estado: Contacto | Prob: 40%
│
└─ 🎯 RECOMENDACIONES SISTEMA
   ✓ Cliente excelente, considerar descuento por volumen
   ✓ Proyecto digital tiene alta probabilidad, hacer seguimiento
   ✓ Programar reunión trimestral el 15/01/2026
```

---

## 🚀 Plan de Implementación (1-2 semanas)

| Fase | Tarea | Tiempo | Prioridad |
|------|-------|--------|-----------|
| 1️⃣ | Crear tablas en BD | 2h | 🔴 CRÍTICA |
| 2️⃣ | Modelos Pydantic expandidos | 2h | 🔴 CRÍTICA |
| 3️⃣ | Repositorio con métodos CRUD | 3h | 🔴 CRÍTICA |
| 4️⃣ | APIs REST (clientes, contactos, actividades) | 3h | 🔴 CRÍTICA |
| 5️⃣ | Integración factura ↔ CRM | 2h | 🟠 ALTA |
| 6️⃣ | Dashboard UI (ver cliente completo) | 4h | 🟠 ALTA |
| 7️⃣ | Sistema de recomendaciones inteligentes | 3h | 🟡 MEDIA |
| 8️⃣ | Testing y validación | 2h | 🔴 CRÍTICA |

**Total: 21 horas (3 días de trabajo concentrado)**

---

## ✅ Checklist Post-Implementación

- [ ] Modelo Cliente expandido con datos CRM
- [ ] Tablas de contactos, actividades, oportunidades creadas
- [ ] APIs REST funcionando (GET, POST, PUT, DELETE)
- [ ] Integración factura → CRM automática
- [ ] Dashboard muestra cliente completo
- [ ] Sistema de alertas funcionando
- [ ] Tests pasando
- [ ] Documentación actualizada
- [ ] BD migrada (backup antes)

---

## 🎁 Beneficios Para Tu Amiga

| Aspecto | Antes | Después |
|--------|-------|---------|
| **Visión de cliente** | Solo nombre y email | Perfil 360° completo |
| **Historial** | Nada | 100% de comunicaciones |
| **Predicción** | No sabe qué viene | Ve oportunidades futuras |
| **Riesgo** | Descubre pagos impagados tarde | Alerta temprana |
| **Crecimiento** | Confía en suerte | Datos dicen dónde crecer |
| **Tiempo dedicado a venta** | Buscando info manualmente | Datos listos en un click |

---

## 📞 Contacto & Soporte

Si tu amiga tiene dudas:
- **API Docs:** `/docs` (Swagger UI)
- **Base datos:** `smartbilling.db` (SQLite)
- **Logs:** `logs/smartbilling.log`

---

**Status:** ✅ LISTO PARA IMPLEMENTAR

**Complejidad:** ⭐⭐⭐☆☆ (Media)

**ROI:** 🚀🚀🚀🚀🚀 (Altísimo - va a transformar su negocio)
