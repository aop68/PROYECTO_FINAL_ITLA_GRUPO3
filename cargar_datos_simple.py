import mysql.connector
import pandas as pd
import os
import sys
import time

# Configuración de la base de datos
db_config = {
    'host': 'trolley.proxy.rlwy.net',
    'port': 37649,
    'user': 'root',
    'password': 'ivPrQpJMsVQQVgoHMqvrZwGkmfoBxjjQ',
    'database': 'DBSistemaPOS'
}

def ejecutar_importacion():
    print("Iniciando importación de datos...")
    
    try:
        # Conectar a la base de datos
        print("Conectando a la BD...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("Conexión exitosa")
        
        # Limpiar tablas
        print("Limpiando tablas...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE transacciones")
        cursor.execute("TRUNCATE TABLE terminales_pos")
        cursor.execute("TRUNCATE TABLE tarifas_por_transaccion")
        cursor.execute("TRUNCATE TABLE usuarios")
        cursor.execute("TRUNCATE TABLE clientes")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        
        # Crear tablas si no existen
        print("Verificando tablas...")
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
        
        # Tabla tarifas
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
        
        # Tabla terminales
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
        
        # Obtener rutas de archivos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        carpeta_csv = os.path.join(project_dir, 'datos_entrenamiento_carnet')
        print(f"Carpeta CSV: {carpeta_csv}")
        
        # Importar clientes
        print("Importando clientes...")
        cliente_csv = os.path.join(carpeta_csv, 'clientes_con_provincia_y_zona.csv')
        df_clientes = pd.read_csv(cliente_csv)
        
        for _, row in df_clientes.iterrows():
            try:
                cursor.execute("""
                INSERT INTO clientes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            except Exception as e:
                print(f"Error cliente: {e}")
        conn.commit()
        print(f"Importados {len(df_clientes)} clientes")
        
        # Importar tarifas
        print("Importando tarifas...")
        tarifas_csv = os.path.join(carpeta_csv, 'tarifas (1).csv')
        df_tarifas = pd.read_csv(tarifas_csv)
        
        for _, row in df_tarifas.iterrows():
            try:
                cursor.execute("""
                INSERT INTO tarifas_por_transaccion VALUES (%s, %s, %s, %s, %s)
                """, (
                    row['tarifa_id'],
                    row['cliente_id'],
                    row['porcentaje_tarifa'],
                    row['tarifa_fija'],
                    row['fecha_vigencia']
                ))
            except Exception as e:
                print(f"Error tarifa: {e}")
        conn.commit()
        print(f"Importadas {len(df_tarifas)} tarifas")
        
        # Importar terminales
        print("Importando terminales...")
        terminales_csv = os.path.join(carpeta_csv, 'terminales (1).csv')
        df_terminales = pd.read_csv(terminales_csv)
        
        for _, row in df_terminales.iterrows():
            try:
                cursor.execute("""
                INSERT INTO terminales_pos VALUES (%s, %s, %s, %s, %s)
                """, (
                    row['terminal_id'],
                    row['cliente_id'],
                    row['modelo'],
                    row['fecha_instalacion'],
                    row['estado']
                ))
            except Exception as e:
                print(f"Error terminal: {e}")
        conn.commit()
        print(f"Importados {len(df_terminales)} terminales")
        
        # Importar transacciones
        print("Importando transacciones...")
        transacciones_csv = os.path.join(carpeta_csv, 'transacciones (1).csv')
        df_transacciones = pd.read_csv(transacciones_csv)
        
        contador = 0
        for _, row in df_transacciones.iterrows():
            try:
                cursor.execute("""
                INSERT INTO transacciones VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['transaccion_id'],
                    row['terminal_id'],
                    row['fecha_hora'],
                    row['monto'],
                    row['tipo_tarjeta'],
                    row['aprobada'],
                    row['referencia']
                ))
                contador += 1
                if contador % 100 == 0:
                    conn.commit()
                    print(f"  {contador}/{len(df_transacciones)} transacciones")
            except Exception as e:
                print(f"Error transacción: {e}")
        conn.commit()
        print(f"Importadas {contador} transacciones")
        
        # Importar usuarios
        print("Importando usuarios...")
        usuarios_csv = os.path.join(carpeta_csv, 'usuarios (1).csv')
        df_usuarios = pd.read_csv(usuarios_csv)
        
        for _, row in df_usuarios.iterrows():
            try:
                cursor.execute("""
                INSERT INTO usuarios VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    row['usuario_id'],
                    row['cliente_id'],
                    row['nombre_contacto'],
                    row['correo_contacto'],
                    row['telefono_contacto'],
                    row['genero']
                ))
            except Exception as e:
                print(f"Error usuario: {e}")
        conn.commit()
        print(f"Importados {len(df_usuarios)} usuarios")
        
        print("¡Importación finalizada con éxito!")
        
    except Exception as e:
        print(f"Error global: {e}")
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    inicio = time.time()
    ejecutar_importacion()
    fin = time.time()
    print(f"Tiempo total: {fin - inicio:.2f} segundos") 