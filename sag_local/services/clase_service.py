import datetime
import storage as db
from models.clase import Clase
from models.inscripcion_clase import InscripcionClase


class ClaseService:
    """Gestión de clases e inscripciones en memoria (RF-10, RF-13, RF-24–26)."""

    def listar_publicas_activas(self) -> list[Clase]:
        return [
            self._row_to_clase(c)
            for c in db.clases
            if c["es_publica"] and c["estado"]
        ]

    def inscribir(
        self,
        codigo_cliente: int,
        codigo_clase: int,
        observaciones: str | None = None,
    ) -> None:
        clase = next((c for c in db.clases if c["codigo_clase"] == codigo_clase), None)
        if clase is None:
            raise ValueError("Clase no encontrada.")
        if not clase["estado"]:
            raise ValueError("La clase no está activa.")
        if not clase["es_publica"]:
            raise ValueError("La clase no es pública.")
        if clase["inscritos"] >= clase["cupo_maximo"]:
            raise ValueError("La clase no tiene lugares disponibles.")

        ya_inscrito = any(
            i for i in db.inscripciones_clase
            if i["codigo_cliente"] == codigo_cliente
            and i["codigo_clase"] == codigo_clase
            and i["estado"] == InscripcionClase.ACTIVA
        )
        if ya_inscrito:
            raise ValueError("El cliente ya está inscrito en esta clase.")

        iid = db.next_id("inscripcion_clase")
        db.inscripciones_clase.append({
            "codigo_inscripcion": iid,
            "fecha": datetime.date.today(),
            "estado": InscripcionClase.ACTIVA,
            "observaciones": observaciones,
            "codigo_cliente": codigo_cliente,
            "codigo_clase": codigo_clase,
        })
        clase["inscritos"] += 1

    def cambiar_estado_inscripcion(
        self, codigo_inscripcion: int, nuevo_estado: str
    ) -> None:
        ins = next(
            (i for i in db.inscripciones_clase if i["codigo_inscripcion"] == codigo_inscripcion),
            None,
        )
        if ins is None:
            raise ValueError("Inscripción no encontrada.")

        clase = next(c for c in db.clases if c["codigo_clase"] == ins["codigo_clase"])

        if nuevo_estado == InscripcionClase.ACTIVA:
            if clase["inscritos"] >= clase["cupo_maximo"]:
                raise ValueError("No hay lugares para reactivar la inscripción.")
            if ins["estado"] != InscripcionClase.ACTIVA:
                clase["inscritos"] += 1
        elif ins["estado"] == InscripcionClase.ACTIVA:
            clase["inscritos"] -= 1

        ins["estado"] = nuevo_estado

    def listar_por_empleado(self, codigo_empleado: int) -> list[Clase]:
        return [
            self._row_to_clase(c)
            for c in db.clases
            if c["codigo_empleado"] == codigo_empleado
        ]

    def listar_inscritos(self, codigo_clase: int) -> list[InscripcionClase]:
        return [
            self._row_to_inscripcion(i)
            for i in db.inscripciones_clase
            if i["codigo_clase"] == codigo_clase
        ]

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
            es_publica=row["es_publica"],
            estado=row["estado"],
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
