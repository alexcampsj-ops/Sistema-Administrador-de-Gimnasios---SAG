from rich.console import Console
from rich.table import Table
from rich import box

from models.empleado import Empleado
from services.cliente_service import ClienteService
from services.membresia_service import MembresiaService
from services.clase_service import ClaseService
from services.asistencia_service import AsistenciaService
from utils.validators import validar_celular, validar_fecha, confirmar
from utils.helpers import calcular_edad, formatear_fecha, dias_restantes

console = Console()
# Instancias de los servicios usados por la recepcionista
_cliente_svc = ClienteService()
_membresia_svc = MembresiaService()
_clase_svc = ClaseService()
_asistencia_svc = AsistenciaService()


def ejecutar(empleado: Empleado) -> None:
    """Menú principal de la recepcionista (RF-04 a RF-11).

    Presenta las 8 operaciones disponibles. Llama a la función correspondiente
    según la opción elegida. Los errores de servicio se capturan y muestran
    en pantalla sin cerrar el menú.
    """
    # Diccionario que mapea número de opción a (descripción, función)
    opciones = {
        "1": ("Tipos de membresía", _ver_tipos_membresia),
        "2": ("Registrar cliente", _registrar_cliente),
        "3": ("Vender membresía", _vender_membresia),
        "4": ("Cancelar membresía", _cancelar_membresia),
        "5": ("Consultar membresía", _consultar_membresia),
        "6": ("Renovar membresía", _renovar_membresia),
        "7": ("Inscribir cliente a clase", _inscribir_clase),
        "8": ("Registrar asistencia", _registrar_asistencia),
        "0": ("Cerrar sesión", None),
    }

    while True:
        console.rule(f"[bold cyan]Recepcionista — {empleado.nombre}[/]")
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
            # Llama a la función de la opción elegida, pasando el empleado activo
            opciones[op][1](empleado)
        except Exception as e:
            # Captura errores de validación de los servicios y los muestra sin romper el menú
            console.print(f"[red]Error:[/] {e}")


