from rich.console import Console
from rich.table import Table
from rich import box

from models.empleado import Empleado
from services.empleado_service import EmpleadoService
from services.cliente_service import ClienteService
from services.membresia_service import MembresiaService
from services.clase_service import ClaseService
from services.rutina_service import RutinaService
from services.asistencia_service import AsistenciaService
from services.reporte_service import ReporteService
from utils.validators import validar_fecha, validar_correo, confirmar
from utils.helpers import formatear_fecha, calcular_edad

console = Console()
_empleado_svc = EmpleadoService()
_cliente_svc = ClienteService()
_membresia_svc = MembresiaService()
_clase_svc = ClaseService()
_rutina_svc = RutinaService()
_asistencia_svc = AsistenciaService()
_reporte_svc = ReporteService()


def ejecutar(empleado: Empleado) -> None:
    """Menú principal del administrador (RF-17 a RF-28)."""
    opciones = {
        "1":  ("Empleados", _menu_empleados),
        "2":  ("Roles", _menu_roles),
        "3":  ("Horarios", _menu_horarios),
        "4":  ("Clientes", _menu_clientes),
        "5":  ("Tipos de membresía y beneficios", _menu_tipos_membresia),
        "6":  ("Membresías", _menu_membresias),
        "7":  ("Pagos y métodos de pago", _menu_pagos),
        "8":  ("Clases", _menu_clases),
        "9":  ("Especialidades", _menu_especialidades),
        "10": ("Inscripciones", _menu_inscripciones),
        "11": ("Rutinas y asistencia", _menu_rutinas_asistencia),
        "12": ("Reportes", _menu_reportes),
        "0":  ("Cerrar sesión", None),
    }

    while True:
        console.rule(f"[bold cyan]Administrador — {empleado.nombre}[/]")
        tabla = Table(box=box.SIMPLE, show_header=False)
        tabla.add_column(style="bold cyan", width=4)
        tabla.add_column()
        for clave, (desc, _) in opciones.items():
            tabla.add_row(clave, desc)
        console.print(tabla)

        op = input("Opción: ").strip()
        if op == "0":
            break
        if op not in opciones or opciones[op][1] is None:
            console.print("[red]Opción no válida.[/]")
            continue
        try:
            opciones[op][1](empleado)
        except Exception as e:
            console.print(f"[red]Error:[/] {e}")


