import threading
import requests
import time
import os
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone

app = Flask(__name__)

# Memoria en tiempo de ejecución para guardar los datos
datos_etl = []
ultima_actualizacion = ""

def keep_alive():
    """Realiza una petición a la app misma cada 3 minutos para evitar que Render la detenga."""
    # Esperar un poco a que el servidor Flask inicie antes de la primera petición
    time.sleep(10)
    while True:
        try:
            # Usar la URL pública si está configurada (por ejemplo, en Render se puede inyectar vía variable de entorno RENDER_EXTERNAL_URL)
            url = os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:8080')
            response = requests.get(f"{url}/live", timeout=5)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Keep-Alive Ping ejecutado. Status: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Keep-Alive Error: {e}")
        # 180 segundos = 3 minutos
        time.sleep(180)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', datos=datos_etl, ultima_actualizacion=ultima_actualizacion)

@app.route('/live', methods=['GET'])
def live_checker():
    return jsonify({"status": "alive", "timestamp": datetime.now().isoformat()}), 200

@app.route('/api/cargar', methods=['POST'])
def cargar_datos():
    global datos_etl, ultima_actualizacion
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400
    
    # Actualizar la memoria con los nuevos datos
    datos_etl = datos
    ultima_actualizacion = datetime.now(timezone.utc).isoformat()
    
    # Aquí se imprime en la consola del servidor lo que llegó del ETL
    print(f"Éxito: Se recibieron {len(datos)} registros de sucursales consolidadas.")
    
    # Se responde al script ETL que todo salió bien (HTTP 200)
    return jsonify({
        "mensaje": "Datos integrados correctamente en la aplicación nativa y actualizados en el Dashboard", 
        "registros_procesados": len(datos)
    }), 200

# Iniciar el hilo de fondo para mantener vivo el servicio, independientemente de si se usa gunicorn
t = threading.Thread(target=keep_alive)
t.daemon = True
t.start()

if __name__ == '__main__':
    # Puerto 8080 estándar para despliegues web
    app.run(host='0.0.0.0', port=8080)