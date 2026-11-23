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
        """Inserta una rutina nueva creada por el entrenador para un cliente.

        Devuelve el codigo_rutina generado por AUTO_INCREMENT.
        observaciones es opcional (puede ser None, que MySQL guarda como NULL).
        """
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
            # Devuelve el ID generado automáticamente por MySQL
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def editar(self, codigo_rutina: int, **campos) -> None:
        """Actualiza solo los campos indicados de una rutina (actualización parcial).

        Construye el UPDATE dinámicamente igual que en ClienteService y EmpleadoService.
        Ejemplo: editar(5, objetivo="Mejorar resistencia", observaciones="Nuevo plan")
        """
        if not campos:
            return
        # Construye la parte SET dinámicamente: "objetivo = %s, observaciones = %s"
        set_clause = ", ".join(f"{col} = %s" for col in campos)
        # Los valores van primero; el ID de la rutina va al final para el WHERE
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
        """Devuelve todas las rutinas creadas por un entrenador, de más reciente a más antigua."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # ORDER BY fecha DESC: la rutina más reciente aparece primero
            cursor.execute(
                "SELECT * FROM RUTINA WHERE codigo_empleado = %s ORDER BY fecha DESC",
                (codigo_empleado,),
            )
            return [self._row_to_rutina(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def historial_cliente(self, codigo_cliente: int) -> list[Rutina]:
        """Devuelve el historial completo de rutinas de un cliente, de más reciente a más antigua."""
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
        """Convierte un diccionario (fila de la BD) en un objeto Rutina.

        Usa .get() para observaciones porque puede ser NULL en la base de datos.
        """
        return Rutina(
            codigo_rutina=row["codigo_rutina"],
            fecha=row["fecha"],
            objetivo=row["objetivo"],
            observaciones=row.get("observaciones"),
            codigo_cliente=row["codigo_cliente"],
            codigo_empleado=row["codigo_empleado"],
        )
