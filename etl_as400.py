import pandas as pd
import jaydebeapi
import requests
import time

# ==========================================
# CONFIGURACIÓN GLOBAL
# ==========================================
USUARIO = 'ANDRESS17'
PASSWORD = '97061705426'
JAR_PATH = "jt400-11.0.jar"
JDBC_URL = "jdbc:as400://pub400.com"
## API_URL = "http://127.0.0.1:8080/api/cargar"
API_URL = "https://etlpython.onrender.com/api/cargar"

def extraer_datos():
    """Conecta al AS/400 y extrae los datos crudos."""
    print("\n" + "="*50)
    print("FASE 1: EXTRACT (IBM AS/400) ")
    print("="*50)
    print("[*] Estableciendo conexión JDBC con PUB400.com...")
    
    try:
        conn = jaydebeapi.connect(
            "com.ibm.as400.access.AS400JDBCDriver",
            JDBC_URL,
            [USUARIO, PASSWORD],
            JAR_PATH
        )
        query = "SELECT * FROM ANDRESS171.TRANSACCIONES"
        df_bruto = pd.read_sql(query, conn)
        conn.close()
        
        print(f"[+] Conexión exitosa. Se extrajeron {len(df_bruto)} registros.\n")
        print("Vista previa de datos crudos:")
        print(df_bruto.head())
        return df_bruto
        
    except Exception as e:
        print(f"[-] Error crítico en la extracción: {e}")
        exit()

def transformar_datos(df):
    """Limpia los nulos, filtra estados y consolida sumas."""
    print("\n" + "="*50)
    print("FASE 2: TRANSFORM (PANDAS) ")
    print("="*50)
    print("[*] Limpiando valores nulos y filtrando transacciones...")
    time.sleep(1) # Pequeña pausa para efecto visual en consola
    
    # 1. Eliminar filas con montos nulos (Basura/Errores)
    df_limpio = df.dropna(subset=['MONTO'])
    
    # 2. Mantener únicamente transacciones consolidadas (APROBADO)
    df_limpio = df_limpio[df_limpio['ESTADO'] == 'APROBADO']
    
    # 3. Agrupar por sucursal y sumar los ingresos
    df_agrupado = df_limpio.groupby('SUCURSAL')['MONTO'].sum().reset_index()
    
    print(f"[+] Transformación completada. Quedan {len(df_agrupado)} sedes consolidadas.\n")
    print("Vista previa de datos transformados:")
    print(df_agrupado)
    return df_agrupado

def cargar_datos(df):
    """Convierte los datos a JSON y los envía vía API REST."""
    print("\n" + "="*50)
    print("FASE 3: LOAD (NUBE / FLASK) ")
    print("="*50)
    print("[*] Empaquetando JSON y enviando payload a la API...")
    
    payload = df.to_dict(orient='records')
    
    try:
        respuesta = requests.post(API_URL, json=payload)
        print(f"[+] Código de estado : HTTP {respuesta.status_code}")
        print(f"[+] Respuesta API    : {respuesta.json().get('mensaje', respuesta.text)}")
        print("="*50 + "\n")
    except requests.exceptions.ConnectionError:
        print("[-] FALLO DE CONEXIÓN: El servidor Flask de destino no está en línea.")
        print("    -> Asegúrate de ejecutar 'python app.py' en otra consola primero.\n")

# ==========================================
# EJECUCIÓN PRINCIPAL (MAIN)
# ==========================================
if __name__ == "__main__":
    datos_crudos = extraer_datos()
    datos_limpios = transformar_datos(datos_crudos)
    cargar_datos(datos_limpios)