CREATE DATABASE IF NOT EXISTS sag_gimnasio
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sag_gimnasio;

-- =========================================================
-- 1. TABLAS CATÁLOGO Y BASE (SIN LLAVES FORÁNEAS)
-- =========================================================

-- Tabla: rol
CREATE TABLE rol (
    codigo VARCHAR(4) PRIMARY KEY,
    nombreRol VARCHAR(20) NOT NULL UNIQUE
);

-- Tabla: horario
CREATE TABLE horario (
    codigo VARCHAR(3) PRIMARY KEY,
    dia VARCHAR(15) NOT NULL,
    horaInicio TIME NOT NULL,
    horaFin TIME NOT NULL,
    CONSTRAINT chk_horario_horas CHECK (horaFin > horaInicio)
);

-- Tabla: beneficio
CREATE TABLE beneficio (
    codigo VARCHAR(3) PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

-- Tabla: tipo_membresia
CREATE TABLE tipo_membresia (
    codigo VARCHAR(4) PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    duracionDias INT NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    CONSTRAINT chk_tipo_membresia_duracion CHECK (duracionDias > 0),
    CONSTRAINT chk_tipo_membresia_monto CHECK (monto >= 0)
);

-- Tabla: especialidad
CREATE TABLE especialidad (
    codigo VARCHAR(5) PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    descripcion VARCHAR(200) NOT NULL
);

-- Tabla: metodo_pago
CREATE TABLE metodo_pago (
    codigo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla: cliente
CREATE TABLE cliente (
    codigo INT AUTO_INCREMENT PRIMARY KEY,
    nombrePila VARCHAR(30) NOT NULL,
    primerApellido VARCHAR(30) NOT NULL,
    segundoApellido VARCHAR(30) NULL,
    fechaNacimiento DATE NOT NULL,
    colonia VARCHAR(40) NOT NULL,
    calle VARCHAR(40) NOT NULL,
    estado VARCHAR(15) NOT NULL DEFAULT 'Activo'
);

-- =========================================================
-- 2. TABLAS DEPENDIENTES DE NIVEL 1
-- =========================================================

-- Tabla: incluye
CREATE TABLE incluye (
    tipo_membresia VARCHAR(4) NOT NULL,
    beneficio VARCHAR(3) NOT NULL,
    PRIMARY KEY (tipo_membresia, beneficio),
    CONSTRAINT fk_incluye_tipo_membresia FOREIGN KEY (tipo_membresia)
        REFERENCES tipo_membresia(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_incluye_beneficio FOREIGN KEY (beneficio)
        REFERENCES beneficio(codigo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Tabla: empleado
CREATE TABLE empleado (
    codigo INT PRIMARY KEY,
    nombrePila VARCHAR(30) NOT NULL,
    primerApellido VARCHAR(25) NOT NULL,
    segundoApellido VARCHAR(25) NULL,
    nombreUsuario VARCHAR(20) NOT NULL UNIQUE,
    correo VARCHAR(40) NOT NULL UNIQUE,
    contrasena VARCHAR(20) NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    horario VARCHAR(3) NOT NULL,
    rol VARCHAR(4) NOT NULL,
    CONSTRAINT chk_empleado_contrasena CHECK (CHAR_LENGTH(contrasena) >= 6),
    CONSTRAINT fk_empleado_horario FOREIGN KEY (horario)
        REFERENCES horario(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_empleado_rol FOREIGN KEY (rol)
        REFERENCES rol(codigo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Tabla: Celular_Cliente
CREATE TABLE Celular_Cliente (
    cliente INT NOT NULL,
    numCel VARCHAR(10) NOT NULL,
    PRIMARY KEY (cliente, numCel),
    CONSTRAINT fk_celular_cliente FOREIGN KEY (cliente)
        REFERENCES cliente(codigo) ON UPDATE CASCADE ON DELETE CASCADE
);

-- =========================================================
-- 3. TABLAS OPERATIVAS DE NIVEL 2
-- =========================================================

-- Tabla: clase
CREATE TABLE clase (
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    dia VARCHAR(15) NOT NULL,
    horaInicio TIME NOT NULL,
    horaFin TIME NOT NULL,
    cupoMax INT NOT NULL,
    publico BOOLEAN NOT NULL DEFAULT TRUE,
    estado VARCHAR(15) NOT NULL DEFAULT 'Activa',
    especialidad VARCHAR(5) NOT NULL,
    empleado INT NOT NULL,
    CONSTRAINT chk_clase_cupo CHECK (cupoMax > 0),
    CONSTRAINT fk_clase_especialidad FOREIGN KEY (especialidad)
        REFERENCES especialidad(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_clase_empleado FOREIGN KEY (empleado)
        REFERENCES empleado(codigo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Tabla: rutina
CREATE TABLE rutina (
    codigo VARCHAR(10) PRIMARY KEY,
    objetivo VARCHAR(150) NOT NULL,
    nombre VARCHAR(60) NOT NULL,
    fecha DATE NOT NULL,
    descripcion VARCHAR(250) NOT NULL,
    frecuencia VARCHAR(30) NOT NULL,
    duracionSesion VARCHAR(30) NOT NULL,
    totalSesiones VARCHAR(25) NOT NULL,
    descanso VARCHAR(30) NOT NULL,
    empleado INT NOT NULL,
    cliente INT NOT NULL,
    CONSTRAINT fk_rutina_empleado FOREIGN KEY (empleado)
        REFERENCES empleado(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_rutina_cliente FOREIGN KEY (cliente)
        REFERENCES cliente(codigo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Tabla: membresia
CREATE TABLE membresia (
    codigo INT AUTO_INCREMENT PRIMARY KEY,
    fechaInicio DATE NOT NULL,
    fechaVencimiento DATE NOT NULL,
    fechaCancelacion DATE NULL,
    motivoCancelacion VARCHAR(150) NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activa',
    tipo_membresia VARCHAR(4) NOT NULL,
    empleado INT NOT NULL,
    cliente INT NOT NULL,
    CONSTRAINT fk_membresia_tipo FOREIGN KEY (tipo_membresia)
        REFERENCES tipo_membresia(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_membresia_empleado FOREIGN KEY (empleado)
        REFERENCES empleado(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_membresia_cliente FOREIGN KEY (cliente)
        REFERENCES cliente(codigo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- =========================================================
-- 4. TABLAS DE DETALLE Y TRANSACCIONES (NIVEL 3 Y 4)
-- =========================================================

-- Tabla: inscripcion_clase
CREATE TABLE inscripcion_clase (
    codigo INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'Activa',
    observaciones VARCHAR(40) NULL,
    cliente INT NOT NULL,
    clase VARCHAR(10) NOT NULL,
    CONSTRAINT fk_inscripcion_cliente FOREIGN KEY (cliente)
        REFERENCES cliente(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inscripcion_clase FOREIGN KEY (clase)
        REFERENCES clase(codigo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Tabla: pago
CREATE TABLE pago (
    codigo INT AUTO_INCREMENT PRIMARY KEY,
    monto DECIMAL(10, 2) NOT NULL,
    fechaPago DATE NOT NULL,
    metodo_pago INT NOT NULL,
    membresia INT NOT NULL,
    CONSTRAINT chk_pago_monto CHECK (monto >= 0),
    CONSTRAINT fk_pago_metodo FOREIGN KEY (metodo_pago)
        REFERENCES metodo_pago(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pago_membresia FOREIGN KEY (membresia)
        REFERENCES membresia(codigo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Tabla: Enfoque_dia
CREATE TABLE Enfoque_dia (
    numero INT AUTO_INCREMENT PRIMARY KEY,
    dia INT NOT NULL,
    enfoque VARCHAR(60) NOT NULL,
    rutina VARCHAR(10) NOT NULL,
    CONSTRAINT fk_enfoque_rutina FOREIGN KEY (rutina)
        REFERENCES rutina(codigo) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Tabla: ejercicio_enfoque
CREATE TABLE ejercicio_enfoque (
    numero INT AUTO_INCREMENT PRIMARY KEY,
    ejercicio VARCHAR(120) NOT NULL,
    enfoqueDia INT NOT NULL,
    CONSTRAINT fk_ejercicio_enfoque_dia FOREIGN KEY (enfoqueDia)
        REFERENCES Enfoque_dia(numero) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Tabla: sesion_entrenamiento
CREATE TABLE sesion_entrenamiento (
    numero INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    horaInicio TIME NOT NULL,
    horaFinal TIME NOT NULL,
    observaciones VARCHAR(200) NULL,
    cliente INT NOT NULL,
    enfoqueDia INT NULL,
    CONSTRAINT fk_sesion_cliente FOREIGN KEY (cliente)
        REFERENCES cliente(codigo) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_sesion_enfoque_dia FOREIGN KEY (enfoqueDia)
        REFERENCES Enfoque_dia(numero) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Tabla: asistencia_clase
CREATE TABLE asistencia_clase (
    numero INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    inscripcionClase INT NOT NULL,
    CONSTRAINT fk_asistencia_inscripcion FOREIGN KEY (inscripcionClase)
        REFERENCES inscripcion_clase(codigo) ON UPDATE CASCADE ON DELETE RESTRICT
);