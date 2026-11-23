USE gimnasio

-- tabla rol
CREATE TABLE rol(
    codigo varchar(4) PRIMARY KEY,
    nombreRol varchar(20) NOT NULL
)

-- tabla horario
CREATE TABLE horario(
    codigo varchar(3) PRIMARY KEY,
    dia varchar(8),
    horainicio TIME NOT NULL CHECK,
    horafin TIME NOT NULL CHECK,
)

-- tabla beneficio
CREATE TABLE beneficio(
    codigo varchar(3) PRIMARY KEY,
    descripcion varchar(100) NOT NULL
)

-- tabla especialidad
CREATE TABLE especialidad(
    codigo varchar(5) PRIMARY KEY,
    nombre varchar(30) NOT NULL,
    descripcion varchar(200)
)

-- tabla tipo_membresia
CREATE TABLE tipo_membresia(
    codigo varchar(4) PRIMARY KEY,
    nombre varchar(30) NOT NULL,
    duracionDias INT NOT NULL CHECK (duracionDias > 0),
    monto DECIMAL(10, 2) NOT NULL CHECK (monto > 0)
)

-- tabla empleado
CREATE TABLE empleado(
    codigo INT PRIMARY KEY,
    nombrepila varchar(30) NOT NULL,
    primerapellido varchar(25) NOT NULL,
    segundoapellido varchar(25),
    nombreusuario varchar(20) NOT NULL,
    correo varchar(40) NOT NULL,
    contrasena varchar(20) NOT NULL,
    estado boolean NOT NULL,
    horario varchar(3),
    rol varchar(4),
    FOREIGN KEY (horario) REFERENCES horario(codigo),
    FOREIGN KEY (rol) REFERENCES rol(codigo)
)

-- tabla clase
CREATE TABLE clase(
    codigo varchar(10) PRIMARY KEY,
    nombre varchar(50) NOT NULL,
    dia varchar(15) NOT NULL,
    horaInicio TIME NOT NULL,
    horaFin TIME NOT NULL,
    cupoMax INT NOT NULL,
    publico boolean NOT NULL,
    estado varchar(15) NOT NULL,
    especialidad varchar(5) NOT NULL,
    empleado INT NOT NULL,
    FOREIGN KEY (especialidad) REFERENCES especialidad(codigo),
    FOREIGN KEY (empleado) REFERENCES empleado(codigo)
)

-- tabla incluye
CREATE TABLE incluye(
    tipo_membresia varchar(4),
    beneficio varchar(3),
    PRIMARY KEY (tipo_membresia, beneficio),
    FOREIGN KEY (tipo_membresia) REFERENCES tipo_membresia(codigo),
    FOREIGN KEY (beneficio) REFERENCES beneficio(codigo)
)

-- tabla se_sigue_en
CREATE TABLE se_sigue_en(
    rutina varchar(45),
    asistencia varchar(10),
    PRIMARY KEY (rutina, asistencia)
    FOREIGN KEY (rutina) REFERENCES rutina(codigo),
    FOREIGN KEY (asistencia) REFERENCES asistencia(codigo)
)