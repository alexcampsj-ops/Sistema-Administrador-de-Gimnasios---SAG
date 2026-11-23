from rich.console import Console
from rich.table import Table
from rich import box

from models.empleado import Empleado
from services.clase_service import ClaseService
from services.rutina_service import RutinaService
from services.asistencia_service import AsistenciaService
from services.empleado_service import EmpleadoService
from services.cliente_service import ClienteService
from utils.validators import validar_fecha, confirmar
from utils.helpers import formatear_fecha

console = Console()
# Instancias de los servicios usados por el entrenador
_clase_svc = ClaseService()
_rutina_svc = RutinaService()
_asistencia_svc = AsistenciaService()
_empleado_svc = EmpleadoService()
_cliente_svc = ClienteService()


def ejecutar(empleado: Empleado) -> None:
    """Menú principal del entrenador (RF-12 a RF-16).

    Presenta las 5 operaciones disponibles. Captura errores de servicio
    y los muestra sin cerrar el menú.
    """
    opciones = {
        "1": ("Mi horario", _ver_horario),
        "2": ("Mis clases", _ver_clases),
        "3": ("Registrar rutina", _registrar_rutina),
        "4": ("Consultar / editar rutinas", _consultar_rutinas),
        "5": ("Asistencia de un cliente", _ver_asistencia_cliente),
        "0": ("Cerrar sesión", None),
    }

    while True:
        console.rule(f"[bold cyan]Entrenador — {empleado.nombre}[/]")
        tabla = Table(box=box.SIMPLE, show_header=False)
        tabla.add_column(style="bold cyan")
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
# RF-12 — Mi horario
# ------------------------------------------------------------------
def _ver_horario(empleado: Empleado) -> None:
    """Muestra el horario asignado al entrenador que inició sesión (RF-12).

    Usa el codigo_empleado del objeto Empleado activo para filtrar
    solo sus propios horarios.
    """
    horarios = _empleado_svc.listar_horarios(empleado.codigo_empleado)
    if not horarios:
        console.print("[yellow]No tienes horarios asignados.[/]")
        input("\nEnter para continuar...")
        return

    tabla = Table(title="Mi Horario", box=box.ROUNDED)
    tabla.add_column("Día")
    tabla.add_column("Entrada")
    tabla.add_column("Salida")
    for h in horarios:
        tabla.add_row(h.dia, str(h.hora_inicio), str(h.hora_fin))
    console.print(tabla)
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-13 — Mis clases
# ------------------------------------------------------------------
def _ver_clases(empleado: Empleado) -> None:
    """Muestra las clases asignadas al entrenador y permite ver sus inscritos (RF-13).

    Tras mostrar las clases, pregunta si se quiere ver el detalle de inscritos
    de alguna clase específica. Para cada inscrito, busca su nombre por ID.
    """
    clases = _clase_svc.listar_por_empleado(empleado.codigo_empleado)
    if not clases:
        console.print("[yellow]No tienes clases asignadas.[/]")
        input("\nEnter para continuar...")
        return

    tabla = Table(title="Mis Clases", box=box.ROUNDED)
    tabla.add_column("Código", style="cyan")
    tabla.add_column("Nombre")
    tabla.add_column("Día")
    tabla.add_column("Horario")
    tabla.add_column("Inscritos/Cupo")
    tabla.add_column("Estado")
    for c in clases:
        tabla.add_row(
            str(c.codigo_clase), c.nombre, c.dia,
            f"{c.hora_inicio} – {c.hora_fin}",
            f"{c.inscritos}/{c.cupo_maximo}",
            "[green]Activa[/]" if c.estado else "[red]Cerrada[/]",
        )
    console.print(tabla)

    ver = input("\n¿Ver inscritos de alguna clase? (código o Enter para omitir): ").strip()
    if ver:
        inscritos = _clase_svc.listar_inscritos(int(ver))
        if not inscritos:
            console.print("[yellow]Sin inscritos.[/]")
        else:
            ti = Table(title=f"Inscritos — Clase {ver}", box=box.SIMPLE)
            ti.add_column("Cliente")
            ti.add_column("Fecha inscripción")
            ti.add_column("Estado")
            for i in inscritos:
                # Busca el nombre del cliente por su código para mostrarlo legible
                cliente = _cliente_svc.obtener_por_id(i.codigo_cliente)
                nombre = cliente.nombre_completo if cliente else str(i.codigo_cliente)
                ti.add_row(nombre, formatear_fecha(i.fecha), i.estado)
            console.print(ti)
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-14 — Registrar rutina
# ------------------------------------------------------------------
def _registrar_rutina(empleado: Empleado) -> None:
    """Registra una nueva rutina de entrenamiento para un cliente (RF-14).

    El entrenador activo queda como responsable de la rutina.
    Las observaciones son opcionales.
    """
    console.rule("Registrar rutina")
    termino = input("Buscar cliente (nombre o celular): ").strip()
    clientes = _cliente_svc.buscar(termino)
    if not clientes:
        console.print("[red]No se encontró ningún cliente.[/]")
        return
    for c in clientes:
        console.print(f"  [{c.codigo_cliente}] {c.nombre_completo}")
    codigo_cliente = int(input("Código del cliente: "))

    # Bucle hasta recibir una fecha válida
    while True:
        fecha_txt = input("Fecha (YYYY-MM-DD): ").strip()
        fecha = validar_fecha(fecha_txt)
        if fecha:
            break
        console.print("[red]Formato inválido.[/]")

    objetivo = input("Objetivo: ").strip()
    # "or None" convierte cadena vacía a None para guardarlo como NULL en BD
    obs = input("Observaciones (opcional): ").strip() or None

    if not confirmar():
        console.print("Operación cancelada.")
        return

    # Registra la rutina con el codigo_empleado del entrenador activo
    codigo = _rutina_svc.registrar(
        fecha, objetivo, obs, codigo_cliente, empleado.codigo_empleado
    )
    console.print(f"[green]Rutina registrada. Código: {codigo}[/]")
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-15 — Consultar / editar rutinas
# ------------------------------------------------------------------
def _consultar_rutinas(empleado: Empleado) -> None:
    """Lista las rutinas del entrenador y permite editar objetivo/observaciones (RF-15).

    Tras mostrar la tabla, pregunta si se quiere editar alguna rutina.
    Solo actualiza los campos que el usuario proporcione (actualización parcial).
    """
    console.rule("Rutinas registradas")
    # Solo muestra las rutinas creadas por este entrenador
    rutinas = _rutina_svc.listar_por_entrenador(empleado.codigo_empleado)
    if not rutinas:
        console.print("[yellow]Sin rutinas registradas.[/]")
        input("\nEnter para continuar...")
        return

    tabla = Table(title="Mis Rutinas", box=box.ROUNDED)
    tabla.add_column("Código", style="cyan")
    tabla.add_column("Cliente")
    tabla.add_column("Fecha")
    tabla.add_column("Objetivo")
    for r in rutinas:
        # Busca el nombre del cliente para mostrarlo en lugar del ID
        cliente = _cliente_svc.obtener_por_id(r.codigo_cliente)
        nombre = cliente.nombre_completo if cliente else str(r.codigo_cliente)
        tabla.add_row(
            str(r.codigo_rutina), nombre,
            formatear_fecha(r.fecha), r.objetivo,
        )
    console.print(tabla)

    editar = input("\n¿Editar alguna rutina? (código o Enter para omitir): ").strip()
    if editar:
        nuevo_objetivo = input("Nuevo objetivo (Enter para no cambiar): ").strip()
        nueva_obs = input("Nuevas observaciones (Enter para no cambiar): ").strip()
        # Solo agrega al dict los campos que el usuario llenó
        campos = {}
        if nuevo_objetivo:
            campos["objetivo"] = nuevo_objetivo
        if nueva_obs:
            campos["observaciones"] = nueva_obs
        if campos:
            if confirmar():
                # Pasa solo los campos modificados al servicio (actualización parcial)
                _rutina_svc.editar(int(editar), **campos)
                console.print("[green]Rutina actualizada.[/]")
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-16 — Asistencia de un cliente
# ------------------------------------------------------------------
def _ver_asistencia_cliente(_empleado) -> None:
    """Muestra el historial de asistencias de un cliente con filtro de fechas (RF-16).

    Las fechas son opcionales: si no se proporcionan, muestra todas las asistencias.
    validar_fecha devuelve None si la cadena está vacía o es inválida,
    y listar_por_cliente acepta None para omitir ese filtro.
    """
    console.rule("Asistencia de cliente")
    termino = input("Buscar cliente (nombre o celular): ").strip()
    clientes = _cliente_svc.buscar(termino)
    if not clientes:
        console.print("[red]No se encontró ningún cliente.[/]")
        return
    for c in clientes:
        console.print(f"  [{c.codigo_cliente}] {c.nombre_completo}")
    codigo_cliente = int(input("Código del cliente: "))

    # Fechas opcionales: si el usuario no escribe nada, quedan como None
    desde_txt = input("Fecha desde (YYYY-MM-DD, Enter para todo): ").strip()
    hasta_txt = input("Fecha hasta (YYYY-MM-DD, Enter para hoy): ").strip()
    desde = validar_fecha(desde_txt) if desde_txt else None
    hasta = validar_fecha(hasta_txt) if hasta_txt else None

    asistencias = _asistencia_svc.listar_por_cliente(codigo_cliente, desde, hasta)
    if not asistencias:
        console.print("[yellow]Sin asistencias en el periodo.[/]")
    else:
        tabla = Table(title="Asistencias", box=box.ROUNDED)
        tabla.add_column("Fecha")
        tabla.add_column("Hora")
        tabla.add_column("Rutina")
        for a in asistencias:
            tabla.add_row(
                formatear_fecha(a.fecha), str(a.hora),
                # Si no hay rutina asociada, muestra "—"
                str(a.codigo_rutina) if a.codigo_rutina else "—",
            )
        console.print(tabla)
    input("\nEnter para continuar...")
