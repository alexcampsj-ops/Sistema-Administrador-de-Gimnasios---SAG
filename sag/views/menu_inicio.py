from rich.console import Console
from rich.table import Table
from rich import box

from services.auth_service import AuthService, MAX_INTENTOS

# Instancia global de Console para imprimir con colores y estilos
console = Console()
# Instancia del servicio de autenticación (se crea una sola vez al cargar el módulo)
_auth = AuthService()


def mostrar_bienvenida() -> None:
    """Imprime el encabezado decorativo del sistema usando rich."""
    # console.rule dibuja una línea horizontal con el texto centrado
    console.rule("[bold cyan]SAG – Sistema Administrativo de Gimnasios[/]")
    console.print()


def ejecutar() -> None:
    """Bucle principal del menú de inicio (RF-01, RF-02, RF-03).

    Muestra las 3 opciones de rol disponibles (Recepcionista, Entrenador, Administrador).
    Cuando el usuario elige un rol, llama a _autenticar() para verificar credenciales.
    Si el login es exitoso, abre el menú correspondiente al rol.
    Al cerrar sesión desde cualquier menú, el flujo regresa aquí.
    Si se agotan los intentos, se cierra el programa por seguridad.
    """
    # Las importaciones se hacen aquí (lazy imports) para evitar
    # importaciones circulares entre los módulos de vistas
    from views.menu_recepcionista import ejecutar as menu_recepcionista
    from views.menu_entrenador import ejecutar as menu_entrenador
    from views.menu_administrador import ejecutar as menu_administrador

    # Diccionario que mapea la opción del menú al nombre del rol y su función de menú
    roles = {
        "1": ("Recepcionista", menu_recepcionista),
        "2": ("Entrenador", menu_entrenador),
        "3": ("Administrador", menu_administrador),
    }

    while True:
        mostrar_bienvenida()

        # Construye la tabla de opciones con rich para que se vea formateada
        tabla = Table(box=box.SIMPLE, show_header=False)
        tabla.add_column(style="bold cyan")
        tabla.add_column()
        tabla.add_row("1", "Recepcionista")
        tabla.add_row("2", "Entrenador")
        tabla.add_row("3", "Administrador")
        tabla.add_row("0", "Salir")
        console.print(tabla)

        opcion = input("Elige una opción: ").strip()

        if opcion == "0":
            console.print("[bold]Hasta luego.[/]")
            break

        if opcion not in roles:
            console.print("[red]Opción no válida.[/]")
            continue

        # Desempaqueta el nombre del rol y la función del menú
        nombre_rol, menu_fn = roles[opcion]
        empleado = _autenticar(nombre_rol)
        if empleado is None:
            # Se agotaron los MAX_INTENTOS intentos; se bloquea el acceso
            console.print("[bold red]Acceso bloqueado. Cerrando el programa.[/]")
            break

        # Abre el menú del rol; cuando el usuario cierra sesión, regresa aquí
        menu_fn(empleado)
        # Al cerrar sesión regresa aquí (RF-03)


def _autenticar(nombre_rol: str):
    """Pide usuario y contraseña con máximo MAX_INTENTOS intentos (RF-02).

    Llama a AuthService.login() en cada intento.
    Devuelve el objeto Empleado si el login es exitoso,
    o None si se agotan todos los intentos.
    """
    for intento in range(1, MAX_INTENTOS + 1):
        # Muestra en qué intento va el usuario
        console.print(f"\n[bold]Inicio de sesión — {nombre_rol}[/] "
                      f"(intento {intento}/{MAX_INTENTOS})")
        usuario = input("Usuario: ").strip()
        contrasena = input("Contraseña: ").strip()

        # Consulta la base de datos con las credenciales proporcionadas
        empleado = _auth.login(usuario, contrasena, nombre_rol)
        if empleado:
            console.print(f"[green]Bienvenido/a, {empleado.nombre}.[/]")
            return empleado

        console.print("[red]Usuario o contraseña incorrectos.[/]")

    # Se llegó al límite de intentos sin éxito
    return None
