import storage as db
from models.empleado import Empleado
from models.horario import Horario


class EmpleadoService:
    """Empleados y horarios en memoria (RF-17, RF-18, RF-19)."""

    def agregar(
        self,
        nombre: str,
        usuario: str,
        contrasena: str,
        correo: str,
        codigo_rol: int,
    ) -> int:
        # Verificar unicidad de usuario y correo
        if any(e["usuario"] == usuario for e in db.empleados):
            raise ValueError(f"El usuario '{usuario}' ya existe.")
        if any(e["correo"] == correo for e in db.empleados):
            raise ValueError(f"El correo '{correo}' ya está registrado.")
        eid = db.next_id("empleado")
        db.empleados.append({
            "codigo_empleado": eid,
            "nombre": nombre,
            "usuario": usuario,
            "contrasena": contrasena,
            "correo": correo,
            "estado": True,
            "codigo_rol": codigo_rol,
        })
        return eid

    def editar(self, codigo_empleado: int, **campos) -> None:
        for e in db.empleados:
            if e["codigo_empleado"] == codigo_empleado:
                e.update(campos)
                return

    def cambiar_estado(self, codigo_empleado: int, estado: bool) -> None:
        self.editar(codigo_empleado, estado=estado)

    def listar(self) -> list[Empleado]:
        return [
            self._row_to_empleado(e)
            for e in sorted(db.empleados, key=lambda x: x["nombre"])
        ]

    def asignar_horario(
        self,
        codigo_empleado: int,
        dia: str,
        hora_inicio,
        hora_fin,
    ) -> None:
        # Reemplazar si ya existe el día para ese empleado
        for h in db.horarios:
            if h["codigo_empleado"] == codigo_empleado and h["dia"] == dia:
                h["hora_inicio"] = hora_inicio
                h["hora_fin"] = hora_fin
                return
        hid = db.next_id("horario")
        db.horarios.append({
            "codigo_horario": hid,
            "dia": dia,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "codigo_empleado": codigo_empleado,
        })

    def eliminar_horario(self, codigo_horario: int) -> None:
        db.horarios[:] = [h for h in db.horarios if h["codigo_horario"] != codigo_horario]

    def listar_horarios(self, codigo_empleado: int) -> list[Horario]:
        return [
            Horario(h["codigo_horario"], h["dia"], h["hora_inicio"],
                    h["hora_fin"], h["codigo_empleado"])
            for h in db.horarios
            if h["codigo_empleado"] == codigo_empleado
        ]

    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_empleado(row: dict) -> Empleado:
        return Empleado(
            codigo_empleado=row["codigo_empleado"],
            nombre=row["nombre"],
            usuario=row["usuario"],
            contrasena=row["contrasena"],
            correo=row["correo"],
            estado=row["estado"],
            codigo_rol=row["codigo_rol"],
        )
