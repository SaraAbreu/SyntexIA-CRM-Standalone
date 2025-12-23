# =====================================================
# 🚀 SyntexIA CRM — APIs REST (FastAPI Router)
# =====================================================
"""
Endpoints completos para gestión de CRM:
- Clientes (CRUD)
- Contactos
- Actividades
- Oportunidades
- Estadísticas
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from src.repositories.crm_repository import CRMRepository
from src.models.crm_models import (
    Cliente, ClienteCreate, ClienteUpdate, ContactoSchema,
    ActividadSchema, OportunidadSchema, ResumenCRM
)
from src.config.logger import get_logger

logger = get_logger("CRM-API")

# Inicializar router y repositorio
router = APIRouter(prefix="/api/crm", tags=["CRM"])
crm_repo = CRMRepository(db_path="crm.db")


# =====================================================
# UTILIDADES
# =====================================================

def get_crm_repo():
    """Inyector de dependencia para repositorio"""
    return crm_repo


# =====================================================
# ENDPOINTS CLIENTES
# =====================================================

@router.post("/clientes", response_model=Cliente, status_code=201)
def crear_cliente(cliente_data: ClienteCreate, repo: CRMRepository = Depends(get_crm_repo)):
    """
    Crear nuevo cliente
    
    **Parámetros:**
    - `nombre_completo`: Nombre o empresa (requerido)
    - `email`: Email único
    - `cif_nif`: ID fiscal
    - `contactos`: Lista de contactos iniciales
    
    **Respuesta:** Cliente creado con ID
    """
    try:
        return repo.crear_cliente(cliente_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error creando cliente: {e}")
        raise HTTPException(status_code=500, detail="Error al crear cliente")


@router.get("/clientes", response_model=dict)
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    estado: Optional[str] = Query(None),
    segmento: Optional[str] = Query(None),
    buscar: Optional[str] = Query(None),
    repo: CRMRepository = Depends(get_crm_repo)
):
    """
    Listar clientes con paginación y filtros
    
    **Parámetros:**
    - `skip`: Saltar N registros (paginación)
    - `limit`: Máximo registros a devolver
    - `estado`: Filtrar por estado (prospecto, activo, inactivo, bloqueado)
    - `segmento`: Filtrar por segmento
    - `buscar`: Buscar por nombre, email o razón social
    
    **Respuesta:** Lista de clientes + total
    """
    try:
        clientes, total = repo.listar_clientes(skip, limit, estado, segmento, buscar)
        return {
            "clientes": clientes,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"❌ Error listando clientes: {e}")
        raise HTTPException(status_code=500, detail="Error al listar clientes")


@router.get("/clientes/{cliente_id}", response_model=Cliente)
def obtener_cliente(cliente_id: str, repo: CRMRepository = Depends(get_crm_repo)):
    """
    Obtener cliente por ID con todos sus datos relacionados
    
    Incluye: contactos, actividades recientes, oportunidades
    """
    cliente = repo.obtener_cliente(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.put("/clientes/{cliente_id}", response_model=Cliente)
def actualizar_cliente(
    cliente_id: str,
    cliente_data: ClienteUpdate,
    repo: CRMRepository = Depends(get_crm_repo)
):
    """
    Actualizar datos del cliente
    
    Solo actualiza los campos proporcionados (parcial)
    """
    try:
        cliente = repo.obtener_cliente(cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return repo.actualizar_cliente(cliente_id, cliente_data)
    except Exception as e:
        logger.error(f"❌ Error actualizando cliente: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar cliente")


@router.delete("/clientes/{cliente_id}", status_code=204)
def eliminar_cliente(cliente_id: str, repo: CRMRepository = Depends(get_crm_repo)):
    """
    Eliminar cliente (y sus datos relacionados)
    
    **Advertencia:** Esta acción es irreversible
    """
    cliente = repo.obtener_cliente(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    repo.eliminar_cliente(cliente_id)


# =====================================================
# ENDPOINTS CONTACTOS
# =====================================================

@router.post("/clientes/{cliente_id}/contactos", status_code=201)
def agregar_contacto(
    cliente_id: str,
    contacto: ContactoSchema,
    repo: CRMRepository = Depends(get_crm_repo)
):
    """
    Agregar contacto a un cliente
    
    **Tipos de contacto:** email, telefono, movil, direccion
    """
    try:
        cliente = repo.obtener_cliente(cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Usar el repositorio para crear el contacto
        repo._crear_contacto(cliente_id, contacto)
        
        # Obtener el contacto creado
        contactos = repo._obtener_contactos(cliente_id)
        if contactos:
            return contactos[-1]  # Retornar el último contacto creado
        
        return {"status": "ok", "message": "Contacto agregado"}
    except Exception as e:
        logger.error(f"[ERROR] Error agregando contacto: {e}")
        raise HTTPException(status_code=500, detail=f"Error al agregar contacto: {str(e)}")


@router.get("/clientes/{cliente_id}/contactos", response_model=List[ContactoSchema])
def listar_contactos(cliente_id: str, repo: CRMRepository = Depends(get_crm_repo)):
    """Obtener todos los contactos de un cliente"""
    cliente = repo.obtener_cliente(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return repo._obtener_contactos(cliente_id)


# =====================================================
# ENDPOINTS ACTIVIDADES
# =====================================================

@router.post("/clientes/{cliente_id}/actividades", response_model=ActividadSchema)
def crear_actividad(
    cliente_id: str,
    actividad: ActividadSchema,
    repo: CRMRepository = Depends(get_crm_repo)
):
    """
    Crear actividad/interacción para un cliente
    
    **Tipos de actividad:** llamada, email, reunion, tarea, nota, venta
    """
    try:
        cliente = repo.obtener_cliente(cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return repo.crear_actividad(cliente_id, actividad)
    except Exception as e:
        logger.error(f"❌ Error creando actividad: {e}")
        raise HTTPException(status_code=500, detail="Error al crear actividad")


@router.get("/clientes/{cliente_id}/actividades", response_model=List[ActividadSchema])
def listar_actividades(cliente_id: str, repo: CRMRepository = Depends(get_crm_repo)):
    """Obtener actividades recientes de un cliente"""
    cliente = repo.obtener_cliente(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return repo._obtener_actividades(cliente_id, limit=20)


# =====================================================
# ENDPOINTS OPORTUNIDADES
# =====================================================

@router.post("/clientes/{cliente_id}/oportunidades", response_model=OportunidadSchema)
def crear_oportunidad(
    cliente_id: str,
    oportunidad: OportunidadSchema,
    repo: CRMRepository = Depends(get_crm_repo)
):
    """
    Crear oportunidad de venta para un cliente
    
    **Estados:** inicial, contacto, propuesta, negociacion, ganada, perdida
    """
    try:
        cliente = repo.obtener_cliente(cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return repo.crear_oportunidad(cliente_id, oportunidad)
    except Exception as e:
        logger.error(f"❌ Error creando oportunidad: {e}")
        raise HTTPException(status_code=500, detail="Error al crear oportunidad")


@router.get("/clientes/{cliente_id}/oportunidades", response_model=List[OportunidadSchema])
def listar_oportunidades(cliente_id: str, repo: CRMRepository = Depends(get_crm_repo)):
    """Obtener oportunidades abiertas de un cliente"""
    cliente = repo.obtener_cliente(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return repo._obtener_oportunidades(cliente_id)


# =====================================================
# ENDPOINTS ESTADÍSTICAS
# =====================================================

@router.get("/resumen", response_model=ResumenCRM)
def obtener_resumen_crm(repo: CRMRepository = Depends(get_crm_repo)):
    """
    Obtener resumen ejecutivo del CRM
    
    Incluye:
    - Total de clientes y estado
    - Valor facturado y oportunidades
    - Actividades pendientes
    - Alertas (clientes morosos, vencimientos próximos)
    """
    try:
        return repo.obtener_resumen_crm()
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener resumen")


# =====================================================
# ENDPOINTS BÚSQUEDA AVANZADA
# =====================================================

@router.get("/clientes/buscar/email/{email}")
def buscar_por_email(email: str, repo: CRMRepository = Depends(get_crm_repo)):
    """Buscar cliente por email exacto"""
    clientes, _ = repo.listar_clientes(buscar=email)
    if not clientes:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return clientes[0]
