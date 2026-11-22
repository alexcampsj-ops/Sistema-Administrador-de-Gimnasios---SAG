import datetime
import storage as db
from models.asistencia_gym import AsistenciaGym
from models.membresia import Membresia


class AsistenciaService:
    """Asistencias en memoria (RF-11, RF-16, RF-27)."""

    def registrar(
        self,
        codigo_cliente: int,
        codigo_rutina: int | None = None,
    ) -> int:
        hoy = datetime.date.today()
        tiene_vigente = any(
            m for m in db.membresias
            if m["codigo_cliente"] == codigo_cliente
            and m["estado"] == Membresia.ACTIVA
            and m["fecha_vencimiento"] >= hoy
        )
        if not tiene_vigente:
            raise ValueError("El cliente no tiene una membresía vigente.")

        ahora = datetime.datetime.now()
        aid = db.next_id("asistencia_gym")
        db.asistencias_gym.append({
            "codigo_asistencia": aid,
            "fecha": ahora.date(),
            "hora": ahora.time().replace(microsecond=0),
            "codigo_cliente": codigo_cliente,
            "codigo_rutina": codigo_rutina,
        })
        return aid

    def listar_por_cliente(
        self,
        codigo_cliente: int,
        fecha_desde: datetime.date | None = None,
        fecha_hasta: datetime.date | None = None,
    ) -> list[AsistenciaGym]:
        resultado = [
            a for a in db.asistencias_gym
            if a["codigo_cliente"] == codigo_cliente
            and (fecha_desde is None or a["fecha"] >= fecha_desde)
            and (fecha_hasta is None or a["fecha"] <= fecha_hasta)
        ]
        resultado.sort(key=lambda x: (x["fecha"], x["hora"]), reverse=True)
        return [
            AsistenciaGym(
                a["codigo_asistencia"], a["fecha"], a["hora"],
                a["codigo_cliente"], a.get("codigo_rutina"),
            )
            for a in resultado
        ]
