'''
# Ruta para manejar el chat (GET para historial, POST para recibir mensajes)
@app.route('/chat', methods=['GET', 'POST', 'PUT'])
def chat():
    if request.method == 'POST':  # Si el usuario envía un mensaje
        try:
            #user_message = request.json.get("message", "").strip()  # Obtiene el mensaje del usuario y lo limpia
            user_message = request.json.get("message").strip().lower()  # Obtiene el mensaje del usuario y lo limpia

            if not user_message:  # Si el mensaje está vacío, responde con un mensaje genérico
                return jsonify({"response": "No entendí tu mensaje. Por favor, escribe algo."})

            # Normalizar el texto (minúsculas y sin signos de puntuación)
            def normalizar_texto(texto):
                texto = texto.lower()  # Convertir a minúsculas
                texto = re.sub(r'[^\w\s]', '', texto)  # Eliminar signos de puntuación
                return texto.strip()

            mensaje_normalizado = normalizar_texto(user_message)
            
            # Busca en la base de datos si la pregunta ya tiene una respuesta guardada
            memory = ChatMemory.query.filter_by(question=user_message).first()

            if memory:  # Si la pregunta ya tiene respuesta
                return jsonify({"response": memory.answer})

            # Si no existe, pregunta si el usuario quiere enseñar la respuesta
            new_entry = ChatMemory(question=mensaje_normalizado, answer="No sé la respuesta aún.")
            db.session.add(new_entry)
            db.session.commit()
            
            return jsonify({
                "response": f"No sé la respuesta a '{user_message}' aún, pero la recordaré para la próxima vez"
            })

        except Exception as e:
            return jsonify({"response": f"Hubo un error procesando tu mensaje: {str(e)}"}), 500

    elif request.method == 'PUT':  # Si el usuario quiere enseñar al chatbot
        data = request.json
        question = data.get("message").strip().lower()
        answer = data.get("answer").strip()
        if not question or not answer:
            return jsonify({"response": "Mensaje y respuesta son requeridos."}), 400

        existing_memory = ChatMemory.query.filter_by(question=question).first()
        
        if existing_memory:
            existing_memory.answer = answer  # Actualiza la respuesta
        else:
            new_entry = ChatMemory(question=question, answer=answer)
            db.session.add(new_entry)
        
        db.session.commit()
        return jsonify({"response": "Respuesta guardada correctamente."})

    elif request.method == 'GET':  # Si se consulta el historial del chat
        try:
            chat_history = ChatMemory.query.all()  # Obtiene todas las conversaciones almacenadas
            history = [{"question": chat.question, "answer": chat.answer} for chat in chat_history]
            return jsonify(history)  # Devuelve el historial en formato JSON
###
        except Exception as e:
            return jsonify({"response": f"Hubo un error al obtener el historial: {str(e)}"}), 500

    # Si no es ni POST ni PUT ni GET, simplemente renderiza el chat
    return render_template('chat.html')
'''