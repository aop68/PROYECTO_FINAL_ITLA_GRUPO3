import mysql.connector
import random
import datetime
import uuid
from faker import Faker
import time

# Inicializar faker para datos en español (República Dominicana)
fake = Faker(['es_DO'])

# Configuración de la base de datos
db_config = {
    'host': 'trolley.proxy.rlwy.net',
    'port': 37649,
    'user': 'root',
    'password': 'ivPrQpJMsVQQVgoHMqvrZwGkmfoBxjjQ',
    'database': 'DBusuarios_app'
}

try:
    # Intentar conectar a la base de datos
    conexion = mysql.connector.connect(**db_config)
    cursor = conexion.cursor()
    print("Conexión a la base de datos establecida correctamente.")
except mysql.connector.Error as error:
    print(f"Error al conectar a la base de datos: {error}")
    exit(1)

# Definiciones de tipos de negocios
TIPOS_NEGOCIOS = [
    "Supermercado", "Restaurante", "Tienda de ropa", "Farmacia", 
    "Gasolinera", "Hotel", "Cafetería", "Tienda de electrónica",
    "Ferretería", "Panadería", "Joyería", "Barbería/Salón", 
    "Gimnasio", "Cine", "Librería"
]

# Provincias de República Dominicana
PROVINCIAS = [
    "Santo Domingo", "Santiago", "La Altagracia", "Puerto Plata", "La Vega", 
    "San Cristóbal", "Duarte", "Espaillat", "San Pedro de Macorís", "La Romana",
    "Barahona", "Monseñor Nouel", "Valverde", "María Trinidad Sánchez", "Samaná"
]

# Zonas (distritos comerciales)
ZONAS = [
    "Zona Colonial", "Piantini", "Naco", "Arroyo Hondo", "Los Jardines",
    "Ensanche Julieta", "Gazcue", "Bella Vista", "Ciudad Nueva", "El Millón",
    "Los Ríos", "Los Prados", "Evaristo Morales", "Paraíso", "Los Cacicazgos"
]

# Modelos de POS
MODELOS_POS = [
    "Verifone VX520", "Ingenico iCT250", "PAX A80", "Clover Mini", 
    "Square Terminal", "Verifone Carbon", "Ingenico Desk 3500", 
    "BBPOS Chipper", "PAX S920", "Dejavoo Z11"
]

