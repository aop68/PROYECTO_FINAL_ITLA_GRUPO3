from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from utils.lmstudio_agent import LMStudioAgent
from datetime import datetime, timedelta
import json
import requests
import random

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave secreta segura

# Configuración de la base de datos
db_config = {
    'host': 'trolley.proxy.rlwy.net',
    'port': 37649,
    'user': 'root',
    'password': 'ivPrQpJMsVQQVgoHMqvrZwGkmfoBxjjQ',
    'database': 'DBSistemaPOS'
}

# Inicializar el agente LM Studio
agent = LMStudioAgent()

# Configuración de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Clase de usuario para Flask-Login
class User(UserMixin):
    def __init__(self, id, nombre, email, cargo, imagen=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.cargo = cargo
        self.imagen = imagen

# Función para conectar a la base de datos
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None

# Función para crear la tabla de usuarios si no existe
def create_users_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'usuarios'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Verificar la estructura de la tabla
            cursor.execute("DESCRIBE usuarios")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            print(f"Estructura actual de la tabla: {column_names}")
            
            # Si no tiene la estructura correcta, recrearla
            required_columns = ['id', 'nombre', 'email', 'password', 'cargo', 'imagen']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"Faltan columnas: {missing_columns}. Recreando la tabla...")
                cursor.execute("DROP TABLE usuarios")
                # Recrear la tabla con la estructura correcta
                cursor.execute('''
                    CREATE TABLE usuarios (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nombre VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        password VARCHAR(255) NOT NULL,
                        cargo VARCHAR(50) NOT NULL,
                        imagen VARCHAR(255)
                    )
                ''')
                print("Tabla recreada correctamente")
        else:
            # Crear tabla de usuarios con la estructura correcta
            cursor.execute('''
                CREATE TABLE usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    cargo VARCHAR(50) NOT NULL,
                    imagen VARCHAR(255)
                )
            ''')
            print("Tabla usuarios creada correctamente")
        
        # Verificar si ya existe un administrador
        try:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cargo = 'administrador'")
            admin_count = cursor.fetchone()[0]
            
            # Si no hay administrador, crear uno por defecto
            if admin_count == 0:
                hashed_password = generate_password_hash('admin123')
                cursor.execute('''
                    INSERT INTO usuarios (nombre, email, password, cargo)
                    VALUES (%s, %s, %s, %s)
                ''', ('Administrador', 'admin@empresa.com', hashed_password, 'administrador'))
                print("Usuario administrador creado correctamente")
        except mysql.connector.Error as err:
            print(f"Error al verificar o crear administrador: {err}")
        
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error al crear la tabla de usuarios: {err}")

# Crear tabla de usuarios al iniciar la aplicación
create_users_table()

# Callback para cargar un usuario
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user_data:
        # Asegurar que las rutas de imágenes no tengan doble prefijo 'static'
        imagen = user_data['imagen']
        if imagen and imagen.startswith('static/'):
            imagen = imagen.replace('static/', '', 1)
        
        return User(
            id=user_data['id'],
            nombre=user_data['nombre'],
            email=user_data['email'],
            cargo=user_data['cargo'],
            imagen=imagen
        )
    return None

# Ruta de inicio
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(
                id=user_data['id'],
                nombre=user_data['nombre'],
                email=user_data['email'],
                cargo=user_data['cargo'],
                imagen=user_data['imagen']
            )
            login_user(user)
            session['user_id'] = user_data['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas. Intente nuevamente.', 'error')
    
    return render_template('login.html')

# Ruta de cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Ruta del dashboard principal
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', active='descriptiva')

# Rutas para las diferentes vistas del dashboard
@app.route('/dashboard/descriptiva')
@login_required
def descriptiva():
    return render_template('dashboard.html', active='descriptiva')

@app.route('/dashboard/cuota_mercado')
@login_required
def cuota_mercado():
    return render_template('dashboard.html', active='cuota_mercado')

@app.route('/dashboard/predictiva')
@login_required
def predictiva():
    return render_template('dashboard.html', active='predictiva')

@app.route('/dashboard/tiempo_real')
@login_required
def tiempo_real():
    return render_template('dashboard.html', active='tiempo_real')

@app.route('/dashboard/datos_globales')
@login_required
def datos_globales():
    # Vista para la sección de Datos Globales
    return render_template('dashboard.html', active='datos_globales')

# Ruta para el agente LLM
@app.route('/agente')
@login_required
def agente():
    return render_template('agente.html')

