import datetime
from config.db import get_connection
from models.clase import Clase
from models.inscripcion_clase import InscripcionClase


class ClaseService:
    """Gestión de clases e inscripciones (RF-10, RF-13, RF-24 a RF-26)."""

    def listar_publicas_activas(self) -> list[Clase]:
        """Devuelve las clases públicas y activas con lugares disponibles."""
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
        """Inscribe a un cliente en una clase (RF-10).

        Valida: clase activa + pública + con lugares + cliente no inscrito.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)

            # Verificar clase
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

            # Verificar que no esté ya inscrito
            cursor.execute(
                """
                SELECT 1 FROM INSCRIPCION_CLASE
                WHERE codigo_cliente = %s AND codigo_clase = %s AND estado = %s
                """,
                (codigo_cliente, codigo_clase, InscripcionClase.ACTIVA),
            )
            if cursor.fetchone():
                raise ValueError("El cliente ya está inscrito en esta clase.")

            # Registrar inscripción y actualizar contador
            cursor.execute(
                """
                INSERT INTO INSCRIPCION_CLASE
                    (fecha, estado, observaciones, codigo_cliente, codigo_clase)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (datetime.date.today(), InscripcionClase.ACTIVA,
                 observaciones, codigo_cliente, codigo_clase),
            )
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
        """Activa o cancela una inscripción; al reactivar verifica el cupo (RF-26)."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM INSCRIPCION_CLASE WHERE codigo_inscripcion = %s",
                (codigo_inscripcion,),
            )
            ins = cursor.fetchone()
            if ins is None:
                raise ValueError("Inscripción no encontrada.")

            if nuevo_estado == InscripcionClase.ACTIVA:
                cursor.execute(
                    "SELECT inscritos, cupo_maximo FROM CLASE WHERE codigo_clase = %s",
                    (ins["codigo_clase"],),
                )
                clase = cursor.fetchone()
                if clase["inscritos"] >= clase["cupo_maximo"]:
                    raise ValueError("No hay lugares para reactivar la inscripción.")
                cursor.execute(
                    "UPDATE CLASE SET inscritos = inscritos + 1 WHERE codigo_clase = %s",
                    (ins["codigo_clase"],),
                )
            elif ins["estado"] == InscripcionClase.ACTIVA:
                cursor.execute(
                    "UPDATE CLASE SET inscritos = inscritos - 1 WHERE codigo_clase = %s",
                    (ins["codigo_clase"],),
                )

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
        return InscripcionClase(
            codigo_inscripcion=row["codigo_inscripcion"],
            fecha=row["fecha"],
            estado=row["estado"],
            observaciones=row.get("observaciones"),
            codigo_cliente=row["codigo_cliente"],
            codigo_clase=row["codigo_clase"],
        )
