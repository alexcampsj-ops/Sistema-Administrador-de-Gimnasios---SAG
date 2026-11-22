import datetime
import storage as db
from models.membresia import Membresia


class ReporteService:
    """6 reportes administrativos sobre los datos en memoria (RF-28)."""

    def ingresos_por_periodo(
        self,
        fecha_desde: datetime.date,
        fecha_hasta: datetime.date,
    ) -> list[dict]:
        totales: dict[str, dict] = {}
        for p in db.pagos:
            if fecha_desde <= p["fecha"] <= fecha_hasta:
                metodo = next(
                    (m["nombre"] for m in db.metodos_pago if m["codigo_metodo"] == p["codigo_metodo"]),
                    str(p["codigo_metodo"]),
                )
                if metodo not in totales:
                    totales[metodo] = {"metodo": metodo, "total": 0.0, "cantidad_pagos": 0}
                totales[metodo]["total"] += p["monto"]
                totales[metodo]["cantidad_pagos"] += 1
        return sorted(totales.values(), key=lambda x: x["total"], reverse=True)

    def membresias_por_estado(self) -> list[dict]:
        conteo: dict[str, int] = {}
        for m in db.membresias:
            conteo[m["estado"]] = conteo.get(m["estado"], 0) + 1
        return [{"estado": k, "cantidad": v} for k, v in conteo.items()]

    def clientes_activos_vencidos(self) -> list[dict]:
        resultado = []
        for m in db.membresias:
            if m["estado"] in (Membresia.ACTIVA, Membresia.VENCIDA):
                cliente = next(
                    (c for c in db.clientes if c["codigo_cliente"] == m["codigo_cliente"]),
                    None,
                )
                nombre = (
                    f"{cliente['nombre']} {cliente['apellido_paterno']}"
                    if cliente else str(m["codigo_cliente"])
                )
                resultado.append({
                    "cliente": nombre,
                    "estado": m["estado"],
                    "fecha_vencimiento": m["fecha_vencimiento"],
                })
        resultado.sort(key=lambda x: (x["estado"], x["cliente"]))
        return resultado

    def asistencia_por_periodo(
        self,
        fecha_desde: datetime.date,
        fecha_hasta: datetime.date,
    ) -> list[dict]:
        conteo: dict[datetime.date, int] = {}
        for a in db.asistencias_gym:
            if fecha_desde <= a["fecha"] <= fecha_hasta:
                conteo[a["fecha"]] = conteo.get(a["fecha"], 0) + 1
        return [
            {"fecha": k, "total_asistencias": v}
            for k, v in sorted(conteo.items())
        ]

    def ocupacion_clases(self) -> list[dict]:
        resultado = []
        for c in db.clases:
            pct = round(c["inscritos"] / c["cupo_maximo"] * 100, 1) if c["cupo_maximo"] else 0
            resultado.append({
                "nombre": c["nombre"],
                "dia": c["dia"],
                "inscritos": c["inscritos"],
                "cupo_maximo": c["cupo_maximo"],
                "ocupacion_pct": pct,
            })
        return sorted(resultado, key=lambda x: x["ocupacion_pct"], reverse=True)

    def clases_por_especialidad(self) -> list[dict]:
        conteo: dict[str, int] = {}
        for c in db.clases:
            esp = next(
                (e["nombre"] for e in db.especialidades if e["codigo_especialidad"] == c["codigo_especialidad"]),
                str(c["codigo_especialidad"]),
            )
            conteo[esp] = conteo.get(esp, 0) + 1
        return [
            {"especialidad": k, "total_clases": v}
            for k, v in sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        ]
