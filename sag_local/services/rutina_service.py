import datetime
import storage as db
from models.rutina import Rutina


class RutinaService:
    """Rutinas en memoria (RF-14, RF-15, RF-27)."""

    def registrar(
        self,
        fecha: datetime.date,
        objetivo: str,
        observaciones: str | None,
        codigo_cliente: int,
        codigo_empleado: int,
    ) -> int:
        rid = db.next_id("rutina")
        db.rutinas.append({
            "codigo_rutina": rid,
            "fecha": fecha,
            "objetivo": objetivo,
            "observaciones": observaciones,
            "codigo_cliente": codigo_cliente,
            "codigo_empleado": codigo_empleado,
        })
        return rid

    def editar(self, codigo_rutina: int, **campos) -> None:
        for r in db.rutinas:
            if r["codigo_rutina"] == codigo_rutina:
                r.update(campos)
                return

    def listar_por_entrenador(self, codigo_empleado: int) -> list[Rutina]:
        return [
            self._row_to_rutina(r)
            for r in sorted(db.rutinas, key=lambda x: x["fecha"], reverse=True)
            if r["codigo_empleado"] == codigo_empleado
        ]

    def historial_cliente(self, codigo_cliente: int) -> list[Rutina]:
        return [
            self._row_to_rutina(r)
            for r in sorted(db.rutinas, key=lambda x: x["fecha"], reverse=True)
            if r["codigo_cliente"] == codigo_cliente
        ]

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
