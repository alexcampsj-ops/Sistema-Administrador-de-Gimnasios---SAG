import datetime
from config.db import get_connection
from models.clase import Clase
from models.inscripcion_clase import InscripcionClase


class ClaseService:
    """Gestión de clases e inscripciones (RF-10, RF-13, RF-24 a RF-26)."""

    def listar_publicas_activas(self) -> list[Clase]:
        """Devuelve las clases que son públicas (es_publica=1) y están activas (estado=1).

        La recepcionista usa este método para mostrar al cliente qué clases
        están disponibles para inscribirse.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM CLASE WHERE es_publica = 1 AND estado = 1"
            )
            return [self._row_to_clase(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def inscribir(
        self,
        codigo_cliente: int,
        codigo_clase: int,
        observaciones: str | None = None,
    ) -> None:
        """Inscribe a un cliente en una clase grupal (RF-10).

        Realiza 4 validaciones antes de insertar:
          1. La clase debe existir.
          2. La clase debe estar activa (estado=1).
          3. La clase debe ser pública (es_publica=1).
          4. El número de inscritos no debe haber alcanzado el cupo máximo.
          5. El cliente no debe estar ya inscrito (con estado ACTIVA) en esa clase.

        Si todas las validaciones pasan, inserta la inscripción y suma 1
        al contador de inscritos de la clase en la misma transacción.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)

            # Verificar existencia y estado de la clase
            cursor.execute(
                "SELECT * FROM CLASE WHERE codigo_clase = %s", (codigo_clase,)
            )
            clase = cursor.fetchone()
            if clase is None:
                raise ValueError("Clase no encontrada.")
            if not clase["estado"]:
                raise ValueError("La clase no está activa.")
            if not clase["es_publica"]:
                raise ValueError("La clase no es pública.")
            if clase["inscritos"] >= clase["cupo_maximo"]:
                raise ValueError("La clase no tiene lugares disponibles.")

            # Verificar que el cliente no esté ya inscrito activamente
            cursor.execute(
                """
                SELECT 1 FROM INSCRIPCION_CLASE
                WHERE codigo_cliente = %s AND codigo_clase = %s AND estado = %s
                """,
                (codigo_cliente, codigo_clase, InscripcionClase.ACTIVA),
            )
            if cursor.fetchone():
                raise ValueError("El cliente ya está inscrito en esta clase.")

            # Insertar la inscripción con estado ACTIVA y fecha actual
            cursor.execute(
                """
                INSERT INTO INSCRIPCION_CLASE
                    (fecha, estado, observaciones, codigo_cliente, codigo_clase)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (datetime.date.today(), InscripcionClase.ACTIVA,
                 observaciones, codigo_cliente, codigo_clase),
            )
            # Incrementar el contador de inscritos en la tabla CLASE
            # Esto se hace en la misma transacción para mantener consistencia
            cursor.execute(
                "UPDATE CLASE SET inscritos = inscritos + 1 WHERE codigo_clase = %s",
                (codigo_clase,),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def cambiar_estado_inscripcion(
        self, codigo_inscripcion: int, nuevo_estado: str
    ) -> None:
        """Activa o cancela una inscripción existente (RF-26).

        Al cambiar el estado también actualiza el contador de inscritos de la clase:
          - Si se REACTIVA una inscripción: verifica que haya cupo y suma 1.
          - Si se CANCELA una inscripción activa: resta 1.
          - Si se cancela una que ya estaba cancelada: no modifica el contador.
        Todo ocurre en una sola transacción.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Obtener la inscripción actual para saber su estado actual y clase
            cursor.execute(
                "SELECT * FROM INSCRIPCION_CLASE WHERE codigo_inscripcion = %s",
                (codigo_inscripcion,),
            )
            ins = cursor.fetchone()
            if ins is None:
                raise ValueError("Inscripción no encontrada.")

            if nuevo_estado == InscripcionClase.ACTIVA:
                # Al reactivar: verificar que la clase aún tenga lugares
                cursor.execute(
                    "SELECT inscritos, cupo_maximo FROM CLASE WHERE codigo_clase = %s",
                    (ins["codigo_clase"],),
                )
                clase = cursor.fetchone()
                if clase["inscritos"] >= clase["cupo_maximo"]:
                    raise ValueError("No hay lugares para reactivar la inscripción.")
                # Suma 1 al contador porque se está reactivando un inscrito
                cursor.execute(
                    "UPDATE CLASE SET inscritos = inscritos + 1 WHERE codigo_clase = %s",
                    (ins["codigo_clase"],),
                )
            elif ins["estado"] == InscripcionClase.ACTIVA:
                # Al cancelar: solo resta 1 si la inscripción estaba activa
                # (evita restar doble si ya estaba cancelada)
                cursor.execute(
                    "UPDATE CLASE SET inscritos = inscritos - 1 WHERE codigo_clase = %s",
                    (ins["codigo_clase"],),
                )

            # Actualiza el estado de la inscripción
            cursor.execute(
                "UPDATE INSCRIPCION_CLASE SET estado = %s WHERE codigo_inscripcion = %s",
                (nuevo_estado, codigo_inscripcion),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def listar_por_empleado(self, codigo_empleado: int) -> list[Clase]:
        """Devuelve todas las clases asignadas a un empleado (entrenador).

        El entrenador usa este método para ver sus propias clases.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM CLASE WHERE codigo_empleado = %s",
                (codigo_empleado,),
            )
            return [self._row_to_clase(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def listar_inscritos(self, codigo_clase: int) -> list[InscripcionClase]:
        """Devuelve todas las inscripciones (activas y canceladas) de una clase."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM INSCRIPCION_CLASE WHERE codigo_clase = %s",
                (codigo_clase,),
            )
            return [self._row_to_inscripcion(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_clase(row: dict) -> Clase:
        """Convierte un diccionario (fila de la BD) en un objeto Clase.

        bool() convierte los campos TINYINT es_publica y estado a True/False.
        """
        return Clase(
            codigo_clase=row["codigo_clase"],
            nombre=row["nombre"],
            dia=row["dia"],
            hora_inicio=row["hora_inicio"],
            hora_fin=row["hora_fin"],
            cupo_maximo=row["cupo_maximo"],
            inscritos=row["inscritos"],
            es_publica=bool(row["es_publica"]),
            estado=bool(row["estado"]),
            codigo_especialidad=row["codigo_especialidad"],
            codigo_empleado=row["codigo_empleado"],
        )

    @staticmethod
    def _row_to_inscripcion(row: dict) -> InscripcionClase:
        """Convierte un diccionario (fila de la BD) en un objeto InscripcionClase.

        Usa .get() para observaciones porque es un campo opcional (puede ser NULL).
        """
        return InscripcionClase(
            codigo_inscripcion=row["codigo_inscripcion"],
            fecha=row["fecha"],
            estado=row["estado"],
            observaciones=row.get("observaciones"),
            codigo_cliente=row["codigo_cliente"],
            codigo_clase=row["codigo_clase"],
        )
