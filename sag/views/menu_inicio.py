from rich.console import Console
from rich.table import Table
from rich import box

from services.auth_service import AuthService, MAX_INTENTOS

console = Console()
_auth = AuthService()


def mostrar_bienvenida() -> None:
    console.rule("[bold cyan]SAG – Sistema Administrativo de Gimnasios[/]")
    console.print()


def ejecutar() -> None:
    """Bucle principal del menú de inicio (RF-01, RF-02, RF-03)."""
    from views.menu_recepcionista import ejecutar as menu_recepcionista
    from views.menu_entrenador import ejecutar as menu_entrenador
    from views.menu_administrador import ejecutar as menu_administrador

    roles = {
        "1": ("Recepcionista", menu_recepcionista),
        "2": ("Entrenador", menu_entrenador),
        "3": ("Administrador", menu_administrador),
    }

    while True:
        mostrar_bienvenida()

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

        nombre_rol, menu_fn = roles[opcion]
        empleado = _autenticar(nombre_rol)
        if empleado is None:
            # Se agotaron los intentos
            console.print("[bold red]Acceso bloqueado. Cerrando el programa.[/]")
            break

        menu_fn(empleado)
        # Al cerrar sesión regresa aquí (RF-03)


def _autenticar(nombre_rol: str):
    """Pide usuario y contraseña con máximo 3 intentos (RF-02).

    Devuelve el objeto Empleado o None si se agotaron los intentos.
    """
    for intento in range(1, MAX_INTENTOS + 1):
        console.print(f"\n[bold]Inicio de sesión — {nombre_rol}[/] "
                      f"(intento {intento}/{MAX_INTENTOS})")
        usuario = input("Usuario: ").strip()
        contrasena = input("Contraseña: ").strip()

        empleado = _auth.login(usuario, contrasena, nombre_rol)
        if empleado:
            console.print(f"[green]Bienvenido/a, {empleado.nombre}.[/]")
            return empleado

        console.print("[red]Usuario o contraseña incorrectos.[/]")

    return None
