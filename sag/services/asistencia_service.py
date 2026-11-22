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
        """Verifica membresía vigente y registra la asistencia. (RF-11)

        Devuelve el codigo_asistencia generado.
        Lanza ValueError si el cliente no tiene membresía activa.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)

            # Verificar membresía vigente
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
                raise ValueError(
                    "El cliente no tiene una membresía vigente."
                )

            ahora = datetime.datetime.now()
            cursor.execute(
                """
                INSERT INTO ASISTENCIA_GYM (fecha, hora, codigo_cliente, codigo_rutina)
                VALUES (%s, %s, %s, %s)
                """,
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
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM ASISTENCIA_GYM WHERE codigo_cliente = %s"
            params: list = [codigo_cliente]
            if fecha_desde:
                query += " AND fecha >= %s"
                params.append(fecha_desde)
            if fecha_hasta:
                query += " AND fecha <= %s"
                params.append(fecha_hasta)
            query += " ORDER BY fecha DESC, hora DESC"
            cursor.execute(query, params)
            return [self._row_to_asistencia(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_asistencia(row: dict) -> AsistenciaGym:
        return AsistenciaGym(
            codigo_asistencia=row["codigo_asistencia"],
            fecha=row["fecha"],
            hora=row["hora"],
            codigo_cliente=row["codigo_cliente"],
            codigo_rutina=row.get("codigo_rutina"),
        )
