import datetime
import uuid
from config.db import get_connection
from models.membresia import Membresia
from models.pago import Pago


class MembresiaService:
    """Venta, renovación, cancelación y consulta de membresías (RF-06 a RF-09, RF-22)."""

    # ------------------------------------------------------------------
    # Venta
    # ------------------------------------------------------------------
    def vender(
        self,
        codigo_cliente: int,
        codigo_tipo: int,
        fecha_inicio: datetime.date,
        codigo_metodo: int,
        codigo_empleado: int,
    ) -> str:
        """Registra la membresía y su pago en una sola transacción.

        Devuelve el código único de la membresía generado.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)

            # Obtener duración y monto del tipo
            cursor.execute(
                "SELECT duracion_dias, monto FROM TIPO_MEMBRESIA WHERE codigo_tipo = %s",
                (codigo_tipo,),
            )
            tipo = cursor.fetchone()
            if tipo is None:
                raise ValueError("Tipo de membresía no encontrado.")

            fecha_vencimiento = fecha_inicio + datetime.timedelta(
                days=tipo["duracion_dias"]
            )
            codigo_membresia = self._generar_codigo()

            cursor.execute(
                """
                INSERT INTO MEMBRESIA
                    (codigo_membresia, fecha_inicio, fecha_vencimiento,
                     estado, codigo_cliente, codigo_tipo, codigo_empleado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (codigo_membresia, fecha_inicio, fecha_vencimiento,
                 Membresia.ACTIVA, codigo_cliente, codigo_tipo, codigo_empleado),
            )
            cursor.execute(
                """
                INSERT INTO PAGO (fecha, monto, codigo_membresia, codigo_metodo)
                VALUES (%s, %s, %s, %s)
                """,
                (fecha_inicio, tipo["monto"], codigo_membresia, codigo_metodo),
            )
            conn.commit()
            return codigo_membresia
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Renovación
    # ------------------------------------------------------------------
    def renovar(
        self,
        codigo_membresia_actual: str,
        codigo_metodo: int,
        codigo_empleado: int,
    ) -> str:
        """Crea una nueva membresía cuya vigencia arranca al vencer la actual."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT m.*, t.duracion_dias, t.monto
                FROM MEMBRESIA m
                INNER JOIN TIPO_MEMBRESIA t ON m.codigo_tipo = t.codigo_tipo
                WHERE m.codigo_membresia = %s
                """,
                (codigo_membresia_actual,),
            )
            actual = cursor.fetchone()
            if actual is None:
                raise ValueError("Membresía no encontrada.")

            hoy = datetime.date.today()
            fecha_inicio_nueva = max(actual["fecha_vencimiento"], hoy)
            fecha_vencimiento_nueva = fecha_inicio_nueva + datetime.timedelta(
                days=actual["duracion_dias"]
            )
            nuevo_codigo = self._generar_codigo()

            cursor.execute(
                """
                INSERT INTO MEMBRESIA
                    (codigo_membresia, fecha_inicio, fecha_vencimiento,
                     estado, codigo_cliente, codigo_tipo, codigo_empleado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (nuevo_codigo, fecha_inicio_nueva, fecha_vencimiento_nueva,
                 Membresia.ACTIVA, actual["codigo_cliente"],
                 actual["codigo_tipo"], codigo_empleado),
            )
            cursor.execute(
                """
                INSERT INTO PAGO (fecha, monto, codigo_membresia, codigo_metodo)
                VALUES (%s, %s, %s, %s)
                """,
                (hoy, actual["monto"], nuevo_codigo, codigo_metodo),
            )
            conn.commit()
            return nuevo_codigo
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Cancelación
    # ------------------------------------------------------------------
    def cancelar(self, codigo_membresia: str, motivo: str) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE MEMBRESIA
                SET estado = %s, fecha_cancelacion = %s, motivo_cancelacion = %s
                WHERE codigo_membresia = %s
                """,
                (Membresia.CANCELADA, datetime.date.today(),
                 motivo, codigo_membresia),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Consulta
    # ------------------------------------------------------------------
    def buscar(self, termino: str) -> list[Membresia]:
        """Busca por código de membresía, nombre o celular del cliente."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT m.*
                FROM MEMBRESIA m
                INNER JOIN CLIENTE c ON m.codigo_cliente = c.codigo_cliente
                LEFT JOIN CELULAR cel ON c.codigo_cliente = cel.codigo_cliente
                WHERE m.codigo_membresia = %s
                   OR c.nombre LIKE %s
                   OR c.apellido_paterno LIKE %s
                   OR cel.numero = %s
                """,
                (termino, f"%{termino}%", f"%{termino}%", termino),
            )
            return [self._row_to_membresia(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def obtener_pagos(self, codigo_membresia: str) -> list[Pago]:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM PAGO WHERE codigo_membresia = %s ORDER BY fecha",
                (codigo_membresia,),
            )
            return [
                Pago(r["codigo_pago"], r["fecha"], r["monto"],
                     r["codigo_membresia"], r["codigo_metodo"])
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def marcar_vencidas(self) -> int:
        """Actualiza a 'vencida' las membresías cuya fecha ya pasó. Devuelve el nº afectado."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE MEMBRESIA
                SET estado = %s
                WHERE estado = %s AND fecha_vencimiento < CURDATE()
                """,
                (Membresia.VENCIDA, Membresia.ACTIVA),
            )
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    @staticmethod
    def _generar_codigo() -> str:
        return "MEM-" + uuid.uuid4().hex[:8].upper()

    @staticmethod
    def _row_to_membresia(row: dict) -> Membresia:
        return Membresia(
            codigo_membresia=row["codigo_membresia"],
            fecha_inicio=row["fecha_inicio"],
            fecha_vencimiento=row["fecha_vencimiento"],
            estado=row["estado"],
            fecha_cancelacion=row.get("fecha_cancelacion"),
            motivo_cancelacion=row.get("motivo_cancelacion"),
            codigo_cliente=row["codigo_cliente"],
            codigo_tipo=row["codigo_tipo"],
            codigo_empleado=row["codigo_empleado"],
        )
