# =====================================================
# 🧠 SyntexIA CRM — Modelos de Datos
# =====================================================
"""
Modelos Pydantic para gestión de clientes, contactos,
oportunidades y actividades del sistema CRM.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EstadoCliente(str, Enum):
    PROSPECTO = "prospecto"
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    BLOQUEADO = "bloqueado"


class EstadoOportunidad(str, Enum):
    INICIAL = "inicial"
    CONTACTO = "contacto"
    PROPUESTA = "propuesta"
    NEGOCIACION = "negociacion"
    GANADA = "ganada"
    PERDIDA = "perdida"


class TipoActividad(str, Enum):
    LLAMADA = "llamada"
    EMAIL = "email"
    REUNION = "reunion"
    TAREA = "tarea"
    NOTA = "nota"
    VENTA = "venta"


class TipoContacto(str, Enum):
    EMAIL = "email"
    TELEFONO = "telefono"
    MOVIL = "movil"
    DIRECCION = "direccion"


class ContactoSchema(BaseModel):
    id: Optional[str] = None
    tipo: TipoContacto
    valor: str
    principal: bool = False
    verificado: bool = False
    fecha_creacion: Optional[datetime] = None


class ActividadSchema(BaseModel):
    id: Optional[str] = None
    tipo: TipoActividad
    titulo: str
    descripcion: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.now)
    completada: bool = False
    responsable: Optional[str] = None
    notas: Optional[str] = None


class OportunidadSchema(BaseModel):
    id: Optional[str] = None
    titulo: str
    descripcion: Optional[str] = None
    estado: EstadoOportunidad = EstadoOportunidad.INICIAL
    valor_estimado: float
    probabilidad_cierre: float = Field(ge=0, le=100)
    fecha_cierre_esperada: datetime
    productos: Optional[List[str]] = None
    notas: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None


class ClienteBase(BaseModel):
    nombre_completo: str
    razon_social: Optional[str] = None
    tipo_cliente: str = "empresa"
    email: Optional[str] = None
    cif_nif: Optional[str] = None
    estado: EstadoCliente = EstadoCliente.PROSPECTO
    segmento: Optional[str] = None
    sector_industria: Optional[str] = None
    website: Optional[str] = None
    notas: Optional[str] = None
    credito_disponible: float = 0.0


class ClienteCreate(ClienteBase):
    contactos: Optional[List[ContactoSchema]] = None


class ClienteUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    razon_social: Optional[str] = None
    tipo_cliente: Optional[str] = None
    email: Optional[str] = None
    cif_nif: Optional[str] = None
    estado: Optional[EstadoCliente] = None
    segmento: Optional[str] = None
    sector_industria: Optional[str] = None
    website: Optional[str] = None
    notas: Optional[str] = None
    credito_disponible: Optional[float] = None


class Cliente(ClienteBase):
    id: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    contactos: List[ContactoSchema] = []
    oportunidades: List[OportunidadSchema] = []
    actividades_recientes: List[ActividadSchema] = []
    total_facturado: float = 0.0
    numero_facturas: int = 0
    promedio_venta: float = 0.0
    dias_desde_ultimo_contacto: Optional[int] = None
    tasa_pagos_a_tiempo: Optional[float] = None


class EstadisticasCliente(BaseModel):
    cliente_id: str
    total_facturado: float
    numero_facturas: int
    promedio_venta: float
    tasa_pagos_a_tiempo: float
    valor_oportunidades_abiertas: float
    dias_desde_primer_contacto: int
    dias_desde_ultimo_contacto: int
    salud_cliente: str


class ResumenCRM(BaseModel):
    total_clientes: int
    clientes_activos: int
    clientes_nuevos_mes: int
    valor_total_facturado: float
    valor_oportunidades_abiertas: float
    promedio_dias_pago: float
    clientes_morosos: int
    actividades_pendientes: int
    oportunidades_proximas_cerrar: int
