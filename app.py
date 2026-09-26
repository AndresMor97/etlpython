from flask import Flask, request, jsonify

app = Flask(__name__)

# Este es el endpoint que recibirá los datos del AS/400
@app.route('/api/cargar', methods=['POST'])
def cargar_datos():
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400
    
    # Aquí se imprime en la consola del servidor lo que llegó del ETL
    print(f"Éxito: Se recibieron {len(datos)} registros de sucursales consolidadas.")
    print(datos)
    
    # Se responde al script ETL que todo salió bien (HTTP 200)
    return jsonify({
        "mensaje": "Datos integrados correctamente en la aplicación nativa", 
        "registros_procesados": len(datos)
    }), 200

if __name__ == '__main__':
    # Puerto 8080 estándar para despliegues web
    app.run(host='0.0.0.0', port=8080)