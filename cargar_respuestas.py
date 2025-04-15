import requests
import json
import pandas as pd

# URL del servidor Flask
url = "http://localhost:5000/chat"

# Cargar datos desde JSON con manejo de errores
def cargar_json():
    try:
        with open("conocimientos.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            print(f"📌 Cargados {len(data)} registros desde JSON.")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Error al cargar JSON: {e}")
        return []  # Retorna una lista vacía si hay error

# Cargar datos desde CSV con manejo de errores
def cargar_csv():
    try:
        df = pd.read_csv("conocimientos.csv", delimiter=",", usecols=[0,1], names=["message", "answer"], skiprows=1)
        data = df.to_dict(orient="records")
        print(f"📌 Cargados {len(data)} registros desde CSV.")
        return data
    except (FileNotFoundError, pd.errors.ParserError) as e:
        print(f"⚠️ Error al cargar CSV: {e}")
        return []  # Retorna una lista vacía si hay error

# Unir datos de JSON y CSV
data = cargar_json() + cargar_csv()
if not data:
    print("❌ No hay datos para enviar.")
else:
    print(f"✅ Enviando {len(data)} registros al chatbot...\n")

    # Enviar cada mensaje al chatbot para que lo aprenda
    for entry in data:
        response = requests.put(url, json=entry)
        print(f"📤 Enviado: {entry['message']} -> {entry['answer']}")
        
        # Verifica si el servidor responde correctamente
        try:
            print(f"✅ Respuesta del servidor: {response.json()}\n")
        except json.JSONDecodeError:
            print(f"❌ Error en la respuesta del servidor: {response.text}\n")
