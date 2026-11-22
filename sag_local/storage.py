"""
storage.py — Almacén central en memoria para sag_local.

Todas las colecciones son listas de dicts (igual que mysql-connector
devuelve con dictionary=True), así los services son fáciles de leer.
Los contadores _id simulan el AUTO_INCREMENT de MySQL.
"""
import datetime

# ---------------------------------------------------------------------------
# Contadores de ID (simulan AUTO_INCREMENT)
# ---------------------------------------------------------------------------
_counters: dict[str, int] = {
    "rol": 3,
    "empleado": 3,
    "horario": 4,
    "cliente": 2,
    "celular": 3,
    "tipo_membresia": 3,
    "beneficio": 3,
    "metodo_pago": 2,
    "membresia": 1,
    "pago": 1,
    "especialidad": 2,
    "clase": 2,
    "inscripcion_clase": 0,
    "rutina": 0,
    "asistencia_gym": 0,
}


def next_id(tabla: str) -> int:
    _counters[tabla] += 1
    return _counters[tabla]


# ---------------------------------------------------------------------------
# Datos de ejemplo
# ---------------------------------------------------------------------------
roles: list[dict] = [
    {"codigo_rol": 1, "nombre": "Recepcionista"},
    {"codigo_rol": 2, "nombre": "Entrenador"},
    {"codigo_rol": 3, "nombre": "Administrador"},
]

empleados: list[dict] = [
    {
        "codigo_empleado": 1, "nombre": "Laura Gómez", "usuario": "lgomez",
        "contrasena": "1234", "correo": "lgomez@gym.com",
        "estado": True, "codigo_rol": 1,
    },
    {
        "codigo_empleado": 2, "nombre": "Carlos Ruiz", "usuario": "cruiz",
        "contrasena": "1234", "correo": "cruiz@gym.com",
        "estado": True, "codigo_rol": 2,
    },
    {
        "codigo_empleado": 3, "nombre": "Ana Torres", "usuario": "atorres",
        "contrasena": "1234", "correo": "atorres@gym.com",
        "estado": True, "codigo_rol": 3,
    },
]

horarios: list[dict] = [
    {"codigo_horario": 1, "dia": "Lunes",    "hora_inicio": datetime.time(8, 0),  "hora_fin": datetime.time(16, 0), "codigo_empleado": 2},
    {"codigo_horario": 2, "dia": "Miércoles","hora_inicio": datetime.time(8, 0),  "hora_fin": datetime.time(16, 0), "codigo_empleado": 2},
    {"codigo_horario": 3, "dia": "Viernes",  "hora_inicio": datetime.time(8, 0),  "hora_fin": datetime.time(16, 0), "codigo_empleado": 2},
    {"codigo_horario": 4, "dia": "Lunes",    "hora_inicio": datetime.time(9, 0),  "hora_fin": datetime.time(17, 0), "codigo_empleado": 1},
]

clientes: list[dict] = [
    {
        "codigo_cliente": 1, "nombre": "Miguel", "apellido_paterno": "Hernández",
        "apellido_materno": "Soto", "fecha_nacimiento": datetime.date(1995, 6, 15),
        "colonia": "Centro", "calle": "Av. Principal 10", "estado": True,
    },
    {
        "codigo_cliente": 2, "nombre": "Sofía", "apellido_paterno": "Martínez",
        "apellido_materno": "López", "fecha_nacimiento": datetime.date(2000, 3, 22),
        "colonia": "Chapultepec", "calle": "Calle 5 #22", "estado": True,
    },
]

celulares: list[dict] = [
    {"codigo_celular": 1, "numero": "6641234567", "codigo_cliente": 1},
    {"codigo_celular": 2, "numero": "6649876543", "codigo_cliente": 1},
    {"codigo_celular": 3, "numero": "6641112233", "codigo_cliente": 2},
]

tipos_membresia: list[dict] = [
    {"codigo_tipo": 1, "nombre": "Mensual",   "duracion_dias": 30,  "monto": 500.0},
    {"codigo_tipo": 2, "nombre": "Trimestral","duracion_dias": 90,  "monto": 1300.0},
    {"codigo_tipo": 3, "nombre": "Anual",     "duracion_dias": 365, "monto": 4500.0},
]

beneficios: list[dict] = [
    {"codigo_beneficio": 1, "descripcion": "Acceso ilimitado al gimnasio"},
    {"codigo_beneficio": 2, "descripcion": "1 clase grupal por semana"},
    {"codigo_beneficio": 3, "descripcion": "Clases grupales ilimitadas"},
]

# Tabla pivot TIPO_MEMBRESIA_BENEFICIO
tipo_membresia_beneficio: list[dict] = [
    {"codigo_tipo": 1, "codigo_beneficio": 1},
    {"codigo_tipo": 2, "codigo_beneficio": 1},
    {"codigo_tipo": 2, "codigo_beneficio": 2},
    {"codigo_tipo": 3, "codigo_beneficio": 1},
    {"codigo_tipo": 3, "codigo_beneficio": 3},
]

metodos_pago: list[dict] = [
    {"codigo_metodo": 1, "nombre": "Efectivo",        "estado": True},
    {"codigo_metodo": 2, "nombre": "Tarjeta de débito","estado": True},
]

membresias: list[dict] = [
    {
        "codigo_membresia": "MEM-00000001",
        "fecha_inicio": datetime.date(2026, 11, 1),
        "fecha_vencimiento": datetime.date(2026, 12, 1),
        "estado": "activa",
        "fecha_cancelacion": None,
        "motivo_cancelacion": None,
        "codigo_cliente": 1,
        "codigo_tipo": 1,
        "codigo_empleado": 1,
    },
]

pagos: list[dict] = [
    {
        "codigo_pago": 1, "fecha": datetime.date(2026, 11, 1),
        "monto": 500.0, "codigo_membresia": "MEM-00000001", "codigo_metodo": 1,
    },
]

especialidades: list[dict] = [
    {"codigo_especialidad": 1, "nombre": "Spinning",  "descripcion": "Ciclismo indoor de alta intensidad"},
    {"codigo_especialidad": 2, "nombre": "Yoga",      "descripcion": "Flexibilidad y meditación"},
]

clases: list[dict] = [
    {
        "codigo_clase": 1, "nombre": "Spinning Matutino", "dia": "Lunes",
        "hora_inicio": datetime.time(7, 0), "hora_fin": datetime.time(8, 0),
        "cupo_maximo": 15, "inscritos": 0, "es_publica": True, "estado": True,
        "codigo_especialidad": 1, "codigo_empleado": 2,
    },
    {
        "codigo_clase": 2, "nombre": "Yoga Relajante", "dia": "Miércoles",
        "hora_inicio": datetime.time(18, 0), "hora_fin": datetime.time(19, 0),
        "cupo_maximo": 10, "inscritos": 0, "es_publica": True, "estado": True,
        "codigo_especialidad": 2, "codigo_empleado": 2,
    },
]

inscripciones_clase: list[dict] = []
rutinas: list[dict] = []
asistencias_gym: list[dict] = []
