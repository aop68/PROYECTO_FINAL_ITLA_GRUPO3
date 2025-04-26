import mysql.connector
import pandas as pd
import os
import time

# Configuración de la base de datos
db_config = {
    'host': 'trolley.proxy.rlwy.net',
    'port': 37649,
    'user': 'root',
    'password': 'ivPrQpJMsVQQVgoHMqvrZwGkmfoBxjjQ',
    'database': 'DBSistemaPOS'
}

# Función para conectar a la base de datos
def conectar_bd():
    try:
        print("Conectando a la base de datos...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("Conexión exitosa!")
        return conn, cursor
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        exit(1)

# Función para crear las tablas si no existen
def crear_tablas(cursor, conn):
    print("Verificando y creando tablas si no existen...")
    
    # Tabla clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        cliente_id VARCHAR(20) PRIMARY KEY,
        nombre_negocio VARCHAR(255),
        tipo_negocio VARCHAR(100),
        longitud VARCHAR(255),
        latitud VARCHAR(255),
        telefono VARCHAR(20),
        rnc VARCHAR(20),
        provincia VARCHAR(100),
        zona VARCHAR(20)
    )
    """)
    
    # Tabla tarifas_por_transaccion
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarifas_por_transaccion (
        tarifa_id VARCHAR(20) PRIMARY KEY,
        cliente_id VARCHAR(20),
        porcentaje_tarifa DECIMAL(5,2),
        tarifa_fija DECIMAL(10,2),
        fecha_vigencia DATE,
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    """)
    
    # Tabla terminales_pos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS terminales_pos (
        terminal_id VARCHAR(20) PRIMARY KEY,
        cliente_id VARCHAR(20),
        modelo VARCHAR(100),
        fecha_instalacion DATE,
        estado ENUM('Activo','Inactivo','Mantenimiento'),
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    """)
    
    # Tabla transacciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacciones (
        transaccion_id VARCHAR(20) PRIMARY KEY,
        terminal_id VARCHAR(20),
        fecha_hora TIMESTAMP,
        monto DECIMAL(10,2),
        tipo_tarjeta ENUM('credito','debito'),
        aprobada TINYINT(1),
        referencia VARCHAR(255),
        FOREIGN KEY (terminal_id) REFERENCES terminales_pos(terminal_id)
    )
    """)
    
    # Tabla usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        usuario_id VARCHAR(20) PRIMARY KEY,
        cliente_id VARCHAR(20),
        nombre_contacto VARCHAR(255),
        correo_contacto VARCHAR(255),
        telefono_contacto VARCHAR(20),
        genero VARCHAR(10),
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    """)
    
    conn.commit()
    print("Tablas verificadas correctamente.")

# Función para limpiar tablas existentes
def limpiar_tablas(cursor, conn):
    print("Limpiando tablas existentes...")
    
    # Desactivar restricciones de clave foránea temporalmente
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # Eliminar datos existentes
    cursor.execute("TRUNCATE TABLE transacciones")
    cursor.execute("TRUNCATE TABLE terminales_pos")
    cursor.execute("TRUNCATE TABLE tarifas_por_transaccion")
    cursor.execute("TRUNCATE TABLE usuarios")
    cursor.execute("TRUNCATE TABLE clientes")
    
    # Reactivar restricciones de clave foránea
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    conn.commit()
    print("Tablas limpiadas correctamente.")

# Función para importar datos de CSV
def importar_datos_csv():
    # Conectar a la base de datos
    conn, cursor = conectar_bd()
    
    try:
        # Verificar si existen datos
        cursor.execute("SELECT COUNT(*) FROM clientes")
        count = cursor.fetchone()[0]
        
        if count > 0:
            # En modo automático, siempre limpiar tablas
            print("Se encontraron datos existentes. Limpiando tablas automáticamente...")
            limpiar_tablas(cursor, conn)
        else:
            # Crear tablas si no existen
            crear_tablas(cursor, conn)
        
        # Ruta de los archivos CSV - Usar ruta completa
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        carpeta_csv = os.path.join(project_dir, 'datos_entrenamiento_carnet')
        print(f"Buscando archivos CSV en: {carpeta_csv}")
        
        # 1. Importar clientes
        print("Importando datos de clientes...")
        cliente_csv = os.path.join(carpeta_csv, 'clientes_con_provincia_y_zona.csv')
        print(f"Archivo de clientes: {cliente_csv}")
        df_clientes = pd.read_csv(cliente_csv)
        
        for _, row in df_clientes.iterrows():
            try:
                cursor.execute("""
                INSERT INTO clientes (cliente_id, nombre_negocio, tipo_negocio, longitud, latitud, telefono, rnc, provincia, zona)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['cliente_id'],
                    row['nombre_negocio'],
                    row['tipo_negocio'],
                    row['longitud'],
                    row['latitud'],
                    row['telefono'],
                    row['rnc'],
                    row['provincia'],
                    row['zona']
                ))
            except mysql.connector.Error as err:
                print(f"Error al insertar cliente {row['cliente_id']}: {err}")
        
        conn.commit()
        print(f"Importados {len(df_clientes)} clientes.")
        
        # 2. Importar tarifas
        print("Importando datos de tarifas...")
        tarifas_csv = os.path.join(carpeta_csv, 'tarifas (1).csv')
        print(f"Archivo de tarifas: {tarifas_csv}")
        df_tarifas = pd.read_csv(tarifas_csv)
        
        for _, row in df_tarifas.iterrows():
            try:
                cursor.execute("""
                INSERT INTO tarifas_por_transaccion (tarifa_id, cliente_id, porcentaje_tarifa, tarifa_fija, fecha_vigencia)
                VALUES (%s, %s, %s, %s, %s)
                """, (
                    row['tarifa_id'],
                    row['cliente_id'],
                    row['porcentaje_tarifa'],
                    row['tarifa_fija'],
                    row['fecha_vigencia']
                ))
            except mysql.connector.Error as err:
                print(f"Error al insertar tarifa {row['tarifa_id']}: {err}")
        
        conn.commit()
        print(f"Importadas {len(df_tarifas)} tarifas.")
        
        # 3. Importar terminales
        print("Importando datos de terminales...")
        terminales_csv = os.path.join(carpeta_csv, 'terminales (1).csv')
        print(f"Archivo de terminales: {terminales_csv}")
        df_terminales = pd.read_csv(terminales_csv)
        
        for _, row in df_terminales.iterrows():
            try:
                cursor.execute("""
                INSERT INTO terminales_pos (terminal_id, cliente_id, modelo, fecha_instalacion, estado)
                VALUES (%s, %s, %s, %s, %s)
                """, (
                    row['terminal_id'],
                    row['cliente_id'],
                    row['modelo'],
                    row['fecha_instalacion'],
                    row['estado']
                ))
            except mysql.connector.Error as err:
                print(f"Error al insertar terminal {row['terminal_id']}: {err}")
        
        conn.commit()
        print(f"Importados {len(df_terminales)} terminales.")
        
        # 4. Importar transacciones
        print("Importando datos de transacciones...")
        transacciones_csv = os.path.join(carpeta_csv, 'transacciones (1).csv')
        print(f"Archivo de transacciones: {transacciones_csv}")
        df_transacciones = pd.read_csv(transacciones_csv)
        
        for i, row in df_transacciones.iterrows():
            try:
                cursor.execute("""
                INSERT INTO transacciones (transaccion_id, terminal_id, fecha_hora, monto, tipo_tarjeta, aprobada, referencia)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['transaccion_id'],
                    row['terminal_id'],
                    row['fecha_hora'],
                    row['monto'],
                    row['tipo_tarjeta'],
                    row['aprobada'],
                    row['referencia']
                ))
                
                # Commit cada 100 transacciones para evitar bloqueos
                if i % 100 == 0:
                    conn.commit()
                    print(f"  Progreso: {i}/{len(df_transacciones)} transacciones")
            
            except mysql.connector.Error as err:
                print(f"Error al insertar transacción {row['transaccion_id']}: {err}")
        
        conn.commit()
        print(f"Importadas {len(df_transacciones)} transacciones.")
        
        # 5. Importar usuarios
        print("Importando datos de usuarios...")
        usuarios_csv = os.path.join(carpeta_csv, 'usuarios (1).csv')
        print(f"Archivo de usuarios: {usuarios_csv}")
        df_usuarios = pd.read_csv(usuarios_csv)
        
        for _, row in df_usuarios.iterrows():
            try:
                cursor.execute("""
                INSERT INTO usuarios (usuario_id, cliente_id, nombre_contacto, correo_contacto, telefono_contacto, genero)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    row['usuario_id'],
                    row['cliente_id'],
                    row['nombre_contacto'],
                    row['correo_contacto'],
                    row['telefono_contacto'],
                    row['genero']
                ))
            except mysql.connector.Error as err:
                print(f"Error al insertar usuario {row['usuario_id']}: {err}")
        
        conn.commit()
        print(f"Importados {len(df_usuarios)} usuarios.")
        
        print("¡Importación completada con éxito!")
        
    except Exception as e:
        print(f"Error durante la importación: {e}")
    finally:
        # Cerrar conexión
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    inicio = time.time()
    importar_datos_csv()
    fin = time.time()
    print(f"Tiempo total de ejecución: {fin - inicio:.2f} segundos") 