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
        """Registra la membresía y su pago en una sola transacción atómica.

        Pasos:
          1. Consulta duración y monto del tipo de membresía.
          2. Calcula la fecha de vencimiento sumando los días al inicio.
          3. Genera un código único con UUID.
          4. Inserta la membresía.
          5. Inserta el pago correspondiente.
          6. Confirma los dos inserts en un solo commit.

        Devuelve el código único de la membresía generado (ej. 'MEM-3A7F2B1C').
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)

            # Paso 1: obtener duración y monto del tipo de membresía
            cursor.execute(
                "SELECT duracion_dias, monto FROM TIPO_MEMBRESIA WHERE codigo_tipo = %s",
                (codigo_tipo,),
            )
            tipo = cursor.fetchone()
            if tipo is None:
                raise ValueError("Tipo de membresía no encontrado.")

            # Paso 2: calcular fecha de vencimiento
            # timedelta suma días al objeto date para obtener la fecha final
            fecha_vencimiento = fecha_inicio + datetime.timedelta(
                days=tipo["duracion_dias"]
            )
            # Paso 3: generar código único para la membresía
            codigo_membresia = self._generar_codigo()

            # Paso 4: insertar la membresía con estado ACTIVA
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
            # Paso 5: insertar el pago con el monto del tipo de membresía
            cursor.execute(
                """
                INSERT INTO PAGO (fecha, monto, codigo_membresia, codigo_metodo)
                VALUES (%s, %s, %s, %s)
                """,
                (fecha_inicio, tipo["monto"], codigo_membresia, codigo_metodo),
            )
            # Paso 6: confirmar ambos inserts en una sola transacción
            conn.commit()
            return codigo_membresia
        except Exception:
            # Si algo falla, deshace ambos inserts (membresía y pago)
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
        """Crea una nueva membresía cuya vigencia arranca al vencer la actual.

        Lógica de fecha de inicio:
          - Si la membresía actual AÚN está vigente, la nueva comienza cuando
            vence la actual (para no perder días pagados).
          - Si ya venció, la nueva comienza hoy.
          Esto se logra con max(fecha_vencimiento_actual, hoy).

        Devuelve el código de la nueva membresía.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Consulta la membresía actual junto con los datos de su tipo
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
            # max() elige la fecha mayor: si aún no vence, usa el vencimiento;
            # si ya venció, usa hoy para que la nueva empiece de inmediato
            fecha_inicio_nueva = max(actual["fecha_vencimiento"], hoy)
            fecha_vencimiento_nueva = fecha_inicio_nueva + datetime.timedelta(
                days=actual["duracion_dias"]
            )
            nuevo_codigo = self._generar_codigo()

            # Inserta la nueva membresía con el mismo cliente y tipo que la actual
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
            # Inserta el pago de la renovación con la fecha de hoy
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
        """Cancela una membresía registrando la fecha y el motivo de cancelación.

        Cambia el estado a CANCELADA y guarda la fecha actual y el motivo.
        No elimina el registro para conservar el historial.
        """
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
        """Busca membresías por código exacto, nombre/apellido o celular del cliente.

        Hace un JOIN con CLIENTE y CELULAR para permitir búsqueda por datos del cliente.
        """
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
        """Devuelve el historial de pagos de una membresía, ordenado por fecha."""
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
        """Actualiza a 'vencida' todas las membresías activas cuya fecha ya pasó.

        Usa CURDATE() de MySQL para comparar contra la fecha del servidor de BD.
        Devuelve el número de filas afectadas (membresías actualizadas).
        """
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
            # rowcount indica cuántas filas fueron modificadas por el UPDATE
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    @staticmethod
    def _generar_codigo() -> str:
        """Genera un código único de membresía con el formato 'MEM-XXXXXXXX'.

        uuid4() crea un UUID aleatorio; .hex[:8] toma los primeros 8 caracteres
        hexadecimales; .upper() los convierte a mayúsculas.
        Ejemplo de resultado: 'MEM-3A7F2B1C'
        """
        return "MEM-" + uuid.uuid4().hex[:8].upper()

    @staticmethod
    def _row_to_membresia(row: dict) -> Membresia:
        """Convierte un diccionario (fila de la BD) en un objeto Membresia.

        Usa .get() para los campos opcionales (fecha_cancelacion, motivo_cancelacion)
        que pueden ser NULL en la base de datos.
        """
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
