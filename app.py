import re
import difflib
from flask import Flask, url_for, request, jsonify, json, render_template  # Importamos Flask y funciones necesarias
from flask_sqlalchemy import SQLAlchemy  # Manejamos la base de datos con SQLAlchemy
from flask_cors import CORS  # Permite peticiones desde el frontend

# Inicialización de la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir peticiones desde el navegador

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'  # Base de datos local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactiva el rastreo de modificaciones

# Inicialización de la base de datos
db = SQLAlchemy(app)

# Modelo de base de datos para almacenar preguntas y respuestas
class ChatMemory(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID autoincremental
    question = db.Column(db.String(255), unique=True, nullable=False)  # Pregunta única
    answer = db.Column(db.String(255), nullable=False)  # Respuesta asociada

# Crea las tablas si no existen dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

# Normalizar texto: minúsculas, sin tildes, sin signos de puntuación
def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = re.sub(r'[^\w\s]', '', texto)  # Eliminar signos de puntuación
    texto = texto.replace('á', 'a').replace('é', 'e').replace('í', 'i')\
                 .replace('ó', 'o').replace('ú', 'u').replace('ü', 'u')
    return texto

# Buscar pregunta similar en la base de datos usando difflib con mejor precisión
def encontrar_pregunta_similar(pregunta_usuario):
    todas_preguntas = [normalizar_texto(chat.question) for chat in ChatMemory.query.all()]
    
    print(todas_preguntas)
    
    if not todas_preguntas:
        return None
    
    pregunta_normalizada = normalizar_texto(pregunta_usuario)
    preguntas_normalizadas = [normalizar_texto(pregunta) for pregunta in todas_preguntas]
    
    coincidencia = difflib.get_close_matches(pregunta_normalizada, todas_preguntas, n=1, cutoff=0.6)  # Más flexible
    return coincidencia[0] if coincidencia else None


@app.route('/chat', methods=['GET', 'POST', 'PUT'])
def chat():
    if request.method == 'POST':
        user_message = request.json.get("message", "").strip()
        
        if not user_message:
            return jsonify({"response": "No entendí tu mensaje."})
        
        # Normalizar el mensaje del usuario
        mensaje_normalizado = normalizar_texto(user_message)

        # Buscar pregunta similar en la base de datos
        pregunta_similar = encontrar_pregunta_similar(mensaje_normalizado)

        if pregunta_similar:
            respuesta = ChatMemory.query.filter_by(question=pregunta_similar).first().answer
            return jsonify({"response": respuesta})

        # Si no existe, la guarda con una respuesta predeterminada
        nueva_entrada = ChatMemory(question=mensaje_normalizado, answer="No sé la respuesta aún.")
        db.session.add(nueva_entrada)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"response": "Hubo un error al guardar la información."})

        return jsonify({"response": f"No sé la respuesta a '{user_message}' aún, pero la recordaré para la próxima vez."})

    elif request.method == 'PUT':
        # Lógica para manejar solicitudes PUT
        data = request.get_json()
        question = data.get('message')
        answer = data.get('answer')
        if question and answer:
            # Verificar si la pregunta ya existe en la base de datos
            existing_entry = ChatMemory.query.filter_by(question=question).first()
            if existing_entry:
                # Actualizar la respuesta si la pregunta ya existe
                existing_entry.answer = answer
                db.session.commit()
                return jsonify({"response": "Conocimiento actualizado exitosamente."}), 200
            else:
                # Agregar una nueva entrada si la pregunta no existe
                new_entry = ChatMemory(question=question, answer=answer)
                db.session.add(new_entry)
                db.session.commit()
                return jsonify({"response": "Nuevo conocimiento agregado exitosamente."}), 201
        else:
            return jsonify({"error": "Datos inválidos. Se requieren 'message' y 'answer'."}), 400

    
@app.route('/')
def index():
    return render_template('chat.html')
        
# Ejecuta la aplicación Flask en modo depuración
if __name__ == '__main__':
    app.run(debug=True)
    """_summary_
    """