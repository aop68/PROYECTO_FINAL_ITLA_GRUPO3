# Configuración de LM Studio para la Aplicación

Este documento explica cómo configurar LM Studio para que funcione como backend de chat en nuestra aplicación.

## Requisitos

1. [LM Studio](https://lmstudio.ai/) - Descarga e instala la última versión desde su sitio web oficial.
2. Un modelo de lenguaje compatible con Llama 3 (recomendado) o cualquier otro modelo que funcione bien con tareas de SQL.

## Pasos para configurar LM Studio

### 1. Instalar LM Studio

- Descarga LM Studio desde [https://lmstudio.ai/](https://lmstudio.ai/)
- Instala la aplicación siguiendo las instrucciones del instalador.

### 2. Descargar un modelo compatible

En LM Studio:
1. Ve a la pestaña "Browse" (Explorar)
2. Busca un modelo de Llama 3 (recomendado) u otro modelo capaz de generar consultas SQL.
3. Haz clic en el botón de descarga para el modelo que deseas usar.
4. Espera a que se complete la descarga.

Modelos recomendados:
- Meta-Llama-3-8B-Instruct 
- Meta-Llama-3-70B-Instruct (si tienes suficiente capacidad de procesamiento)
- Otros modelos capaces de generar consultas SQL

### 3. Configurar el Servidor de Inferencia

Una vez descargado el modelo:

1. En LM Studio, ve a la pestaña "Local Server" (Servidor Local)
2. Selecciona el modelo que descargaste en la lista desplegable
3. Configura los parámetros del servidor:
   - Asegúrate de marcar la opción "OpenAI Compatible Server" (Servidor Compatible con OpenAI)
   - Puerto: 1234 (por defecto, si lo cambias, actualiza también en el archivo .env)
   - Marca "Enable streaming" para mejor experiencia
   - Ajusta los parámetros de inferencia según tu hardware (temperatura, tokens máximos, etc.)

4. Haz clic en "Start Server" (Iniciar Servidor)

### 4. Verificar que el servidor está funcionando

Para verificar que el servidor está funcionando correctamente:

1. Abre un navegador web
2. Navega a: `http://localhost:1234/v1/models`
3. Deberías ver una respuesta JSON con la información del modelo cargado

### 5. Configurar la aplicación

La aplicación ya está configurada para usar el servidor de LM Studio en `http://localhost:1234/v1`. 
Si necesitas cambiar esta URL:

1. Abre el archivo `.env` en la carpeta raíz del proyecto
2. Actualiza la línea `LMSTUDIO_API_URL=http://localhost:1234/v1` con la URL correcta

### 6. Iniciar la aplicación

Ahora puedes iniciar la aplicación Flask:

```bash
python app.py
```

## Solución de problemas

### El indicador de estado muestra "Sin conexión a LM Studio"

1. Verifica que el servidor de LM Studio esté en ejecución
2. Comprueba que el puerto en el archivo .env coincida con el configurado en LM Studio
3. Asegúrate de que no haya un firewall bloqueando la conexión

### Respuestas lentas o errores de tiempo de espera

1. Reduce el tamaño del modelo o ajusta los parámetros de inferencia en LM Studio
2. Asegúrate de que tu hardware sea suficiente para el modelo que estás utilizando
3. Aumenta el parámetro `timeout` en el archivo `utils/lmstudio_agent.py` si es necesario

### Errores en las consultas SQL generadas

1. Asegúrate de usar un modelo que tenga buen rendimiento con tareas de SQL
2. Si el modelo genera consultas SQL incorrectas, considera ajustar el prompt en la clase `LMStudioAgent` 