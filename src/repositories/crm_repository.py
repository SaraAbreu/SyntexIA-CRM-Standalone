# =====================================================
# 🗄️ SyntexIA CRM — Repositorio de Base de Datos
# =====================================================
"""
Gestor de persistencia para clientes, contactos, 
oportunidades y actividades del CRM.
Utiliza SQLite (local).
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid
from src.models.crm_models import (
    Cliente, ClienteCreate, ClienteUpdate, ContactoSchema,
    ActividadSchema, OportunidadSchema, EstadisticasCliente,
    ResumenCRM, EstadoCliente, EstadoOportunidad
)
from src.config.logger import get_logger

logger = get_logger("CRM-Repository")


class CRMRepository:
    """Repositorio para todas las operaciones CRUD del CRM"""

    def __init__(self, db_path: str = "crm.db"):
        self.db_path = db_path
        self.connection_string = f"sqlite:///{db_path}"
        self._init_db()

    # =====================================================
    # INICIALIZACIÓN BASE DE DATOS
    # =====================================================

    def _init_db(self):
        """Crea las tablas si no existen"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        # Tabla Clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
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
        )
        """)

        # Tabla Contactos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id TEXT PRIMARY KEY,
            cliente_id TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor TEXT NOT NULL,
            principal BOOLEAN DEFAULT 0,
            verificado BOOLEAN DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
        """)

        # Tabla Actividades
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id TEXT PRIMARY KEY,
            cliente_id TEXT NOT NULL,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            fecha TIMESTAMP NOT NULL,
            completada BOOLEAN DEFAULT 0,
            responsable TEXT,
            notas TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
        """)

        # Tabla Oportunidades
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS oportunidades (
            id TEXT PRIMARY KEY,
            cliente_id TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'inicial',
            valor_estimado REAL NOT NULL,
            probabilidad_cierre REAL DEFAULT 0,
            fecha_cierre_esperada TIMESTAMP,
            productos TEXT,
            notas TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
        """)

        # Índices para búsquedas rápidas
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_cliente_email ON clientes(email)""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_cliente_estado ON clientes(estado)""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_actividades_fecha ON actividades(fecha)""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_oportunidades_estado ON oportunidades(estado)""")

        conn.commit()
        conn.close()
        logger.info("[OK] Base de datos CRM inicializada")

    # =====================================================
    # CRUD CLIENTES
    # =====================================================

    def crear_cliente(self, cliente_data: ClienteCreate) -> Cliente:
        """Crear nuevo cliente"""
        cliente_id = f"cli_{uuid.uuid4().hex[:12]}"
        ahora = datetime.now()

        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO clientes (
                id, nombre_completo, razon_social, tipo_cliente, email, cif_nif,
                estado, segmento, sector_industria, website, notas, credito_disponible,
                fecha_creacion, fecha_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cliente_id, cliente_data.nombre_completo, cliente_data.razon_social,
                cliente_data.tipo_cliente, cliente_data.email, cliente_data.cif_nif,
                cliente_data.estado, cliente_data.segmento, cliente_data.sector_industria,
                cliente_data.website, cliente_data.notas, cliente_data.credito_disponible,
                ahora, ahora
            ))

            # Agregar contactos si existen
            if cliente_data.contactos:
                for contacto in cliente_data.contactos:
                    self._crear_contacto(cliente_id, contacto, cursor)

            conn.commit()
            logger.info(f"[OK] Cliente creado: {cliente_id}")

            return self.obtener_cliente(cliente_id)
        except sqlite3.IntegrityError as e:
            conn.rollback()
            logger.error(f"[ERROR] Error al crear cliente: {e}")
            raise ValueError(f"Email o CIF ya existe: {e}")
        finally:
            conn.close()

    def obtener_cliente(self, cliente_id: str) -> Optional[Cliente]:
        """Obtener cliente por ID"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
            row = cursor.fetchone()

            if not row:
                return None

            cliente_dict = dict(row)
            cliente_dict['contactos'] = self._obtener_contactos(cliente_id, cursor)
            cliente_dict['actividades_recientes'] = self._obtener_actividades(cliente_id, cursor, limit=5)
            cliente_dict['oportunidades'] = self._obtener_oportunidades(cliente_id, cursor)

            return Cliente(**cliente_dict)
        finally:
            conn.close()

    def listar_clientes(
        self,
        skip: int = 0,
        limit: int = 50,
        estado: Optional[str] = None,
        segmento: Optional[str] = None,
        buscar: Optional[str] = None
    ) -> tuple[List[Cliente], int]:
        """Listar clientes con filtros"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM clientes WHERE 1=1"
            params = []

            if estado:
                query += " AND estado = ?"
                params.append(estado)
            if segmento:
                query += " AND segmento = ?"
                params.append(segmento)
            if buscar:
                query += " AND (nombre_completo LIKE ? OR email LIKE ? OR razon_social LIKE ?)"
                buscar_param = f"%{buscar}%"
                params.extend([buscar_param, buscar_param, buscar_param])

            # Contar total
            count_query = query.replace("SELECT *", "SELECT COUNT(*)")
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            # Obtener página
            query += " ORDER BY fecha_actualizacion DESC LIMIT ? OFFSET ?"
            params.extend([limit, skip])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            clientes = []
            for row in rows:
                cliente_dict = dict(row)
                cliente_dict['contactos'] = self._obtener_contactos(cliente_dict['id'], cursor)
                cliente_dict['actividades_recientes'] = self._obtener_actividades(cliente_dict['id'], cursor, limit=3)
                cliente_dict['oportunidades'] = self._obtener_oportunidades(cliente_dict['id'], cursor)
                clientes.append(Cliente(**cliente_dict))

            return clientes, total
        finally:
            conn.close()

    def actualizar_cliente(self, cliente_id: str, cliente_data: ClienteUpdate) -> Cliente:
        """Actualizar cliente"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        try:
            # Construir query dinámicamente
            campos_actualizar = []
            valores = []

            for campo, valor in cliente_data.dict(exclude_unset=True).items():
                campos_actualizar.append(f"{campo} = ?")
                valores.append(valor)

            if campos_actualizar:
                campos_actualizar.append("fecha_actualizacion = ?")
                valores.append(datetime.now())
                valores.append(cliente_id)

                query = f"UPDATE clientes SET {', '.join(campos_actualizar)} WHERE id = ?"
                cursor.execute(query, valores)
                conn.commit()
                logger.info(f"[OK] Cliente actualizado: {cliente_id}")

            return self.obtener_cliente(cliente_id)
        finally:
            conn.close()

    def eliminar_cliente(self, cliente_id: str) -> bool:
        """Eliminar cliente"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            conn.commit()
            logger.info(f"[OK] Cliente eliminado: {cliente_id}")
            return cursor.rowcount > 0
        finally:
            conn.close()

    # =====================================================
    # OPERACIONES CONTACTOS
    # =====================================================

    def _crear_contacto(
        self,
        cliente_id: str,
        contacto: ContactoSchema,
        cursor: Optional[sqlite3.Cursor] = None
    ):
        """Crear contacto para cliente"""
        contacto_id = f"cont_{uuid.uuid4().hex[:12]}"
        should_close = cursor is None

        if cursor is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
            cursor = conn.cursor()
        else:
            conn = None

        try:
            cursor.execute("""
            INSERT INTO contactos (id, cliente_id, tipo, valor, principal, verificado, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                contacto_id, cliente_id, contacto.tipo, contacto.valor,
                contacto.principal, contacto.verificado, datetime.now()
            ))

            if conn:
                conn.commit()
        finally:
            if conn and should_close:
                conn.close()

    def _obtener_contactos(self, cliente_id: str, cursor: Optional[sqlite3.Cursor] = None) -> List[ContactoSchema]:
        """Obtener contactos de un cliente"""
        should_close = cursor is None

        if cursor is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        else:
            conn = None

        try:
            cursor.execute("SELECT * FROM contactos WHERE cliente_id = ?", (cliente_id,))
            rows = cursor.fetchall()
            return [ContactoSchema(**dict(row)) for row in rows]
        finally:
            if conn and should_close:
                conn.close()

    # =====================================================
    # OPERACIONES ACTIVIDADES
    # =====================================================

    def crear_actividad(self, cliente_id: str, actividad: ActividadSchema) -> ActividadSchema:
        """Crear actividad para cliente"""
        actividad_id = f"act_{uuid.uuid4().hex[:12]}"

        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO actividades (
                id, cliente_id, tipo, titulo, descripcion, fecha, completada, responsable, notas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                actividad_id, cliente_id, actividad.tipo, actividad.titulo,
                actividad.descripcion, actividad.fecha, actividad.completada,
                actividad.responsable, actividad.notas
            ))

            conn.commit()
            logger.info(f"[OK] Actividad creada para cliente {cliente_id}: {actividad_id}")

            actividad.id = actividad_id
            return actividad
        finally:
            conn.close()

    def _obtener_actividades(
        self,
        cliente_id: str,
        cursor: Optional[sqlite3.Cursor] = None,
        limit: int = 10
    ) -> List[ActividadSchema]:
        """Obtener actividades de un cliente"""
        should_close = cursor is None

        if cursor is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        else:
            conn = None

        try:
            cursor.execute(
                "SELECT * FROM actividades WHERE cliente_id = ? ORDER BY fecha DESC LIMIT ?",
                (cliente_id, limit)
            )
            rows = cursor.fetchall()
            return [ActividadSchema(**dict(row)) for row in rows]
        finally:
            if conn and should_close:
                conn.close()

    # =====================================================
    # OPERACIONES OPORTUNIDADES
    # =====================================================

    def crear_oportunidad(self, cliente_id: str, oportunidad: OportunidadSchema) -> OportunidadSchema:
        """Crear oportunidad para cliente"""
        oportunidad_id = f"opp_{uuid.uuid4().hex[:12]}"

        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        try:
            productos_json = json.dumps(oportunidad.productos) if oportunidad.productos else None

            cursor.execute("""
            INSERT INTO oportunidades (
                id, cliente_id, titulo, descripcion, estado, valor_estimado,
                probabilidad_cierre, fecha_cierre_esperada, productos, notas,
                fecha_creacion, fecha_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                oportunidad_id, cliente_id, oportunidad.titulo, oportunidad.descripcion,
                oportunidad.estado, oportunidad.valor_estimado, oportunidad.probabilidad_cierre,
                oportunidad.fecha_cierre_esperada, productos_json, oportunidad.notas,
                datetime.now(), datetime.now()
            ))

            conn.commit()
            logger.info(f"[OK] Oportunidad creada para cliente {cliente_id}: {oportunidad_id}")

            oportunidad.id = oportunidad_id
            return oportunidad
        finally:
            conn.close()

    def _obtener_oportunidades(self, cliente_id: str, cursor: Optional[sqlite3.Cursor] = None) -> List[OportunidadSchema]:
        """Obtener oportunidades abiertas de un cliente"""
        should_close = cursor is None

        if cursor is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        else:
            conn = None

        try:
            cursor.execute(
                "SELECT * FROM oportunidades WHERE cliente_id = ? AND estado != 'ganada' AND estado != 'perdida'",
                (cliente_id,)
            )
            rows = cursor.fetchall()

            oportunidades = []
            for row in rows:
                row_dict = dict(row)
                if row_dict['productos']:
                    row_dict['productos'] = json.loads(row_dict['productos'])
                oportunidades.append(OportunidadSchema(**row_dict))

            return oportunidades
        finally:
            if conn and should_close:
                conn.close()

    # =====================================================
    # ESTADÍSTICAS
    # =====================================================

    def obtener_resumen_crm(self) -> ResumenCRM:
        """Obtener resumen general del CRM"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        try:
            # Total clientes
            cursor.execute("SELECT COUNT(*) FROM clientes")
            total_clientes = cursor.fetchone()[0]

            # Clientes activos
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE estado = 'activo'")
            clientes_activos = cursor.fetchone()[0]

            # Clientes nuevos este mes
            cursor.execute("""
            SELECT COUNT(*) FROM clientes 
            WHERE strftime('%Y-%m', fecha_creacion) = strftime('%Y-%m', 'now')
            """)
            clientes_nuevos_mes = cursor.fetchone()[0]

            # Total facturado
            cursor.execute("SELECT COALESCE(SUM(total_facturado), 0) FROM clientes")
            valor_total_facturado = cursor.fetchone()[0]

            # Oportunidades abiertas
            cursor.execute("""
            SELECT COALESCE(SUM(valor_estimado), 0) FROM oportunidades
            WHERE estado NOT IN ('ganada', 'perdida')
            """)
            valor_oportunidades_abiertas = cursor.fetchone()[0]

            # Promedio días pago
            cursor.execute("""
            SELECT COALESCE(AVG(dias_desde_ultimo_contacto), 0) FROM clientes
            WHERE dias_desde_ultimo_contacto IS NOT NULL
            """)
            promedio_dias_pago = cursor.fetchone()[0]

            # Clientes morosos
            cursor.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE estado = 'activo' AND tasa_pagos_a_tiempo IS NOT NULL
            AND tasa_pagos_a_tiempo < 80
            """)
            clientes_morosos = cursor.fetchone()[0]

            # Actividades pendientes
            cursor.execute("SELECT COUNT(*) FROM actividades WHERE completada = 0")
            actividades_pendientes = cursor.fetchone()[0]

            # Oportunidades próximas a cerrar
            cursor.execute("""
            SELECT COUNT(*) FROM oportunidades
            WHERE estado NOT IN ('ganada', 'perdida')
            AND fecha_cierre_esperada <= datetime('now', '+7 days')
            """)
            oportunidades_proximas_cerrar = cursor.fetchone()[0]

            return ResumenCRM(
                total_clientes=total_clientes,
                clientes_activos=clientes_activos,
                clientes_nuevos_mes=clientes_nuevos_mes,
                valor_total_facturado=valor_total_facturado,
                valor_oportunidades_abiertas=valor_oportunidades_abiertas,
                promedio_dias_pago=promedio_dias_pago,
                clientes_morosos=clientes_morosos,
                actividades_pendientes=actividades_pendientes,
                oportunidades_proximas_cerrar=oportunidades_proximas_cerrar
            )
        finally:
            conn.close()