# ------------------------------------------------------------------
# RF-04 — Tipos de membresía (solo consulta)
# ------------------------------------------------------------------
def _ver_tipos_membresia(_empleado) -> None:
    """Muestra los tipos de membresía disponibles con sus beneficios (RF-04).

    Consulta directamente la BD con un JOIN de tres tablas para obtener
    el nombre del tipo y los beneficios concatenados en una sola cadena.
    GROUP_CONCAT es una función de MySQL que une múltiples filas en un string.
    """
    from config.db import get_connection
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT t.codigo_tipo, t.nombre, t.duracion_dias, t.monto,
                   GROUP_CONCAT(b.descripcion SEPARATOR ' | ') AS beneficios
            FROM TIPO_MEMBRESIA t
            LEFT JOIN TIPO_MEMBRESIA_BENEFICIO tb ON t.codigo_tipo = tb.codigo_tipo
            LEFT JOIN BENEFICIO b ON tb.codigo_beneficio = b.codigo_beneficio
            GROUP BY t.codigo_tipo
            ORDER BY t.monto
            """
        )
        filas = cursor.fetchall()
    finally:
        conn.close()

    # Muestra los resultados en una tabla formateada con rich
    tabla = Table(title="Tipos de Membresía", box=box.ROUNDED)
    tabla.add_column("Código", style="cyan")
    tabla.add_column("Nombre")
    tabla.add_column("Días", justify="right")
    tabla.add_column("Monto", justify="right")
    tabla.add_column("Beneficios")
    for f in filas:
        tabla.add_row(
            str(f["codigo_tipo"]), f["nombre"],
            str(f["duracion_dias"]), f"${f['monto']:.2f}",
            # Si no hay beneficios (LEFT JOIN devolvió NULL), muestra "—"
            f["beneficios"] or "—",
        )
    console.print(tabla)
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-05 — Registrar cliente
# ------------------------------------------------------------------
def _registrar_cliente(_empleado) -> None:
    """Registra un nuevo cliente con sus datos personales y celulares (RF-05).

    Valida:
      - Formato de fecha de nacimiento (YYYY-MM-DD)
      - Al menos un celular (exactamente 10 dígitos)
    Muestra un resumen antes de confirmar para evitar errores.
    """
    console.rule("Registrar cliente")
    nombre = input("Nombre de pila: ").strip()
    ap = input("Apellido paterno: ").strip()
    am = input("Apellido materno: ").strip()

    # Bucle hasta recibir una fecha válida
    while True:
        fn_txt = input("Fecha de nacimiento (YYYY-MM-DD): ").strip()
        fn = validar_fecha(fn_txt)
        if fn:
            break
        console.print("[red]Formato inválido. Usa YYYY-MM-DD.[/]")

    colonia = input("Colonia: ").strip()
    calle = input("Calle: ").strip()

    # Recolecta celulares; requiere al menos uno válido para continuar
    celulares: list[str] = []
    while True:
        cel = input("Celular (10 dígitos) [Enter para terminar]: ").strip()
        if not cel:
            if not celulares:
                console.print("[red]Debes ingresar al menos un celular.[/]")
                continue
            break  # Termina el bucle si ya hay al menos uno
        if validar_celular(cel):
            celulares.append(cel)
        else:
            console.print("[red]Número inválido. Deben ser exactamente 10 dígitos.[/]")

    # Muestra resumen calculando la edad antes de confirmar
    edad = calcular_edad(fn)
    console.print(
        f"\nNombre: [bold]{nombre} {ap} {am}[/]  |  "
        f"Edad: {edad} años  |  "
        f"Celulares: {', '.join(celulares)}"
    )
    if not confirmar():
        console.print("Operación cancelada.")
        return

    codigo = _cliente_svc.registrar(nombre, ap, am, fn, colonia, calle, celulares)
    console.print(f"[green]Cliente registrado. Código: {codigo}[/]")
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-06 — Vender membresía
# ------------------------------------------------------------------
def _vender_membresia(empleado: Empleado) -> None:
    """Registra la venta de una membresía a un cliente existente (RF-06).

    Flujo:
      1. Busca al cliente por nombre o celular.
      2. Muestra los tipos de membresía disponibles.
      3. Solicita fecha de inicio y método de pago.
      4. Llama a MembresiaService.vender() que inserta membresía y pago.
    """
    console.rule("Venta de membresía")
    termino = input("Buscar cliente (nombre o celular): ").strip()
    clientes = _cliente_svc.buscar(termino)
    if not clientes:
        console.print("[red]No se encontró ningún cliente.[/]")
        return

    # Muestra los clientes encontrados para que el usuario elija
    for c in clientes:
        console.print(f"  [{c.codigo_cliente}] {c.nombre_completo}")
    codigo_cliente = int(input("Código del cliente: "))

    # Reutiliza la función de tipos de membresía para mostrarlos
    _ver_tipos_membresia(empleado)
    codigo_tipo = int(input("Código del tipo de membresía: "))

    # Bucle hasta recibir una fecha de inicio válida
    while True:
        fi_txt = input("Fecha de inicio (YYYY-MM-DD): ").strip()
        fi = validar_fecha(fi_txt)
        if fi:
            break
        console.print("[red]Formato inválido.[/]")

    metodo = int(input("Código del método de pago: "))

    if not confirmar():
        console.print("Operación cancelada.")
        return

    # Llama al servicio; el empleado activo queda registrado como vendedor
    codigo_mem = _membresia_svc.vender(
        codigo_cliente, codigo_tipo, fi, metodo, empleado.codigo_empleado
    )
    console.print(f"[green]Membresía vendida. Código: {codigo_mem}[/]")
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-07 — Cancelar membresía
# ------------------------------------------------------------------
def _cancelar_membresia(_empleado) -> None:
    """Cancela una membresía existente registrando el motivo (RF-07).

    Busca la membresía, muestra su estado actual y solicita confirmación
    antes de ejecutar la cancelación.
    """
    console.rule("Cancelar membresía")
    termino = input("Buscar membresía (código, nombre o celular): ").strip()
    mems = _membresia_svc.buscar(termino)
    if not mems:
        console.print("[red]No se encontró ninguna membresía.[/]")
        return

    # Muestra las membresías encontradas con su estado y vencimiento
    for m in mems:
        console.print(
            f"  [{m.codigo_membresia}] estado={m.estado} "
            f"vence={formatear_fecha(m.fecha_vencimiento)}"
        )
    codigo = input("Código de membresía a cancelar: ").strip()
    motivo = input("Motivo de cancelación: ").strip()

    if not confirmar():
        console.print("Operación cancelada.")
        return

    _membresia_svc.cancelar(codigo, motivo)
    console.print("[green]Membresía cancelada.[/]")
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-08 — Consultar membresía
# ------------------------------------------------------------------
def _consultar_membresia(_empleado) -> None:
    """Muestra el detalle de una membresía con sus pagos y días restantes (RF-08).

    dias_restantes() calcula cuántos días quedan; si es negativo, ya venció.
    """
    console.rule("Consultar membresía")
    termino = input("Buscar membresía (código, nombre o celular): ").strip()
    mems = _membresia_svc.buscar(termino)
    if not mems:
        console.print("[red]No se encontró ninguna membresía.[/]")
        return

    for m in mems:
        # Calcula los días restantes para mostrarlos junto al estado
        dias = dias_restantes(m.fecha_vencimiento)
        console.print(
            f"\n[bold]{m.codigo_membresia}[/]  estado=[cyan]{m.estado}[/]  "
            f"inicio={formatear_fecha(m.fecha_inicio)}  "
            f"vence={formatear_fecha(m.fecha_vencimiento)}  "
            f"días restantes={dias}"
        )
        # Obtiene y muestra el historial de pagos de esta membresía
        pagos = _membresia_svc.obtener_pagos(m.codigo_membresia)
        if pagos:
            tp = Table(box=box.SIMPLE, title="Pagos")
            tp.add_column("Fecha")
            tp.add_column("Monto", justify="right")
            for p in pagos:
                tp.add_row(formatear_fecha(p.fecha), f"${p.monto:.2f}")
            console.print(tp)
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-09 — Renovar membresía
# ------------------------------------------------------------------
def _renovar_membresia(empleado: Empleado) -> None:
    """Renueva una membresía creando una nueva con vigencia consecutiva (RF-09).

    El cálculo de la fecha de inicio de la nueva membresía lo hace
    MembresiaService.renovar() usando max(vencimiento_actual, hoy).
    """
    console.rule("Renovar membresía")
    codigo = input("Código de membresía a renovar: ").strip()
    metodo = int(input("Código del método de pago: "))

    if not confirmar():
        console.print("Operación cancelada.")
        return

    # El empleado activo queda registrado como el que procesó la renovación
    nuevo = _membresia_svc.renovar(codigo, metodo, empleado.codigo_empleado)
    console.print(f"[green]Renovación exitosa. Nuevo código: {nuevo}[/]")
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-10 — Inscribir cliente a clase
# ------------------------------------------------------------------
def _inscribir_clase(_empleado) -> None:
    """Inscribe a un cliente en una clase grupal disponible (RF-10).

    Muestra solo las clases públicas y activas.
    lugares_disponibles es una propiedad calculada del modelo Clase:
    cupo_maximo - inscritos.
    """
    console.rule("Inscripción a clase")
    # Obtiene solo clases públicas y activas para mostrar al cliente
    clases = _clase_svc.listar_publicas_activas()
    if not clases:
        console.print("[red]No hay clases disponibles.[/]")
        return

    tabla = Table(title="Clases disponibles", box=box.ROUNDED)
    tabla.add_column("Código", style="cyan")
    tabla.add_column("Nombre")
    tabla.add_column("Día")
    tabla.add_column("Horario")
    tabla.add_column("Lugares", justify="right")
    for c in clases:
        tabla.add_row(
            str(c.codigo_clase), c.nombre, c.dia,
            f"{c.hora_inicio} – {c.hora_fin}",
            # lugares_disponibles = cupo_maximo - inscritos (propiedad del modelo)
            str(c.lugares_disponibles),
        )
    console.print(tabla)

    termino = input("Buscar cliente (nombre o celular): ").strip()
    clientes = _cliente_svc.buscar(termino)
    if not clientes:
        console.print("[red]No se encontró ningún cliente.[/]")
        return
    for c in clientes:
        console.print(f"  [{c.codigo_cliente}] {c.nombre_completo}")
    codigo_cliente = int(input("Código del cliente: "))
    codigo_clase = int(input("Código de la clase: "))
    # Las observaciones son opcionales; "or None" convierte cadena vacía a None
    obs = input("Observaciones (opcional): ").strip() or None

    if not confirmar():
        console.print("Operación cancelada.")
        return

    _clase_svc.inscribir(codigo_cliente, codigo_clase, obs)
    console.print("[green]Inscripción registrada.[/]")
    input("\nEnter para continuar...")


# ------------------------------------------------------------------
# RF-11 — Registrar asistencia
# ------------------------------------------------------------------
def _registrar_asistencia(_empleado) -> None:
    """Registra la asistencia de un cliente al gimnasio (RF-11).

    El servicio verifica automáticamente que el cliente tenga membresía activa.
    La rutina es opcional: si el cliente viene a seguir una rutina específica
    se puede registrar cuál.
    """
    console.rule("Registrar asistencia")
    termino = input("Buscar cliente (nombre o celular): ").strip()
    clientes = _cliente_svc.buscar(termino)
    if not clientes:
        console.print("[red]No se encontró ningún cliente.[/]")
        return
    for c in clientes:
        console.print(f"  [{c.codigo_cliente}] {c.nombre_completo}")
    codigo_cliente = int(input("Código del cliente: "))
    rutina_txt = input("Código de rutina (opcional, Enter para omitir): ").strip()
    # Convierte a int si se proporcionó un código; si no, deja None
    codigo_rutina = int(rutina_txt) if rutina_txt else None

    if not confirmar():
        console.print("Operación cancelada.")
        return

    _asistencia_svc.registrar(codigo_cliente, codigo_rutina)
    console.print("[green]Asistencia registrada.[/]")
    input("\nEnter para continuar...")
