DROP TABLE IF EXISTS reserva_evento;
DROP TABLE IF EXISTS reserva_juego;
DROP TABLE IF EXISTS reserva;
DROP TABLE IF EXISTS linea_pedido;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS evento;
DROP TABLE IF EXISTS juego;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS estado;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS usuario;

CREATE TABLE usuario(
    id INT AUTO_INCREMENT,
    email VARCHAR(80) NOT NULL UNIQUE,
    nombre VARCHAR(50) NOT NULL, 
    password VARCHAR(255) NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE cliente (
    id INT,
    username VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY(id),
    FOREIGN KEY(id) REFERENCES usuario(id) ON DELETE CASCADE
); 

CREATE TABLE admin(
    id INT,
    username VARCHAR(50) NOT NULL UNIQUE,
    fecha_alta DATE NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(id) REFERENCES usuario(id) ON DELETE CASCADE
);

CREATE TABLE estado(
    id INT AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO estado (id, name) VALUES
(1, 'Procesando'),
(2, 'Preparando'),
(3, 'Enviado'),
(4, 'Recibido');

CREATE TABLE pedido(
    numero_pedido INT AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    fecha_pedido DATE NOT NULL, 
    precio_total DECIMAL(10,2) NOT NULL, 
    estado INT NOT NULL,
    PRIMARY KEY (numero_pedido),
    FOREIGN KEY (estado) REFERENCES estado(id),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id)
);

CREATE TABLE producto(
    id INT AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL, 
    descripcion VARCHAR(500),
    categoria VARCHAR(50), 
    precio_unitario DECIMAL(10,2) NOT NULL, 
    stock INT NOT NULL DEFAULT 0,
    disponibilidad BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id)
);

CREATE TABLE linea_pedido(
    id INT AUTO_INCREMENT,
    numero_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (numero_pedido) REFERENCES pedido(numero_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES producto(id)
);

CREATE TABLE evento(
    id INT AUTO_INCREMENT,
    id_admin INT NOT NULL,
    nombre_evento VARCHAR(100) NOT NULL, 
    fecha DATE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (id_admin) REFERENCES admin(id)
);

CREATE TABLE juego(
    id INT AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL, 
    precio_dia DECIMAL(10,2) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE reserva(
    id INT AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    tipo INT NOT NULL,
    cantidad INT NOT NULL,
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id)
);

CREATE TABLE reserva_juego(
    id_reserva INT, 
    id_juego INT,
    fecha_inicio DATE NOT NULL, 
    fecha_fin DATE NOT NULL, 
    precio_total DECIMAL(10,2) NOT NULL,
    PRIMARY KEY(id_reserva, id_juego),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id) ON DELETE CASCADE,
    FOREIGN KEY (id_juego) REFERENCES juego(id)
);

CREATE TABLE reserva_evento(
    id_reserva INT, 
    id_evento INT,
    PRIMARY KEY(id_reserva, id_evento),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id) ON DELETE CASCADE,
    FOREIGN KEY (id_evento) REFERENCES evento(id)
);