# API para listar tablas de DBSistemaPOS
@app.route('/api/agent/tables', methods=['GET'])
@login_required
def agent_tables():
    # Listar tablas directamente usando la conexión de la app
    conn = get_db_connection()
    if not conn:
        return jsonify({'tables': [], 'success': False, 'error': 'No se pudo conectar a la base de datos'}), 500
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        rows = cursor.fetchall()
        # rows como lista de tuplas [('clientes',), ('transacciones',)...]
        tables = [row[0] for row in rows]
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'tables': [], 'success': False, 'error': str(e)}), 500
    cursor.close()
    conn.close()
    return jsonify({'tables': tables, 'success': True})

# API para procesar preguntas a través del agente
@app.route('/api/agent/ask', methods=['POST'])
@login_required
def agent_ask():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'No se proporcionó ninguna pregunta', 'success': False}), 400
    question = data['question']
    table = data.get('table')
    if not table:
        return jsonify({'error': 'No se especificó la tabla', 'success': False}), 400
    # Generar la consulta SQL usando Gemini (sólo SQL), con la tabla especificada
    sql_resp = agent.nl_to_sql(question, table)
    if not sql_resp.get('success', False):
        return jsonify({'error': sql_resp.get('error', 'Error al generar la consulta SQL'), 'success': False}), 400
    sql_query = sql_resp['sql_query']
    # Ejecutar la consulta en DBSistemaPOS
    try:
        conn = mysql.connector.connect(
            host=agent.db_config['host'],
            port=agent.db_config['port'],
            user=agent.db_config['user'],
            password=agent.db_config['password'],
            database=agent.db_config['database']
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Generar respuesta en lenguaje natural a partir de los resultados
        try:
            answer = agent.results_to_nl(question, rows)
        except Exception as e:
            answer = f"Error al interpretar resultados: {str(e)}"
        return jsonify({'sql_query': sql_query, 'data': rows, 'answer': answer, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# API para verificar el estado de la conexión con LM Studio
@app.route('/api/agent/status', methods=['GET'])
@login_required
def agent_status():
    try:
        # Verificar la conexión a Gemini API
        if agent.offline_mode:
            return jsonify({
                'connected': False,
                'error': 'API key de Gemini no configurada o inválida',
                'api_url': agent.api_url
            })
        
        # Intentar realizar una solicitud simple para verificar la conexión
        url = f"{agent.api_url}/models?key={agent.api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return jsonify({
                'connected': True,
                'api_url': agent.api_url
            })
        else:
            return jsonify({
                'connected': False,
                'error': f"Error al conectar con la API de Gemini. Código: {response.status_code}",
                'api_url': agent.api_url
            })
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e),
            'api_url': agent.api_url
        })

# Ruta para la gestión de equipo
@app.route('/equipo')
@login_required
def equipo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('equipo.html', usuarios=usuarios)