# ------------------------------------------------------------------
# RF-17 — Empleados
# ------------------------------------------------------------------
def _menu_empleados(_empleado) -> None:
    while True:
        console.rule("Empleados")
        console.print("1. Listar  2. Agregar  3. Editar  4. Activar/Desactivar  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            empleados = _empleado_svc.listar()
            tabla = Table(box=box.ROUNDED)
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Nombre")
            tabla.add_column("Usuario")
            tabla.add_column("Correo")
            tabla.add_column("Estado")
            tabla.add_column("Rol")
            for e in empleados:
                tabla.add_row(
                    str(e.codigo_empleado), e.nombre, e.usuario, e.correo,
                    "[green]Activo[/]" if e.estado else "[red]Inactivo[/]",
                    str(e.codigo_rol),
                )
            console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            nombre = input("Nombre: ").strip()
            usuario = input("Usuario: ").strip()
            contrasena = input("Contraseña: ").strip()
            while True:
                correo = input("Correo: ").strip()
                if validar_correo(correo):
                    break
                console.print("[red]Correo inválido.[/]")
            codigo_rol = int(input("Código de rol: "))
            if confirmar():
                codigo = _empleado_svc.agregar(nombre, usuario, contrasena, correo, codigo_rol)
                console.print(f"[green]Empleado agregado. Código: {codigo}[/]")
        elif op == "3":
            codigo = int(input("Código del empleado a editar: "))
            nombre = input("Nuevo nombre (Enter para no cambiar): ").strip()
            correo = input("Nuevo correo (Enter para no cambiar): ").strip()
            campos = {}
            if nombre:
                campos["nombre"] = nombre
            if correo and validar_correo(correo):
                campos["correo"] = correo
            if campos and confirmar():
                _empleado_svc.editar(codigo, **campos)
                console.print("[green]Empleado actualizado.[/]")
        elif op == "4":
            codigo = int(input("Código del empleado: "))
            estado_txt = input("¿Activar o desactivar? (A/D): ").strip().upper()
            if estado_txt in ("A", "D") and confirmar():
                _empleado_svc.cambiar_estado(codigo, estado_txt == "A")
                console.print("[green]Estado actualizado.[/]")


# ------------------------------------------------------------------
# RF-18 — Roles
# ------------------------------------------------------------------
def _menu_roles(_empleado) -> None:
    import storage as _db
    while True:
        console.rule("Roles")
        console.print("1. Listar  2. Agregar  3. Editar  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            filas = sorted(_db.roles, key=lambda x: x["nombre"])
            tabla = Table(title="Roles", box=box.ROUNDED)
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Nombre")
            for f in filas:
                tabla.add_row(str(f["codigo_rol"]), f["nombre"])
            console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            nombre = input("Nombre del rol: ").strip()
            if confirmar():
                rid = _db.next_id("rol")
                _db.roles.append({"codigo_rol": rid, "nombre": nombre})
                console.print(f"[green]Rol agregado. Código: {rid}[/]")
        elif op == "3":
            codigo = int(input("Código del rol: "))
            nombre = input("Nuevo nombre: ").strip()
            if nombre and confirmar():
                for r in _db.roles:
                    if r["codigo_rol"] == codigo:
                        r["nombre"] = nombre
                        break
                console.print("[green]Rol actualizado.[/]")


# ------------------------------------------------------------------
# RF-19 — Horarios
# ------------------------------------------------------------------
def _menu_horarios(_empleado) -> None:
    while True:
        console.rule("Horarios")
        console.print("1. Ver horarios de empleado  2. Asignar/editar  3. Eliminar  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            codigo = int(input("Código del empleado: "))
            horarios = _empleado_svc.listar_horarios(codigo)
            if not horarios:
                console.print("[yellow]Sin horarios.[/]")
            else:
                tabla = Table(box=box.ROUNDED)
                tabla.add_column("Código", style="cyan")
                tabla.add_column("Día")
                tabla.add_column("Entrada")
                tabla.add_column("Salida")
                for h in horarios:
                    tabla.add_row(str(h.codigo_horario), h.dia, str(h.hora_inicio), str(h.hora_fin))
                console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            codigo = int(input("Código del empleado: "))
            dia = input("Día (Lunes/Martes/...): ").strip()
            hi = input("Hora inicio (HH:MM): ").strip()
            hf = input("Hora fin (HH:MM): ").strip()
            if confirmar():
                _empleado_svc.asignar_horario(codigo, dia, hi, hf)
                console.print("[green]Horario guardado.[/]")
        elif op == "3":
            codigo = int(input("Código del horario a eliminar: "))
            if confirmar():
                _empleado_svc.eliminar_horario(codigo)
                console.print("[green]Horario eliminado.[/]")


# ------------------------------------------------------------------
# RF-20 — Clientes
# ------------------------------------------------------------------
def _menu_clientes(_empleado) -> None:
    while True:
        console.rule("Clientes")
        console.print("1. Buscar  2. Editar  3. Dar de baja / reactivar  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            termino = input("Nombre o celular: ").strip()
            clientes = _cliente_svc.buscar(termino)
            if not clientes:
                console.print("[yellow]Sin resultados.[/]")
            else:
                tabla = Table(box=box.ROUNDED)
                tabla.add_column("Código", style="cyan")
                tabla.add_column("Nombre")
                tabla.add_column("Nacimiento")
                tabla.add_column("Edad")
                tabla.add_column("Estado")
                for c in clientes:
                    tabla.add_row(
                        str(c.codigo_cliente), c.nombre_completo,
                        formatear_fecha(c.fecha_nacimiento),
                        str(calcular_edad(c.fecha_nacimiento)),
                        "[green]Activo[/]" if c.estado else "[red]Baja[/]",
                    )
                console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            codigo = int(input("Código del cliente: "))
            colonia = input("Nueva colonia (Enter para no cambiar): ").strip()
            calle = input("Nueva calle (Enter para no cambiar): ").strip()
            campos = {}
            if colonia:
                campos["colonia"] = colonia
            if calle:
                campos["calle"] = calle
            if campos and confirmar():
                _cliente_svc.editar(codigo, **campos)
                console.print("[green]Cliente actualizado.[/]")
        elif op == "3":
            codigo = int(input("Código del cliente: "))
            estado_txt = input("¿Dar de baja o reactivar? (B/R): ").strip().upper()
            if estado_txt in ("B", "R") and confirmar():
                _cliente_svc.cambiar_estado(codigo, estado_txt == "R")
                console.print("[green]Estado actualizado.[/]")


# ------------------------------------------------------------------
# RF-21 — Tipos de membresía y beneficios
# ------------------------------------------------------------------
def _menu_tipos_membresia(_empleado) -> None:
    import storage as _db
    while True:
        console.rule("Tipos de membresía y beneficios")
        console.print("1. Listar tipos  2. Agregar tipo  3. Editar tipo  "
                      "4. Listar beneficios  5. Agregar beneficio  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            filas = sorted(_db.tipos_membresia, key=lambda x: x["monto"])
            tabla = Table(box=box.ROUNDED)
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Nombre")
            tabla.add_column("Días", justify="right")
            tabla.add_column("Monto", justify="right")
            for f in filas:
                tabla.add_row(str(f["codigo_tipo"]), f["nombre"],
                              str(f["duracion_dias"]), f"${f['monto']:.2f}")
            console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            nombre = input("Nombre: ").strip()
            dias = int(input("Duración en días: "))
            monto = float(input("Monto: "))
            if confirmar():
                tid = _db.next_id("tipo_membresia")
                _db.tipos_membresia.append({"codigo_tipo": tid, "nombre": nombre,
                                            "duracion_dias": dias, "monto": monto})
                console.print("[green]Tipo agregado.[/]")
        elif op == "3":
            codigo = int(input("Código del tipo: "))
            nombre = input("Nuevo nombre (Enter para no cambiar): ").strip()
            dias_txt = input("Nueva duración en días (Enter para no cambiar): ").strip()
            monto_txt = input("Nuevo monto (Enter para no cambiar): ").strip()
            campos = {}
            if nombre:
                campos["nombre"] = nombre
            if dias_txt:
                campos["duracion_dias"] = int(dias_txt)
            if monto_txt:
                campos["monto"] = float(monto_txt)
            if campos and confirmar():
                for t in _db.tipos_membresia:
                    if t["codigo_tipo"] == codigo:
                        t.update(campos)
                        break
                console.print("[green]Tipo actualizado.[/]")
        elif op == "4":
            filas = sorted(_db.beneficios, key=lambda x: x["descripcion"])
            tabla = Table(box=box.ROUNDED, title="Beneficios")
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Descripción")
            for f in filas:
                tabla.add_row(str(f["codigo_beneficio"]), f["descripcion"])
            console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "5":
            desc = input("Descripción del beneficio: ").strip()
            if confirmar():
                bid = _db.next_id("beneficio")
                _db.beneficios.append({"codigo_beneficio": bid, "descripcion": desc})
                console.print("[green]Beneficio agregado.[/]")


# ------------------------------------------------------------------
# RF-22 — Membresías
# ------------------------------------------------------------------
def _menu_membresias(_empleado) -> None:
    while True:
        console.rule("Membresías")
        console.print("1. Buscar  2. Marcar vencidas  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            termino = input("Código, nombre o celular: ").strip()
            mems = _membresia_svc.buscar(termino)
            if not mems:
                console.print("[yellow]Sin resultados.[/]")
            else:
                tabla = Table(box=box.ROUNDED)
                tabla.add_column("Código", style="cyan")
                tabla.add_column("Estado")
                tabla.add_column("Inicio")
                tabla.add_column("Vencimiento")
                tabla.add_column("Cliente")
                for m in mems:
                    tabla.add_row(
                        m.codigo_membresia, m.estado,
                        formatear_fecha(m.fecha_inicio),
                        formatear_fecha(m.fecha_vencimiento),
                        str(m.codigo_cliente),
                    )
                console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            if confirmar("¿Marcar como vencidas las membresías expiradas? (S/N): "):
                n = _membresia_svc.marcar_vencidas()
                console.print(f"[green]{n} membresía(s) marcada(s) como vencidas.[/]")


# ------------------------------------------------------------------
# RF-23 — Pagos y métodos de pago
# ------------------------------------------------------------------
def _menu_pagos(_empleado) -> None:
    import storage as _db
    while True:
        console.rule("Pagos y métodos de pago")
        console.print("1. Historial de pagos  2. Métodos de pago  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            termino = input("Código de membresía o nombre de cliente: ").strip()
            mems = _membresia_svc.buscar(termino)
            for m in mems:
                pagos = _membresia_svc.obtener_pagos(m.codigo_membresia)
                console.print(f"\n[bold]{m.codigo_membresia}[/]")
                tabla = Table(box=box.SIMPLE)
                tabla.add_column("Fecha")
                tabla.add_column("Monto", justify="right")
                tabla.add_column("Método")
                for p in pagos:
                    metodo_nombre = next(
                        (mp["nombre"] for mp in _db.metodos_pago if mp["codigo_metodo"] == p.codigo_metodo),
                        str(p.codigo_metodo),
                    )
                    tabla.add_row(formatear_fecha(p.fecha), f"${p.monto:.2f}", metodo_nombre)
                console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            filas = sorted(_db.metodos_pago, key=lambda x: x["nombre"])
            tabla = Table(title="Métodos de pago", box=box.ROUNDED)
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Nombre")
            tabla.add_column("Estado")
            for f in filas:
                tabla.add_row(
                    str(f["codigo_metodo"]), f["nombre"],
                    "[green]Activo[/]" if f["estado"] else "[red]Inactivo[/]",
                )
            console.print(tabla)
            agregar = input("\n¿Agregar método? (S/N): ").strip().upper()
            if agregar == "S":
                nombre = input("Nombre: ").strip()
                if confirmar():
                    mid = _db.next_id("metodo_pago")
                    _db.metodos_pago.append({"codigo_metodo": mid, "nombre": nombre, "estado": True})
                    console.print("[green]Método agregado.[/]")
            input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-24 — Clases
# ------------------------------------------------------------------
def _menu_clases(_empleado) -> None:
    import storage as _db
    import datetime as _dt
    while True:
        console.rule("Clases")
        console.print("1. Listar  2. Agregar  3. Editar  4. Abrir/Cerrar  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            filas = sorted(_db.clases, key=lambda x: (x["dia"], str(x["hora_inicio"])))
            tabla = Table(box=box.ROUNDED)
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Nombre")
            tabla.add_column("Día")
            tabla.add_column("Pública")
            tabla.add_column("Estado")
            tabla.add_column("Inscritos/Cupo")
            for f in filas:
                tabla.add_row(
                    str(f["codigo_clase"]), f["nombre"], f["dia"],
                    "Sí" if f["es_publica"] else "No",
                    "[green]Activa[/]" if f["estado"] else "[red]Cerrada[/]",
                    f"{f['inscritos']}/{f['cupo_maximo']}",
                )
            console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            nombre = input("Nombre: ").strip()
            dia = input("Día: ").strip()
            hi_txt = input("Hora inicio (HH:MM): ").strip()
            hf_txt = input("Hora fin (HH:MM): ").strip()
            cupo = int(input("Cupo máximo: "))
            publica = input("¿Es pública? (S/N): ").strip().upper() == "S"
            esp = int(input("Código de especialidad: "))
            emp = int(input("Código del instructor: "))
            if confirmar():
                h, m = hi_txt.split(":")
                hi = _dt.time(int(h), int(m))
                h, m = hf_txt.split(":")
                hf = _dt.time(int(h), int(m))
                cid = _db.next_id("clase")
                _db.clases.append({
                    "codigo_clase": cid, "nombre": nombre, "dia": dia,
                    "hora_inicio": hi, "hora_fin": hf, "cupo_maximo": cupo,
                    "inscritos": 0, "es_publica": publica, "estado": True,
                    "codigo_especialidad": esp, "codigo_empleado": emp,
                })
                console.print("[green]Clase agregada.[/]")
        elif op == "3":
            codigo = int(input("Código de la clase: "))
            nombre = input("Nuevo nombre (Enter para no cambiar): ").strip()
            cupo_txt = input("Nuevo cupo máximo (Enter para no cambiar): ").strip()
            campos = {}
            if nombre:
                campos["nombre"] = nombre
            if cupo_txt:
                campos["cupo_maximo"] = int(cupo_txt)
            if campos and confirmar():
                for c in _db.clases:
                    if c["codigo_clase"] == codigo:
                        c.update(campos)
                        break
                console.print("[green]Clase actualizada.[/]")
        elif op == "4":
            codigo = int(input("Código de la clase: "))
            estado_txt = input("¿Abrir o cerrar? (A/C): ").strip().upper()
            if estado_txt in ("A", "C") and confirmar():
                for c in _db.clases:
                    if c["codigo_clase"] == codigo:
                        c["estado"] = estado_txt == "A"
                        break
                console.print("[green]Estado de la clase actualizado.[/]")


# ------------------------------------------------------------------
# RF-25 — Especialidades
# ------------------------------------------------------------------
def _menu_especialidades(_empleado) -> None:
    import storage as _db
    while True:
        console.rule("Especialidades")
        console.print("1. Listar  2. Agregar  3. Editar  4. Eliminar  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            filas = sorted(_db.especialidades, key=lambda x: x["nombre"])
            tabla = Table(title="Especialidades", box=box.ROUNDED)
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Nombre")
            tabla.add_column("Descripción")
            for f in filas:
                tabla.add_row(str(f["codigo_especialidad"]), f["nombre"], f["descripcion"])
            console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            nombre = input("Nombre: ").strip()
            desc = input("Descripción: ").strip()
            if confirmar():
                eid = _db.next_id("especialidad")
                _db.especialidades.append({"codigo_especialidad": eid, "nombre": nombre, "descripcion": desc})
                console.print("[green]Especialidad agregada.[/]")
        elif op == "3":
            codigo = int(input("Código: "))
            nombre = input("Nuevo nombre (Enter para no cambiar): ").strip()
            desc = input("Nueva descripción (Enter para no cambiar): ").strip()
            campos = {}
            if nombre:
                campos["nombre"] = nombre
            if desc:
                campos["descripcion"] = desc
            if campos and confirmar():
                for e in _db.especialidades:
                    if e["codigo_especialidad"] == codigo:
                        e.update(campos)
                        break
                console.print("[green]Especialidad actualizada.[/]")
        elif op == "4":
            codigo = int(input("Código: "))
            tiene_clases = any(c for c in _db.clases if c["codigo_especialidad"] == codigo)
            if tiene_clases:
                console.print("[red]No se puede eliminar: tiene clases asociadas.[/]")
            elif confirmar():
                _db.especialidades[:] = [e for e in _db.especialidades if e["codigo_especialidad"] != codigo]
                console.print("[green]Especialidad eliminada.[/]")


# ------------------------------------------------------------------
# RF-26 — Inscripciones
# ------------------------------------------------------------------
def _menu_inscripciones(_empleado) -> None:
    from models.inscripcion_clase import InscripcionClase
    while True:
        console.rule("Inscripciones")
        console.print("1. Por clase  2. Por cliente  3. Cambiar estado  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op in ("1", "2"):
            if op == "1":
                codigo = int(input("Código de la clase: "))
                inscripciones = _clase_svc.listar_inscritos(codigo)
            else:
                termino = input("Nombre o celular del cliente: ").strip()
                clientes = _cliente_svc.buscar(termino)
                if not clientes:
                    console.print("[yellow]Sin resultados.[/]")
                    continue
                for c in clientes:
                    console.print(f"  [{c.codigo_cliente}] {c.nombre_completo}")
                codigo = int(input("Código del cliente: "))
                import storage as _db
                from models.inscripcion_clase import InscripcionClase as IC
                inscripciones = [
                    IC(r["codigo_inscripcion"], r["fecha"], r["estado"],
                       r.get("observaciones"), r["codigo_cliente"], r["codigo_clase"])
                    for r in _db.inscripciones_clase
                    if r["codigo_cliente"] == codigo
                ]

            tabla = Table(box=box.ROUNDED)
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Clase")
            tabla.add_column("Fecha")
            tabla.add_column("Estado")
            for i in inscripciones:
                tabla.add_row(
                    str(i.codigo_inscripcion), str(i.codigo_clase),
                    formatear_fecha(i.fecha), i.estado,
                )
            console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "3":
            codigo = int(input("Código de la inscripción: "))
            estado_txt = input("Nuevo estado (activa/cancelada): ").strip().lower()
            if estado_txt in (InscripcionClase.ACTIVA, InscripcionClase.CANCELADA) and confirmar():
                _clase_svc.cambiar_estado_inscripcion(codigo, estado_txt)
                console.print("[green]Estado actualizado.[/]")


# ------------------------------------------------------------------
# RF-27 — Rutinas y asistencia
# ------------------------------------------------------------------
def _menu_rutinas_asistencia(_empleado) -> None:
    while True:
        console.rule("Rutinas y asistencia")
        console.print("1. Rutinas por cliente  2. Asistencia por cliente y periodo  0. Volver")
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op == "1":
            termino = input("Nombre o celular: ").strip()
            clientes = _cliente_svc.buscar(termino)
            if not clientes:
                console.print("[yellow]Sin resultados.[/]")
                continue
            for c in clientes:
                console.print(f"  [{c.codigo_cliente}] {c.nombre_completo}")
            codigo = int(input("Código del cliente: "))
            rutinas = _rutina_svc.historial_cliente(codigo)
            tabla = Table(box=box.ROUNDED, title="Rutinas")
            tabla.add_column("Código", style="cyan")
            tabla.add_column("Fecha")
            tabla.add_column("Objetivo")
            tabla.add_column("Entrenador")
            for r in rutinas:
                tabla.add_row(
                    str(r.codigo_rutina), formatear_fecha(r.fecha),
                    r.objetivo, str(r.codigo_empleado),
                )
            console.print(tabla)
            input("\nEnter para continuar...")
        elif op == "2":
            termino = input("Nombre o celular: ").strip()
            clientes = _cliente_svc.buscar(termino)
            if not clientes:
                console.print("[yellow]Sin resultados.[/]")
                continue
            for c in clientes:
                console.print(f"  [{c.codigo_cliente}] {c.nombre_completo}")
            codigo = int(input("Código del cliente: "))
            desde_txt = input("Desde (YYYY-MM-DD, Enter para todo): ").strip()
            hasta_txt = input("Hasta (YYYY-MM-DD, Enter para hoy): ").strip()
            desde = validar_fecha(desde_txt) if desde_txt else None
            hasta = validar_fecha(hasta_txt) if hasta_txt else None
            asistencias = _asistencia_svc.listar_por_cliente(codigo, desde, hasta)
            tabla = Table(box=box.ROUNDED, title="Asistencias")
            tabla.add_column("Fecha")
            tabla.add_column("Hora")
            tabla.add_column("Rutina")
            for a in asistencias:
                tabla.add_row(
                    formatear_fecha(a.fecha), str(a.hora),
                    str(a.codigo_rutina) if a.codigo_rutina else "—",
                )
            console.print(tabla)
            input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-28 — Reportes
# ------------------------------------------------------------------
def _menu_reportes(_empleado) -> None:
    while True:
        console.rule("Reportes")
        console.print(
            "1. Ingresos por periodo\n"
            "2. Membresías por estado\n"
            "3. Clientes activos y vencidos\n"
            "4. Asistencia al gimnasio\n"
            "5. Ocupación de clases\n"
            "6. Clases por especialidad\n"
            "0. Volver"
        )
        op = input("Opción: ").strip()
        if op == "0":
            break
        elif op in ("1", "4"):
            desde_txt = input("Desde (YYYY-MM-DD): ").strip()
            hasta_txt = input("Hasta (YYYY-MM-DD): ").strip()
            desde = validar_fecha(desde_txt)
            hasta = validar_fecha(hasta_txt)
            if not desde or not hasta:
                console.print("[red]Fechas inválidas.[/]")
                continue
            if op == "1":
                filas = _reporte_svc.ingresos_por_periodo(desde, hasta)
                tabla = Table(title=f"Ingresos {formatear_fecha(desde)} – {formatear_fecha(hasta)}", box=box.ROUNDED)
                tabla.add_column("Método de pago")
                tabla.add_column("Pagos", justify="right")
                tabla.add_column("Total", justify="right")
                for f in filas:
                    tabla.add_row(f["metodo"], str(f["cantidad_pagos"]), f"${f['total']:.2f}")
            else:
                filas = _reporte_svc.asistencia_por_periodo(desde, hasta)
                tabla = Table(title="Asistencia diaria", box=box.ROUNDED)
                tabla.add_column("Fecha")
                tabla.add_column("Asistencias", justify="right")
                for f in filas:
                    tabla.add_row(formatear_fecha(f["fecha"]), str(f["total_asistencias"]))
            console.print(tabla)
        elif op == "2":
            filas = _reporte_svc.membresias_por_estado()
            tabla = Table(title="Membresías por estado", box=box.ROUNDED)
            tabla.add_column("Estado")
            tabla.add_column("Cantidad", justify="right")
            for f in filas:
                tabla.add_row(f["estado"], str(f["cantidad"]))
            console.print(tabla)
        elif op == "3":
            filas = _reporte_svc.clientes_activos_vencidos()
            tabla = Table(title="Clientes activos / vencidos", box=box.ROUNDED)
            tabla.add_column("Cliente")
            tabla.add_column("Estado")
            tabla.add_column("Vencimiento")
            for f in filas:
                tabla.add_row(f["cliente"], f["estado"], formatear_fecha(f["fecha_vencimiento"]))
            console.print(tabla)
        elif op == "5":
            filas = _reporte_svc.ocupacion_clases()
            tabla = Table(title="Ocupación de clases", box=box.ROUNDED)
            tabla.add_column("Clase")
            tabla.add_column("Día")
            tabla.add_column("Inscritos", justify="right")
            tabla.add_column("Cupo", justify="right")
            tabla.add_column("Ocupación %", justify="right")
            for f in filas:
                tabla.add_row(
                    f["nombre"], f["dia"],
                    str(f["inscritos"]), str(f["cupo_maximo"]),
                    f"{f['ocupacion_pct']}%",
                )
            console.print(tabla)
        elif op == "6":
            filas = _reporte_svc.clases_por_especialidad()
            tabla = Table(title="Clases por especialidad", box=box.ROUNDED)
            tabla.add_column("Especialidad")
            tabla.add_column("Clases", justify="right")
            for f in filas:
                tabla.add_row(f["especialidad"], str(f["total_clases"]))
            console.print(tabla)
        input("\nEnter para continuar...")
