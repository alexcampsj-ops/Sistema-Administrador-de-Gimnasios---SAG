import datetime
from config.db import get_connection
from models.rutina import Rutina


class RutinaService:
    """Registro y consulta de rutinas de entrenamiento (RF-14, RF-15, RF-27)."""

    def registrar(
        self,
        fecha: datetime.date,
        objetivo: str,
        observaciones: str | None,
        codigo_cliente: int,
        codigo_empleado: int,
    ) -> int:
        """Inserta una rutina nueva. Devuelve el codigo_rutina generado."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO RUTINA
                    (fecha, objetivo, observaciones, codigo_cliente, codigo_empleado)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (fecha, objetivo, observaciones, codigo_cliente, codigo_empleado),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def editar(self, codigo_rutina: int, **campos) -> None:
        if not campos:
            return
        set_clause = ", ".join(f"{col} = %s" for col in campos)
        valores = list(campos.values()) + [codigo_rutina]
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE RUTINA SET {set_clause} WHERE codigo_rutina = %s",
                valores,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def listar_por_entrenador(self, codigo_empleado: int) -> list[Rutina]:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM RUTINA WHERE codigo_empleado = %s ORDER BY fecha DESC",
                (codigo_empleado,),
            )
            return [self._row_to_rutina(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def historial_cliente(self, codigo_cliente: int) -> list[Rutina]:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM RUTINA WHERE codigo_cliente = %s ORDER BY fecha DESC",
                (codigo_cliente,),
            )
            return [self._row_to_rutina(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_rutina(row: dict) -> Rutina:
        return Rutina(
            codigo_rutina=row["codigo_rutina"],
            fecha=row["fecha"],
            objetivo=row["objetivo"],
            observaciones=row.get("observaciones"),
            codigo_cliente=row["codigo_cliente"],
            codigo_empleado=row["codigo_empleado"],
        )
