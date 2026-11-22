import datetime
import uuid
import storage as db
from models.membresia import Membresia
from models.pago import Pago


class MembresiaService:
    """Venta, renovación, cancelación y consulta en memoria (RF-06–09, RF-22)."""

    def vender(
        self,
        codigo_cliente: int,
        codigo_tipo: int,
        fecha_inicio: datetime.date,
        codigo_metodo: int,
        codigo_empleado: int,
    ) -> str:
        tipo = next((t for t in db.tipos_membresia if t["codigo_tipo"] == codigo_tipo), None)
        if tipo is None:
            raise ValueError("Tipo de membresía no encontrado.")

        fecha_vencimiento = fecha_inicio + datetime.timedelta(days=tipo["duracion_dias"])
        codigo_membresia = "MEM-" + uuid.uuid4().hex[:8].upper()

        db.membresias.append({
            "codigo_membresia": codigo_membresia,
            "fecha_inicio": fecha_inicio,
            "fecha_vencimiento": fecha_vencimiento,
            "estado": Membresia.ACTIVA,
            "fecha_cancelacion": None,
            "motivo_cancelacion": None,
            "codigo_cliente": codigo_cliente,
            "codigo_tipo": codigo_tipo,
            "codigo_empleado": codigo_empleado,
        })
        pid = db.next_id("pago")
        db.pagos.append({
            "codigo_pago": pid,
            "fecha": fecha_inicio,
            "monto": tipo["monto"],
            "codigo_membresia": codigo_membresia,
            "codigo_metodo": codigo_metodo,
        })
        return codigo_membresia

    def renovar(
        self,
        codigo_membresia_actual: str,
        codigo_metodo: int,
        codigo_empleado: int,
    ) -> str:
        actual = next(
            (m for m in db.membresias if m["codigo_membresia"] == codigo_membresia_actual),
            None,
        )
        if actual is None:
            raise ValueError("Membresía no encontrada.")

        tipo = next(t for t in db.tipos_membresia if t["codigo_tipo"] == actual["codigo_tipo"])
        hoy = datetime.date.today()
        fecha_inicio_nueva = max(actual["fecha_vencimiento"], hoy)
        fecha_vencimiento_nueva = fecha_inicio_nueva + datetime.timedelta(days=tipo["duracion_dias"])
        nuevo_codigo = "MEM-" + uuid.uuid4().hex[:8].upper()

        db.membresias.append({
            "codigo_membresia": nuevo_codigo,
            "fecha_inicio": fecha_inicio_nueva,
            "fecha_vencimiento": fecha_vencimiento_nueva,
            "estado": Membresia.ACTIVA,
            "fecha_cancelacion": None,
            "motivo_cancelacion": None,
            "codigo_cliente": actual["codigo_cliente"],
            "codigo_tipo": actual["codigo_tipo"],
            "codigo_empleado": codigo_empleado,
        })
        pid = db.next_id("pago")
        db.pagos.append({
            "codigo_pago": pid,
            "fecha": hoy,
            "monto": tipo["monto"],
            "codigo_membresia": nuevo_codigo,
            "codigo_metodo": codigo_metodo,
        })
        return nuevo_codigo

    def cancelar(self, codigo_membresia: str, motivo: str) -> None:
        for m in db.membresias:
            if m["codigo_membresia"] == codigo_membresia:
                m["estado"] = Membresia.CANCELADA
                m["fecha_cancelacion"] = datetime.date.today()
                m["motivo_cancelacion"] = motivo
                return
        raise ValueError("Membresía no encontrada.")

    def buscar(self, termino: str) -> list[Membresia]:
        termino_l = termino.lower()
        clientes_ids = {
            c["codigo_cliente"]
            for c in db.clientes
            if termino_l in c["nombre"].lower()
            or termino_l in c["apellido_paterno"].lower()
        }
        cel_ids = {c["codigo_cliente"] for c in db.celulares if c["numero"] == termino}
        clientes_ids |= cel_ids

        resultado = []
        for m in db.membresias:
            if (
                m["codigo_membresia"] == termino
                or m["codigo_cliente"] in clientes_ids
            ):
                resultado.append(self._row_to_membresia(m))
        return resultado

    def obtener_pagos(self, codigo_membresia: str) -> list[Pago]:
        return [
            Pago(p["codigo_pago"], p["fecha"], p["monto"],
                 p["codigo_membresia"], p["codigo_metodo"])
            for p in db.pagos
            if p["codigo_membresia"] == codigo_membresia
        ]

    def marcar_vencidas(self) -> int:
        hoy = datetime.date.today()
        count = 0
        for m in db.membresias:
            if m["estado"] == Membresia.ACTIVA and m["fecha_vencimiento"] < hoy:
                m["estado"] = Membresia.VENCIDA
                count += 1
        return count

    # ------------------------------------------------------------------
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