# Ruta para agregar usuario
@app.route('/equipo/agregar', methods=['GET', 'POST'])
@login_required
def agregar_usuario():
    if current_user.cargo != 'administrador':
        flash('No tiene permisos para realizar esta acción', 'error')
        return redirect(url_for('equipo'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        cargo = request.form['cargo']
        
        imagen = None
        if 'imagen' in request.files and request.files['imagen'].filename:
            file = request.files['imagen']
            filename = secure_filename(file.filename)
            file_path = os.path.join('static/images', filename)
            file.save(file_path)
            imagen = file_path
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (nombre, email, password, cargo, imagen)
                VALUES (%s, %s, %s, %s, %s)
            ''', (nombre, email, hashed_password, cargo, imagen))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Usuario agregado correctamente', 'success')
            return redirect(url_for('equipo'))
        except mysql.connector.Error as err:
            flash(f'Error al agregar usuario: {err}', 'error')
    
    return render_template('agregar_usuario.html')

# Ruta para editar usuario
@app.route('/equipo/editar/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(user_id):
    if current_user.cargo != 'administrador' and current_user.id != user_id:
        flash('No tiene permisos para realizar esta acción', 'error')
        return redirect(url_for('equipo'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('equipo'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        cargo = request.form['cargo']
        
        # Si es administrador, puede cambiar el cargo, si no, mantiene el cargo original
        if current_user.cargo != 'administrador':
            cargo = usuario['cargo']
        
        # Mantener la imagen original si no se proporciona una nueva
        imagen = usuario['imagen']
        if 'imagen' in request.files and request.files['imagen'].filename:
            file = request.files['imagen']
            filename = secure_filename(file.filename)
            file_path = os.path.join('static/images', filename)
            file.save(file_path)
            imagen = file_path
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Si se proporciona una nueva contraseña, actualizarla
            if request.form.get('password'):
                hashed_password = generate_password_hash(request.form['password'])
                cursor.execute('''
                    UPDATE usuarios 
                    SET nombre = %s, email = %s, password = %s, cargo = %s, imagen = %s
                    WHERE id = %s
                ''', (nombre, email, hashed_password, cargo, imagen, user_id))
            else:
                cursor.execute('''
                    UPDATE usuarios 
                    SET nombre = %s, email = %s, cargo = %s, imagen = %s
                    WHERE id = %s
                ''', (nombre, email, cargo, imagen, user_id))
                
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('equipo'))
        except mysql.connector.Error as err:
            flash(f'Error al actualizar usuario: {err}', 'error')
    
    return render_template('editar_usuario.html', usuario=usuario)

# Modificar la ruta de las imágenes para que funcione en PythonAnywhere
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# API para obtener datos del dashboard en tiempo real
@app.route('/api/dashboard/data')
@login_required
def dashboard_data():
    # Obtener parámetros de filtro
    fecha = request.args.get('fecha', 'hoy')
    tipo_tarjeta = request.args.get('tipo_tarjeta', 'todas')
    provincia = request.args.get('provincia', 'todas')
    tipo_negocio = request.args.get('tipo_negocio', 'todos')
    
    # Modo sin conexión - usar datos de ejemplo directamente
    use_demo_data = True
    
    if use_demo_data:
        print("Usando datos de demostración para el dashboard (modo sin conexión)")
        # Datos de ejemplo para el dashboard
        return jsonify({
            "kpis": {
                "num_transacciones": 24873,
                "monto_total": 15200000,
                "tasa_aprobacion": 94.2,
                "porcentaje_credito": 65,
                "porcentaje_debito": 30,
                "porcentaje_prepago": 5,
                "comparativa_transacciones": 12.3,
                "comparativa_monto": 8.7
            },
            "transacciones_por_hora": [
                {"hora": f"{h}:00", "total": 570 + (h * 90) + random.randint(-50, 50), 
                 "credito": 350 + (h * 50) + random.randint(-30, 30), 
                 "debito": 220 + (h * 40) + random.randint(-20, 20),
                 "prepago": 20 + (h * 5) + random.randint(-5, 5)} 
                for h in range(24)
            ],
            "terminales": {
                "activos": 4500,
                "inactivos": 450,
                "mantenimiento": 950,
                "reemplazo": 100
            },
            "tipos_negocio": [
                {"tipo_negocio": "Supermercados", "transacciones": 7462, "porcentaje": 32},
                {"tipo_negocio": "Restaurantes", "transacciones": 6218, "porcentaje": 27},
                {"tipo_negocio": "Gasolineras", "transacciones": 4975, "porcentaje": 22},
                {"tipo_negocio": "Farmacias", "transacciones": 4123, "porcentaje": 18},
                {"tipo_negocio": "Tiendas", "transacciones": 2095, "porcentaje": 9}
            ],
            "mapa_transacciones": [
                {"nombre_negocio": "Supermercado Nacional", "latitud": 18.4861, "longitud": -69.9312, "provincia": "Santo Domingo", "transacciones": 1200, "monto_total": 3500000},
                {"nombre_negocio": "Plaza Central", "latitud": 19.4517, "longitud": -70.6986, "provincia": "Santiago", "transacciones": 980, "monto_total": 2800000},
                {"nombre_negocio": "Jumbo", "latitud": 18.5001, "longitud": -69.8893, "provincia": "Santo Domingo", "transacciones": 850, "monto_total": 2400000},
                {"nombre_negocio": "CCN", "latitud": 18.4825, "longitud": -69.9129, "provincia": "Santo Domingo", "transacciones": 720, "monto_total": 1950000},
                {"nombre_negocio": "La Sirena", "latitud": 18.4755, "longitud": -69.8952, "provincia": "Santo Domingo", "transacciones": 680, "monto_total": 1800000}
            ],
            "transacciones_recientes": [
                {"transaccion_id": "T284955", "fecha_hora": datetime.now().isoformat(), "nombre_negocio": "Supermercado Nacional", "monto": 2450.00, "tipo_tarjeta": "crédito", "estado": "aprobada", "ultimos_4_digitos": "5432"},
                {"transaccion_id": "T284954", "fecha_hora": (datetime.now() - timedelta(minutes=2)).isoformat(), "nombre_negocio": "Restaurante Mitre", "monto": 1350.50, "tipo_tarjeta": "débito", "estado": "aprobada", "ultimos_4_digitos": "1234"},
                {"transaccion_id": "T284953", "fecha_hora": (datetime.now() - timedelta(minutes=5)).isoformat(), "nombre_negocio": "Farmacia Carol", "monto": 540.00, "tipo_tarjeta": "crédito", "estado": "rechazada", "ultimos_4_digitos": "8765"},
                {"transaccion_id": "T284952", "fecha_hora": (datetime.now() - timedelta(minutes=8)).isoformat(), "nombre_negocio": "Texaco Av 27 de Febrero", "monto": 1800.00, "tipo_tarjeta": "débito", "estado": "aprobada", "ultimos_4_digitos": "9876"},
                {"transaccion_id": "T284951", "fecha_hora": (datetime.now() - timedelta(minutes=10)).isoformat(), "nombre_negocio": "La Sirena", "monto": 3200.75, "tipo_tarjeta": "prepago", "estado": "aprobada", "ultimos_4_digitos": "6543"}
            ],
            "filtros": {
                "provincias": ["Santo Domingo", "Santiago", "La Altagracia", "Puerto Plata", "La Romana"],
                "tipos_negocio": ["Supermercado", "Restaurante", "Farmacia", "Gasolinera", "Hotel"]
            }
        })
    
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(
            host="trolley.proxy.rlwy.net",
            port=37649,
            user="root",
            password="ivPrQpJMsVQQVgoHMqvrZwGkmfoBxjjQ",
            database="DBSistemaPOS"
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Construir cláusulas WHERE basadas en filtros
        where_clauses = []
        
        # Filtro de fecha
        if fecha == 'hoy':
            where_clauses.append("DATE(t.fecha_hora) = CURDATE()")
        elif fecha == 'ayer':
            where_clauses.append("DATE(t.fecha_hora) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)")
        elif fecha == 'semana':
            where_clauses.append("t.fecha_hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        elif fecha == 'mes':
            where_clauses.append("t.fecha_hora >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
        
        # Filtro de tipo de tarjeta
        if tipo_tarjeta != 'todas':
            where_clauses.append(f"t.tipo_tarjeta = '{tipo_tarjeta}'")
        
        # Filtro de provincia
        if provincia != 'todas':
            where_clauses.append(f"c.provincia = '{provincia}'")
        
        # Filtro de tipo de negocio
        if tipo_negocio != 'todos':
            where_clauses.append(f"c.tipo_negocio = '{tipo_negocio}'")
        
        # Construir cláusula WHERE completa
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Obtener datos para KPIs
        kpi_query = f"""
        SELECT 
            COUNT(*) AS num_transacciones,
            COALESCE(SUM(t.monto), 0) AS monto_total,
            (SUM(CASE WHEN t.estado = 'aprobada' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)) * 100 AS tasa_aprobacion,
            SUM(CASE WHEN t.tipo_tarjeta = 'crédito' THEN 1 ELSE 0 END) AS num_credito,
            SUM(CASE WHEN t.tipo_tarjeta = 'débito' THEN 1 ELSE 0 END) AS num_debito,
            SUM(CASE WHEN t.tipo_tarjeta = 'prepago' THEN 1 ELSE 0 END) AS num_prepago
        FROM transacciones t
        JOIN terminales_pos tp ON t.terminal_id = tp.id
        JOIN clientes c ON tp.cliente_id = c.id
        WHERE {where_clause}
        """
        
        cursor.execute(kpi_query)
        kpi_data = cursor.fetchone()
        
        # Asegurar que no haya valores nulos
        for key in kpi_data:
            if kpi_data[key] is None:
                kpi_data[key] = 0
        
        # Calcular porcentajes de tipos de tarjeta
        total_transacciones = kpi_data['num_credito'] + kpi_data['num_debito'] + kpi_data['num_prepago']
        porcentaje_credito = 0
        porcentaje_debito = 0
        porcentaje_prepago = 0
        
        if total_transacciones > 0:
            porcentaje_credito = (kpi_data['num_credito'] / total_transacciones) * 100
            porcentaje_debito = (kpi_data['num_debito'] / total_transacciones) * 100
            porcentaje_prepago = (kpi_data['num_prepago'] / total_transacciones) * 100
        
        # Obtener datos para comparativas con día anterior
        comparativa_query = f"""
        SELECT 
            COUNT(*) AS num_transacciones_ayer,
            COALESCE(SUM(t.monto), 0) AS monto_total_ayer
        FROM transacciones t
        JOIN terminales_pos tp ON t.terminal_id = tp.id
        JOIN clientes c ON tp.cliente_id = c.id
        WHERE DATE(t.fecha_hora) = DATE_SUB(
            CASE 
                WHEN '{fecha}' = 'hoy' THEN CURDATE()
                WHEN '{fecha}' = 'ayer' THEN DATE_SUB(CURDATE(), INTERVAL 1 DAY)
                ELSE CURDATE() 
            END, 
            INTERVAL 1 DAY
        )
        """
        
        if tipo_tarjeta != 'todas':
            comparativa_query += f" AND t.tipo_tarjeta = '{tipo_tarjeta}'"
        
        if provincia != 'todas':
            comparativa_query += f" AND c.provincia = '{provincia}'"
        
        if tipo_negocio != 'todos':
            comparativa_query += f" AND c.tipo_negocio = '{tipo_negocio}'"
        
        cursor.execute(comparativa_query)
        comp_data = cursor.fetchone()
        
        # Asegurar que no haya valores nulos en los datos comparativos
        if not comp_data:
            comp_data = {
                'num_transacciones_ayer': 0, 
                'monto_total_ayer': 0
            }
        else:
            for key in comp_data:
                if comp_data[key] is None:
                    comp_data[key] = 0
        
        # Calcular comparativas con manejo de casos edge
        num_transacciones_ayer = comp_data['num_transacciones_ayer'] or 1  # Evitar división por cero
        monto_total_ayer = comp_data['monto_total_ayer'] or 1  # Evitar división por cero
        
        # Si cualquiera de los valores es cero, establecer la comparativa según corresponda
        if num_transacciones_ayer == 0 and kpi_data['num_transacciones'] > 0:
            comparativa_transacciones = 100  # 100% de incremento (de 0 a algo)
        elif num_transacciones_ayer == 0 and kpi_data['num_transacciones'] == 0:
            comparativa_transacciones = 0  # Sin cambio (ambos son cero)
        else:
            comparativa_transacciones = ((kpi_data['num_transacciones'] - num_transacciones_ayer) / num_transacciones_ayer) * 100
        
        if monto_total_ayer == 0 and kpi_data['monto_total'] > 0:
            comparativa_monto = 100  # 100% de incremento (de 0 a algo)
        elif monto_total_ayer == 0 and kpi_data['monto_total'] == 0:
            comparativa_monto = 0  # Sin cambio (ambos son cero)
        else:
            comparativa_monto = ((kpi_data['monto_total'] - monto_total_ayer) / monto_total_ayer) * 100
        
        # Obtener datos de transacciones por hora
        hora_query = f"""
        SELECT 
            HOUR(t.fecha_hora) AS hora,
            COUNT(t.id) AS total,
            SUM(CASE WHEN t.tipo_tarjeta = 'crédito' THEN 1 ELSE 0 END) AS credito,
            SUM(CASE WHEN t.tipo_tarjeta = 'débito' THEN 1 ELSE 0 END) AS debito,
            SUM(CASE WHEN t.tipo_tarjeta = 'prepago' THEN 1 ELSE 0 END) AS prepago
        FROM transacciones t
        JOIN terminales_pos tp ON t.terminal_id = tp.id
        JOIN clientes c ON tp.cliente_id = c.id
        WHERE {where_clause}
        GROUP BY HOUR(t.fecha_hora)
        ORDER BY hora
        """
        
        cursor.execute(hora_query)
        horas_data = cursor.fetchall()
        
        # Asegurar que los datos por hora no tengan valores nulos
        for item in horas_data:
            for key in item:
                if item[key] is None and key != 'hora':
                    item[key] = 0
        
        # Si no hay datos por hora, crear datos de ejemplo
        if not horas_data:
            horas_data = [
                {'hora': h, 'total': 0, 'credito': 0, 'debito': 0, 'prepago': 0} 
                for h in range(24)
            ]
        
        # Obtener datos de estado de terminales
        terminales_query = """
        SELECT 
            SUM(CASE WHEN estado = 'activo' THEN 1 ELSE 0 END) AS activos,
            SUM(CASE WHEN estado = 'inactivo' THEN 1 ELSE 0 END) AS inactivos,
            SUM(CASE WHEN estado = 'mantenimiento' THEN 1 ELSE 0 END) AS mantenimiento,
            SUM(CASE WHEN estado = 'reemplazo' THEN 1 ELSE 0 END) AS reemplazo
        FROM terminales_pos
        """
        
        cursor.execute(terminales_query)
        terminales_data = cursor.fetchone()
        
        # Asegurar que no haya valores nulos en datos de terminales
        if not terminales_data:
            terminales_data = {'activos': 0, 'inactivos': 0, 'mantenimiento': 0, 'reemplazo': 0}
        else:
            for key in terminales_data:
                if terminales_data[key] is None:
                    terminales_data[key] = 0
        
        # Obtener datos de tipos de negocios
        tipos_negocio_query = f"""
        SELECT 
            c.tipo_negocio,
            COUNT(t.id) AS transacciones,
            COALESCE(
                COUNT(t.id) / NULLIF(
                    (SELECT COUNT(*) 
                     FROM transacciones t2
                     JOIN terminales_pos tp2 ON t2.terminal_id = tp2.id
                     JOIN clientes c2 ON tp2.cliente_id = c2.id
                     WHERE {where_clause}),
                    0
                ),
                0
            ) * 100 AS porcentaje
        FROM transacciones t
        JOIN terminales_pos tp ON t.terminal_id = tp.id
        JOIN clientes c ON tp.cliente_id = c.id
        WHERE {where_clause}
        GROUP BY c.tipo_negocio
        ORDER BY transacciones DESC
        LIMIT 10
        """
        
        cursor.execute(tipos_negocio_query)
        tipos_negocio_data = cursor.fetchall()
        
        # Asegurar que no haya valores nulos en datos de tipos de negocio
        for item in tipos_negocio_data:
            for key in item:
                if item[key] is None and key != 'tipo_negocio':
                    item[key] = 0
        
        # Si no hay datos de tipos de negocio, crear datos de ejemplo
        if not tipos_negocio_data:
            tipos_negocio_data = [
                {'tipo_negocio': 'Supermercado', 'transacciones': 0, 'porcentaje': 0},
                {'tipo_negocio': 'Restaurante', 'transacciones': 0, 'porcentaje': 0},
                {'tipo_negocio': 'Farmacia', 'transacciones': 0, 'porcentaje': 0}
            ]
        
        # Obtener datos para el mapa de calor
        mapa_query = f"""
        SELECT 
            c.nombre,
            c.latitud,
            c.longitud,
            c.provincia,
            COUNT(t.id) AS transacciones,
            COALESCE(SUM(t.monto), 0) AS monto_total
        FROM transacciones t
        JOIN terminales_pos tp ON t.terminal_id = tp.id
        JOIN clientes c ON tp.cliente_id = c.id
        WHERE {where_clause} AND c.latitud IS NOT NULL AND c.longitud IS NOT NULL
        GROUP BY c.nombre, c.latitud, c.longitud, c.provincia
        """
        
        cursor.execute(mapa_query)
        mapa_data = cursor.fetchall()
        
        # Asegurar que no haya valores nulos en datos del mapa
        for item in mapa_data:
            for key in item:
                if item[key] is None and key not in ['nombre', 'provincia']:
                    item[key] = 0
        
        # Si no hay datos para el mapa, crear datos de ejemplo
        if not mapa_data:
            mapa_data = [
                {
                    'nombre': 'Ejemplo Supermercado', 
                    'latitud': 18.4861, 
                    'longitud': -69.9312, 
                    'provincia': 'Santo Domingo',
                    'transacciones': 0,
                    'monto_total': 0
                }
            ]
        
        # Obtener transacciones recientes
        recientes_query = f"""
        SELECT 
            t.id AS transaccion_id,
            t.fecha_hora,
            c.nombre AS nombre_negocio,
            t.monto,
            t.tipo_tarjeta,
            t.estado,
            t.ultimos_4_digitos
        FROM transacciones t
        JOIN terminales_pos tp ON t.terminal_id = tp.id
        JOIN clientes c ON tp.cliente_id = c.id
        WHERE {where_clause}
        ORDER BY t.fecha_hora DESC
        LIMIT 10
        """
        
        cursor.execute(recientes_query)
        recientes_data = cursor.fetchall()
        
        # Asegurar que no haya valores nulos en transacciones recientes
        for item in recientes_data:
            for key in item:
                if item[key] is None and key not in ['fecha_hora', 'nombre_negocio', 'ultimos_4_digitos']:
                    item[key] = 0
        
        # Si no hay transacciones recientes, crear datos de ejemplo
        if not recientes_data:
            now = datetime.now()
            recientes_data = [
                {
                    'transaccion_id': f'T{i}00000',
                    'fecha_hora': now - timedelta(minutes=i*5),
                    'nombre_negocio': f'Ejemplo Negocio {i}',
                    'monto': 1000 + (i * 100),
                    'tipo_tarjeta': 'crédito' if i % 2 == 0 else 'débito',
                    'estado': 'aprobada' if i % 3 != 0 else 'rechazada',
                    'ultimos_4_digitos': f"{random.randint(1000, 9999)}"
                }
                for i in range(1, 6)
            ]
        
        # Obtener lista de provincias para el filtro
        cursor.execute("SELECT DISTINCT provincia FROM clientes ORDER BY provincia")
        provincias = [item['provincia'] for item in cursor.fetchall() if item['provincia']]
        
        # Si no hay provincias, agregar algunas por defecto
        if not provincias:
            provincias = ['Santo Domingo', 'Santiago', 'La Altagracia', 'Puerto Plata', 'La Romana']
        
        # Obtener lista de tipos de negocios para el filtro
        cursor.execute("SELECT DISTINCT tipo_negocio FROM clientes ORDER BY tipo_negocio")
        tipos_negocio = [item['tipo_negocio'] for item in cursor.fetchall() if item['tipo_negocio']]
        
        # Si no hay tipos de negocio, agregar algunos por defecto
        if not tipos_negocio:
            tipos_negocio = ['Supermercado', 'Restaurante', 'Farmacia', 'Gasolinera', 'Hotel']
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        # Preparar datos de respuesta
        response_data = {
            "kpis": {
                "num_transacciones": kpi_data['num_transacciones'] or 0,
                "monto_total": float(kpi_data['monto_total'] or 0),
                "tasa_aprobacion": float(kpi_data['tasa_aprobacion'] or 0),
                "porcentaje_credito": porcentaje_credito,
                "porcentaje_debito": porcentaje_debito,
                "porcentaje_prepago": porcentaje_prepago,
                "comparativa_transacciones": comparativa_transacciones,
                "comparativa_monto": comparativa_monto
            },
            "transacciones_por_hora": [
                {
                    "hora": f"{item['hora']}:00",
                    "total": item['total'],
                    "credito": item['credito'],
                    "debito": item['debito'],
                    "prepago": item.get('prepago', 0)
                } for item in horas_data
            ],
            "terminales": {
                "activos": terminales_data['activos'] or 0,
                "inactivos": terminales_data['inactivos'] or 0,
                "mantenimiento": terminales_data['mantenimiento'] or 0,
                "reemplazo": terminales_data.get('reemplazo', 0) or 0
            },
            "tipos_negocio": [
                {
                    "tipo_negocio": item['tipo_negocio'],
                    "transacciones": item['transacciones'],
                    "porcentaje": float(item['porcentaje'] or 0)
                } for item in tipos_negocio_data
            ],
            "mapa_transacciones": [
                {
                    "nombre_negocio": item['nombre'],
                    "latitud": float(item['latitud']),
                    "longitud": float(item['longitud']),
                    "provincia": item['provincia'],
                    "transacciones": item['transacciones'],
                    "monto_total": float(item['monto_total'] or 0)
                } for item in mapa_data
            ],
            "transacciones_recientes": [
                {
                    "transaccion_id": item['transaccion_id'],
                    "fecha_hora": item['fecha_hora'].isoformat() if isinstance(item['fecha_hora'], datetime) else item['fecha_hora'],
                    "nombre_negocio": item['nombre_negocio'],
                    "monto": float(item['monto'] or 0),
                    "tipo_tarjeta": item['tipo_tarjeta'],
                    "estado": item['estado'],
                    "ultimos_4_digitos": item.get('ultimos_4_digitos', '****')
                } for item in recientes_data
            ],
            "filtros": {
                "provincias": provincias,
                "tipos_negocio": tipos_negocio
            }
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error en API dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # En caso de error, usar los mismos datos de ejemplo
        return jsonify({
            "kpis": {
                "num_transacciones": 24873,
                "monto_total": 15200000,
                "tasa_aprobacion": 94.2,
                "porcentaje_credito": 65,
                "porcentaje_debito": 30,
                "porcentaje_prepago": 5,
                "comparativa_transacciones": 12.3,
                "comparativa_monto": 8.7
            },
            "transacciones_por_hora": [
                {"hora": f"{h}:00", "total": 570 + (h * 90) + random.randint(-50, 50), 
                 "credito": 350 + (h * 50) + random.randint(-30, 30), 
                 "debito": 220 + (h * 40) + random.randint(-20, 20),
                 "prepago": 20 + (h * 5) + random.randint(-5, 5)} 
                for h in range(24)
            ],
            "terminales": {
                "activos": 4500,
                "inactivos": 450,
                "mantenimiento": 950,
                "reemplazo": 100
            },
            "tipos_negocio": [
                {"tipo_negocio": "Supermercados", "transacciones": 7462, "porcentaje": 32},
                {"tipo_negocio": "Restaurantes", "transacciones": 6218, "porcentaje": 27},
                {"tipo_negocio": "Gasolineras", "transacciones": 4975, "porcentaje": 22},
                {"tipo_negocio": "Farmacias", "transacciones": 4123, "porcentaje": 18},
                {"tipo_negocio": "Tiendas", "transacciones": 2095, "porcentaje": 9}
            ],
            "mapa_transacciones": [
                {"nombre_negocio": "Supermercado Nacional", "latitud": 18.4861, "longitud": -69.9312, "provincia": "Santo Domingo", "transacciones": 1200, "monto_total": 3500000},
                {"nombre_negocio": "Plaza Central", "latitud": 19.4517, "longitud": -70.6986, "provincia": "Santiago", "transacciones": 980, "monto_total": 2800000},
                {"nombre_negocio": "Jumbo", "latitud": 18.5001, "longitud": -69.8893, "provincia": "Santo Domingo", "transacciones": 850, "monto_total": 2400000},
                {"nombre_negocio": "CCN", "latitud": 18.4825, "longitud": -69.9129, "provincia": "Santo Domingo", "transacciones": 720, "monto_total": 1950000},
                {"nombre_negocio": "La Sirena", "latitud": 18.4755, "longitud": -69.8952, "provincia": "Santo Domingo", "transacciones": 680, "monto_total": 1800000}
            ],
            "transacciones_recientes": [
                {"transaccion_id": "T284955", "fecha_hora": datetime.now().isoformat(), "nombre_negocio": "Supermercado Nacional", "monto": 2450.00, "tipo_tarjeta": "crédito", "estado": "aprobada", "ultimos_4_digitos": "5432"},
                {"transaccion_id": "T284954", "fecha_hora": (datetime.now() - timedelta(minutes=2)).isoformat(), "nombre_negocio": "Restaurante Mitre", "monto": 1350.50, "tipo_tarjeta": "débito", "estado": "aprobada", "ultimos_4_digitos": "1234"},
                {"transaccion_id": "T284953", "fecha_hora": (datetime.now() - timedelta(minutes=5)).isoformat(), "nombre_negocio": "Farmacia Carol", "monto": 540.00, "tipo_tarjeta": "crédito", "estado": "rechazada", "ultimos_4_digitos": "8765"},
                {"transaccion_id": "T284952", "fecha_hora": (datetime.now() - timedelta(minutes=8)).isoformat(), "nombre_negocio": "Texaco Av 27 de Febrero", "monto": 1800.00, "tipo_tarjeta": "débito", "estado": "aprobada", "ultimos_4_digitos": "9876"},
                {"transaccion_id": "T284951", "fecha_hora": (datetime.now() - timedelta(minutes=10)).isoformat(), "nombre_negocio": "La Sirena", "monto": 3200.75, "tipo_tarjeta": "prepago", "estado": "aprobada", "ultimos_4_digitos": "6543"}
            ],
            "filtros": {
                "provincias": ["Santo Domingo", "Santiago", "La Altagracia", "Puerto Plata", "La Romana"],
                "tipos_negocio": ["Supermercado", "Restaurante", "Farmacia", "Gasolinera", "Hotel"]
            }
        })

if __name__ == '__main__':
    # En desarrollo, usar puerto 5000 para evitar conflictos
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # En producción (PythonAnywhere)
    application = app 