def crear_tablas():
    """Crea las tablas necesarias si no existen"""
    # Tabla de clientes (negocios)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        tipo_negocio VARCHAR(100) NOT NULL,
        direccion VARCHAR(255) NOT NULL,
        provincia VARCHAR(100) NOT NULL,
        zona VARCHAR(100) NOT NULL,
        telefono VARCHAR(20) NOT NULL,
        email VARCHAR(255) NOT NULL,
        fecha_registro DATETIME NOT NULL,
        estado ENUM('activo', 'inactivo', 'suspendido') NOT NULL,
        latitud DECIMAL(10, 8) NOT NULL,
        longitud DECIMAL(11, 8) NOT NULL
    )
    ''')
    
    # Tabla de tarifas por transacción
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tarifas_por_transaccion (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cliente_id INT NOT NULL,
        tipo_tarjeta ENUM('crédito', 'débito', 'prepago') NOT NULL,
        porcentaje DECIMAL(5, 2) NOT NULL,
        cuota_fija DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )
    ''')
    
    # Tabla de terminales POS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS terminales_pos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cliente_id INT NOT NULL,
        serial VARCHAR(50) NOT NULL,
        modelo VARCHAR(100) NOT NULL,
        fecha_instalacion DATETIME NOT NULL,
        estado ENUM('activo', 'inactivo', 'mantenimiento', 'reemplazo') NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )
    ''')
    
    # Tabla de transacciones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transacciones (
        id VARCHAR(36) PRIMARY KEY,
        terminal_id INT NOT NULL,
        fecha_hora DATETIME NOT NULL,
        monto DECIMAL(12, 2) NOT NULL,
        tipo_tarjeta ENUM('crédito', 'débito', 'prepago') NOT NULL,
        ultimos_4_digitos VARCHAR(4) NOT NULL,
        estado ENUM('aprobada', 'rechazada', 'cancelada', 'pendiente') NOT NULL,
        motivo_rechazo VARCHAR(255),
        tarifa_aplicada DECIMAL(10, 2),
        FOREIGN KEY (terminal_id) REFERENCES terminales_pos(id)
    )
    ''')
    
    # Tabla de contactos de usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cliente_id INT NOT NULL,
        nombre VARCHAR(255) NOT NULL,
        cargo VARCHAR(100) NOT NULL,
        telefono VARCHAR(20) NOT NULL,
        email VARCHAR(255) NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )
    ''')
    
    conexion.commit()
    print("Tablas creadas correctamente.")

def generar_datos():
    """Genera datos de ejemplo para las tablas"""
    inicio = time.time()
    
    # Generar clientes (negocios)
    print("Generando clientes...")
    clientes_ids = []
    for _ in range(100):
        # Coordenadas aproximadas de República Dominicana
        latitud = random.uniform(17.5, 19.9)
        longitud = random.uniform(-71.7, -68.3)
        
        nombre = fake.company()
        tipo_negocio = random.choice(TIPOS_NEGOCIOS)
        direccion = fake.street_address()
        provincia = random.choice(PROVINCIAS)
        zona = random.choice(ZONAS)
        telefono = fake.phone_number()
        email = fake.company_email()
        fecha_registro = fake.date_time_between(start_date='-3y', end_date='now')
        estado = random.choice(['activo', 'activo', 'activo', 'inactivo', 'suspendido'])
        
        cursor.execute('''
        INSERT INTO clientes (nombre, tipo_negocio, direccion, provincia, zona, telefono, email, 
                            fecha_registro, estado, latitud, longitud)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (nombre, tipo_negocio, direccion, provincia, zona, telefono, email, 
             fecha_registro, estado, latitud, longitud))
        
        cliente_id = cursor.lastrowid
        clientes_ids.append(cliente_id)
    
    conexion.commit()
    print(f"Se generaron {len(clientes_ids)} clientes.")
    
    # Generar tarifas por transacción
    print("Generando tarifas por transacción...")
    for cliente_id in clientes_ids:
        for tipo_tarjeta in ['crédito', 'débito', 'prepago']:
            porcentaje = round(random.uniform(1.5, 4.5), 2)
            cuota_fija = round(random.uniform(0.5, 2.0), 2)
            
            cursor.execute('''
            INSERT INTO tarifas_por_transaccion (cliente_id, tipo_tarjeta, porcentaje, cuota_fija)
            VALUES (%s, %s, %s, %s)
            ''', (cliente_id, tipo_tarjeta, porcentaje, cuota_fija))
    
    conexion.commit()
    print("Tarifas generadas correctamente.")
    
    # Generar terminales POS
    print("Generando terminales POS...")
    terminales_ids = []
    for cliente_id in clientes_ids:
        # Asignar de 1 a 5 terminales por cliente
        num_terminales = random.randint(1, 5)
        for _ in range(num_terminales):
            serial = f"POS-{fake.unique.random_number(digits=8)}"
            modelo = random.choice(MODELOS_POS)
            fecha_instalacion = fake.date_time_between(start_date='-2y', end_date='now')
            estado = random.choices(
                ['activo', 'inactivo', 'mantenimiento', 'reemplazo'],
                weights=[0.85, 0.05, 0.07, 0.03]
            )[0]
            
            cursor.execute('''
            INSERT INTO terminales_pos (cliente_id, serial, modelo, fecha_instalacion, estado)
            VALUES (%s, %s, %s, %s, %s)
            ''', (cliente_id, serial, modelo, fecha_instalacion, estado))
            
            terminal_id = cursor.lastrowid
            terminales_ids.append(terminal_id)
    
    conexion.commit()
    print(f"Se generaron {len(terminales_ids)} terminales POS.")
    
    # Generar transacciones
    print("Generando transacciones...")
    num_transacciones = 10000
    
    # Obtener fecha actual
    ahora = datetime.datetime.now()
    
    # Generar transacciones para los últimos 30 días
    for _ in range(num_transacciones):
        terminal_id = random.choice(terminales_ids)
        
        # Generar fecha en los últimos 30 días con mayor densidad en las últimas 24 horas
        if random.random() < 0.3:  # 30% de transacciones en las últimas 24 horas
            fecha_hora = ahora - datetime.timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
        else:
            fecha_hora = ahora - datetime.timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
        
        monto = round(random.uniform(50, 15000), 2)
        tipo_tarjeta = random.choices(
            ['crédito', 'débito', 'prepago'],
            weights=[0.65, 0.30, 0.05]
        )[0]
        ultimos_4_digitos = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        # Estado de transacción con distribución realista
        estado = random.choices(
            ['aprobada', 'rechazada', 'cancelada', 'pendiente'],
            weights=[0.92, 0.06, 0.015, 0.005]
        )[0]
        
        motivo_rechazo = None
        if estado == 'rechazada':
            motivos = [
                'Fondos insuficientes',
                'Tarjeta vencida',
                'Tarjeta reportada',
                'CVV incorrecto',
                'Límite de crédito excedido',
                'Transacción sospechosa'
            ]
            motivo_rechazo = random.choice(motivos)
        
        # Calcular tarifa aplicada
        cursor.execute('''
        SELECT tp.cliente_id, tp.porcentaje, tp.cuota_fija 
        FROM terminales_pos t 
        JOIN tarifas_por_transaccion tp ON t.cliente_id = tp.cliente_id 
        WHERE t.id = %s AND tp.tipo_tarjeta = %s
        ''', (terminal_id, tipo_tarjeta))
        
        tarifa_datos = cursor.fetchone()
        tarifa_aplicada = None
        if tarifa_datos and estado == 'aprobada':
            porcentaje, cuota_fija = tarifa_datos[1], tarifa_datos[2]
            tarifa_aplicada = round((monto * porcentaje / 100) + cuota_fija, 2)
        
        # Generar UUID
        transaccion_id = str(uuid.uuid4())
        
        cursor.execute('''
        INSERT INTO transacciones (id, terminal_id, fecha_hora, monto, tipo_tarjeta, 
                                ultimos_4_digitos, estado, motivo_rechazo, tarifa_aplicada)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (transaccion_id, terminal_id, fecha_hora, monto, tipo_tarjeta, 
             ultimos_4_digitos, estado, motivo_rechazo, tarifa_aplicada))
    
    conexion.commit()
    print(f"Se generaron {num_transacciones} transacciones.")
    
    # Generar usuarios de contacto
    print("Generando usuarios de contacto...")
    for cliente_id in clientes_ids:
        # Generar de 1 a 3 contactos por cliente
        for _ in range(random.randint(1, 3)):
            nombre = fake.name()
            cargos = [
                'Gerente', 'Supervisor', 'Cajero', 'Administrador', 
                'Dueño', 'Contador', 'Director Financiero'
            ]
            cargo = random.choice(cargos)
            telefono = fake.phone_number()
            email = fake.email()
            
            cursor.execute('''
            INSERT INTO usuarios (cliente_id, nombre, cargo, telefono, email)
            VALUES (%s, %s, %s, %s, %s)
            ''', (cliente_id, nombre, cargo, telefono, email))
    
    conexion.commit()
    print("Usuarios de contacto generados correctamente.")
    
    fin = time.time()
    print(f"Generación de datos completada en {round(fin - inicio, 2)} segundos.")

# Función principal
if __name__ == "__main__":
    # Verificar si ya hay datos
    cursor.execute("SELECT COUNT(*) FROM clientes")
    count = cursor.fetchone()[0]
    
    if count > 0:
        respuesta = input(f"Ya existen {count} registros en la tabla clientes. ¿Desea eliminar los datos existentes? (s/n): ")
        if respuesta.lower() == 's':
            # Desactivar restricciones de clave foránea temporalmente
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Eliminar datos de todas las tablas
            cursor.execute("TRUNCATE TABLE transacciones")
            cursor.execute("TRUNCATE TABLE usuarios")
            cursor.execute("TRUNCATE TABLE terminales_pos")
            cursor.execute("TRUNCATE TABLE tarifas_por_transaccion")
            cursor.execute("TRUNCATE TABLE clientes")
            
            # Reactivar restricciones de clave foránea
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            conexion.commit()
            print("Datos eliminados correctamente.")
            
            # Crear tablas y generar datos
            crear_tablas()
            generar_datos()
        else:
            print("Operación cancelada. No se han realizado cambios.")
    else:
        # No hay datos, crear tablas y generar datos
        crear_tablas()
        generar_datos()
    
    # Cerrar conexión
    cursor.close()
    conexion.close()
    print("Conexión a la base de datos cerrada.") 