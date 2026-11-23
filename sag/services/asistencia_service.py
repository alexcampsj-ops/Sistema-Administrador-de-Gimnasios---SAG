import datetime
from config.db import get_connection
from models.asistencia_gym import AsistenciaGym
from models.membresia import Membresia


class AsistenciaService:
    """Registro y consulta de asistencias al gimnasio (RF-11, RF-16, RF-27)."""

    def registrar(
        self,
        codigo_cliente: int,
        codigo_rutina: int | None = None,
    ) -> int:
        """Verifica membresía vigente y registra la entrada del cliente (RF-11).

        Antes de guardar la asistencia, consulta si el cliente tiene al menos
        una membresía con estado ACTIVA cuya fecha de vencimiento sea hoy o posterior.
        Si no la tiene, lanza ValueError para que la vista muestre el error.

        El parámetro codigo_rutina es opcional: si el cliente viene a seguir
        una rutina específica, se puede registrar cuál.

        Devuelve el codigo_asistencia generado por AUTO_INCREMENT.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)

            # Verificar que el cliente tenga membresía activa y vigente
            # CURDATE() devuelve la fecha actual del servidor MySQL
            # LIMIT 1 optimiza la consulta: solo necesitamos saber si existe una
            cursor.execute(
                """
                SELECT codigo_membresia FROM MEMBRESIA
                WHERE codigo_cliente = %s
                  AND estado = %s
                  AND fecha_vencimiento >= CURDATE()
                LIMIT 1
                """,
                (codigo_cliente, Membresia.ACTIVA),
            )
            if cursor.fetchone() is None:
                # No hay membresía activa; no se permite el acceso
                raise ValueError(
                    "El cliente no tiene una membresía vigente."
                )

            # Captura fecha y hora actuales del servidor de aplicación
            ahora = datetime.datetime.now()
            cursor.execute(
                """
                INSERT INTO ASISTENCIA_GYM (fecha, hora, codigo_cliente, codigo_rutina)
                VALUES (%s, %s, %s, %s)
                """,
                # ahora.date() extrae solo la parte de fecha (sin hora)
                # ahora.time() extrae solo la parte de hora (sin fecha)
                (ahora.date(), ahora.time(), codigo_cliente, codigo_rutina),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def listar_por_cliente(
        self,
        codigo_cliente: int,
        fecha_desde: datetime.date | None = None,
        fecha_hasta: datetime.date | None = None,
    ) -> list[AsistenciaGym]:
        """Devuelve el historial de asistencias de un cliente, con filtro de fechas opcional.

        Las fechas son parámetros opcionales: si no se pasan, devuelve todas.
        La consulta se construye dinámicamente agregando condiciones solo si se proporcionan.
        Los resultados se ordenan de más reciente a más antiguo.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Base de la consulta; se le agregarán condiciones según los filtros
            query = "SELECT * FROM ASISTENCIA_GYM WHERE codigo_cliente = %s"
            params: list = [codigo_cliente]
            if fecha_desde:
                # Agrega filtro de fecha mínima solo si se proporcionó
                query += " AND fecha >= %s"
                params.append(fecha_desde)
            if fecha_hasta:
                # Agrega filtro de fecha máxima solo si se proporcionó
                query += " AND fecha <= %s"
                params.append(fecha_hasta)
            # Ordena de más reciente a más antigua (DESC = descendente)
            query += " ORDER BY fecha DESC, hora DESC"
            cursor.execute(query, params)
            # Convierte cada fila en un objeto AsistenciaGym
            return [self._row_to_asistencia(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_asistencia(row: dict) -> AsistenciaGym:
        """Convierte un diccionario (fila de la BD) en un objeto AsistenciaGym.

        Usa .get() para codigo_rutina porque puede ser NULL (campo opcional).
        """
        return AsistenciaGym(
            codigo_asistencia=row["codigo_asistencia"],
            fecha=row["fecha"],
            hora=row["hora"],
            codigo_cliente=row["codigo_cliente"],
            codigo_rutina=row.get("codigo_rutina"),
        )
