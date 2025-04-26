import os
import mysql.connector
from mysql.connector import Error
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo env/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class LMStudioAgent:
    def __init__(self):
        # Configuración de la API
        self.api_url = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta")
        # Obtener API key, o usar clave por defecto si no está en .env
        self.api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyDjHOgB1lkHNRzQBLx_0bIm6d7cTRqwKNE"
        # Nombre del modelo Gemini a usar
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
        print(f"Gemini Agent inicializado con modelo {self.model_name}")
        
        # Modo sin conexión solo si no hay clave en absoluto
        self.offline_mode = False
        
        # Configuración de la base de datos POS
        self.db_config = {
            "host": os.getenv("DB_POS_HOST", "localhost"),
            "port": int(os.getenv("DB_POS_PORT", "3306")),
            "user": os.getenv("DB_POS_USER", "root"),
            "password": os.getenv("DB_POS_PASSWORD", ""),
            "database": os.getenv("DB_POS_DATABASE", "DBSistemaPOS")
        }
        
        print(f"Configuración de BD POS: {self.db_config}")
        
        # Probar la conexión
        if not self.offline_mode:
            self.test_connection()
        else:
            print("Modo sin conexión activado - no se probará la conexión con Gemini")
    
    def test_connection(self):
        try:
            # Verificar que la API de Gemini está accesible
            url = f"{self.api_url}/models?key={self.api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                print(f"Conexión exitosa con la API de Gemini.")
            else:
                print(f"Error al conectar con la API de Gemini. Código: {response.status_code}")
                self.offline_mode = True
        except Exception as e:
            print(f"Error al conectar con la API de Gemini: {e}")
            self.offline_mode = True
    
    def generate_response(self, prompt, max_tokens=1000, temperature=0.7):
        """Genera una respuesta basada en el prompt dado, con posibilidad de consultar la base de datos."""
        
        if self.offline_mode:
            # Modo sin conexión - devolver respuesta simulada
            return {
                "response": "Estoy funcionando en modo sin conexión. Mi tarea normal sería:\n\n1) Recibir tu pregunta en lenguaje natural\n2) Convertirla a una consulta SQL válida para la base de datos DBSistemaPOS\n3) Ejecutar esa consulta en la base de datos\n4) Convertir los resultados técnicos a una explicación clara en lenguaje natural\n\nActualmente no puedo conectarme a la base de datos o a la API de Gemini, pero cuando esté en línea podré ayudarte a consultar información sobre transacciones, clientes, terminales y todos los datos relacionados con el sistema POS.",
                "db_used": "No (modo sin conexión)",
                "sql_query": "N/A",
                "data": []
            }
        
        # Generar la consulta SQL a partir del prompt del usuario
        sql_response = self.nl_to_sql(prompt, "")
        
        if not sql_response or not sql_response.get('success', False):
            # Mostrar el error real al usuario
            error_msg = sql_response.get('error', 'Error desconocido') if sql_response else 'Error desconocido'
            return {
                "response": f"Error al generar la consulta SQL: {error_msg}",
                "db_used": "No",
                "sql_query": sql_response.get('sql_query', 'N/A') if sql_response else 'N/A',
                "data": []
            }
        
        # Ejecutar la consulta SQL en la base de datos
        db_response = self.execute_sql_query(sql_response['sql_query'])
        
        if not db_response or not db_response.get('success', False):
            return {
                "response": f"Generé la consulta SQL pero hubo un problema al ejecutarla: {db_response.get('error', 'Error desconocido')}",
                "db_used": "Parcialmente",
                "sql_query": sql_response['sql_query'],
                "data": []
            }
        
        # Generar respuesta en lenguaje natural a partir de los resultados
        nl_response = self.results_to_nl(prompt, db_response['data'])
        
        return {
            "response": nl_response,
            "db_used": "Sí",
            "sql_query": sql_response['sql_query'],
            "data": db_response['data']
        }
    
    def nl_to_sql(self, prompt, table):
        """Convierte un texto en paréntesis a consulta SQL válida para MySQL para la tabla especificada usando Gemini."""
        # Crear el prompt incluyendo la tabla y la base DBSistemaPOS
        gemini_prompt = (
            f"Para la base de datos DBSistemaPOS, tabla {table}, convierte el texto que está entre paréntesis "
            f"en una consulta SQL válida para MySQL: ({prompt})"
        )
        
        try:
            # Llamar al modelo configurado de Gemini con prompt de tabla
            url = f"{self.api_url}/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": gemini_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1024
                }
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Error al generar consulta SQL. Código: {response.status_code}"
                }
            
            result = response.json()
            
            # Extraer el texto generado
            if 'candidates' in result and len(result['candidates']) > 0:
                sql_query = result['candidates'][0]['content']['parts'][0]['text']
                
                # Limpiar la consulta SQL
                sql_query = sql_query.strip()
                if sql_query.startswith('```sql'):
                    sql_query = sql_query[6:]
                if sql_query.endswith('```'):
                    sql_query = sql_query[:-3]
                sql_query = sql_query.strip()
                
                return {
                    "success": True,
                    "sql_query": sql_query
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudo generar una consulta SQL"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al generar consulta SQL: {str(e)}"
            }
    
    def get_db_schema(self):
        """Obtiene el esquema de la base de datos."""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Obtener las tablas de la base de datos
            cursor.execute("SHOW TABLES")
            tables = [table[f"Tables_in_{self.db_config['database']}"] for table in cursor.fetchall()]
            
            schema = []
            
            # Para cada tabla, obtener la estructura
            for table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                table_info = {
                    "table_name": table,
                    "columns": []
                }
                
                for col in columns:
                    column_info = {
                        "column_name": col["Field"],
                        "data_type": col["Type"],
                        "is_primary": col["Key"] == "PRI",
                        "is_nullable": col["Null"] == "YES"
                    }
                    table_info["columns"].append(column_info)
                
                schema.append(table_info)
            
            cursor.close()
            conn.close()
            
            return schema
            
        except Exception as e:
            print(f"Error al obtener el esquema de la BD: {str(e)}")
            return None
    
    def execute_sql_query(self, sql_query):
        """Ejecuta una consulta SQL en la base de datos."""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "data": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al ejecutar consulta SQL: {str(e)}"
            }
    
    def results_to_nl(self, original_question, results):
        """Convierte los resultados de la consulta SQL a una respuesta en lenguaje natural."""
        
        # Si no hay resultados, devolver un mensaje adecuado
        if not results:
            return "No se encontraron resultados que coincidan con tu consulta."
        
        try:
            # Convertir los resultados a formato JSON
            results_json = json.dumps(results, ensure_ascii=False, indent=2)
            
            # Crear el prompt para Gemini
            gemini_prompt = f"""
            Responde a la siguiente pregunta del usuario en español basándote en los resultados de la consulta SQL:
            
            PREGUNTA DEL USUARIO:
            {original_question}
            
            RESULTADOS DE LA CONSULTA:
            {results_json}
            
            Proporciona una respuesta clara, concisa y en lenguaje natural que responda directamente a la pregunta del usuario.
            No menciones que estás interpretando resultados SQL, simplemente proporciona la información solicitada.
            """
            
            # Llamar al modelo configurado de Gemini para interpretación
            url = f"{self.api_url}/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": gemini_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024
                }
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code != 200:
                return f"No pude interpretar los resultados de la consulta. Error {response.status_code}"
            
            result = response.json()
            
            # Extraer el texto generado
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "No pude generar una interpretación de los resultados."
            
        except Exception as e:
            return f"Error al interpretar los resultados: {str(e)}" 