import datetime
from config.db import get_connection


class ReporteService:
    """Genera los 6 reportes administrativos del sistema (RF-28)."""

    def ingresos_por_periodo(
        self,
        fecha_desde: datetime.date,
        fecha_hasta: datetime.date,
    ) -> list[dict]:
        """Reporte 1: ingresos (pagos) agrupados por método de pago en un periodo."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT mp.nombre AS metodo, SUM(p.monto) AS total,
                       COUNT(*) AS cantidad_pagos
                FROM PAGO p
                INNER JOIN METODO_PAGO mp ON p.codigo_metodo = mp.codigo_metodo
                WHERE p.fecha BETWEEN %s AND %s
                GROUP BY mp.nombre
                ORDER BY total DESC
                """,
                (fecha_desde, fecha_hasta),
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def membresias_por_estado(self) -> list[dict]:
        """Reporte 2: cantidad de membresías agrupadas por estado."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT estado, COUNT(*) AS cantidad
                FROM MEMBRESIA
                GROUP BY estado
                """
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def clientes_activos_vencidos(self) -> list[dict]:
        """Reporte 3: clientes con membresía activa vs. vencida."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    c.codigo_cliente,
                    CONCAT(c.nombre,' ',c.apellido_paterno) AS cliente,
                    m.estado,
                    m.fecha_vencimiento
                FROM CLIENTE c
                INNER JOIN MEMBRESIA m ON c.codigo_cliente = m.codigo_cliente
                WHERE m.estado IN ('activa','vencida')
                ORDER BY m.estado, c.apellido_paterno
                """
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def asistencia_por_periodo(
        self,
        fecha_desde: datetime.date,
        fecha_hasta: datetime.date,
    ) -> list[dict]:
        """Reporte 4: asistencias diarias en el periodo."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT fecha, COUNT(*) AS total_asistencias
                FROM ASISTENCIA_GYM
                WHERE fecha BETWEEN %s AND %s
                GROUP BY fecha
                ORDER BY fecha
                """,
                (fecha_desde, fecha_hasta),
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def ocupacion_clases(self) -> list[dict]:
        """Reporte 5: inscritos vs. cupo máximo por clase."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT cl.nombre, cl.dia, cl.inscritos,
                       cl.cupo_maximo,
                       ROUND(cl.inscritos / cl.cupo_maximo * 100, 1) AS ocupacion_pct
                FROM CLASE cl
                ORDER BY ocupacion_pct DESC
                """
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def clases_por_especialidad(self) -> list[dict]:
        """Reporte 6: cantidad de clases por especialidad."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT e.nombre AS especialidad, COUNT(*) AS total_clases
                FROM CLASE cl
                INNER JOIN ESPECIALIDAD e ON cl.codigo_especialidad = e.codigo_especialidad
                GROUP BY e.nombre
                ORDER BY total_clases DESC
                """
            )
            return cursor.fetchall()
        finally:
            conn.close()
