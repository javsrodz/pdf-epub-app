import os
import threading
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from converter import pdf_to_epub 

app = Flask(__name__)
CORS(app)

# --- NUEVA PROTECCIÓN: Límite de tamaño (16MB) ---
# Evita que saturen la memoria de tu servidor en Render
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def delete_files_delayed(files, delay=60):
    def task():
        time.sleep(delay)
        for f in files:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass
    threading.Thread(target=task).start()

# Manejador para archivos demasiado grandes
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'El archivo es demasiado grande (máximo 16MB)'}), 413

@app.route('/api/convert', methods=['POST'])
def convert_file():
    input_path = None
    output_path = None
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se recibió ningún archivo'}), 400
        
        file = request.files['file']
        title = request.form.get('title', 'Libro Sin Nombre').strip()
        author = request.form.get('author', 'Anónimo').strip()

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Formato no soportado. Debe ser PDF'}), 400

        # Guardado seguro
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"in_{int(time.time())}_{filename}")
        output_path = input_path.replace('.pdf', '.epub')
        
        file.save(input_path)

        # Intentar conversión
        pdf_to_epub(input_path, output_path, title, author)
        
        # Limpieza programada
        delete_files_delayed([input_path, output_path])

        return send_file(output_path, as_attachment=True, download_name=f"{title}.epub")

    except ValueError as ve:
        # Errores controlados (ej: PDF con contraseña)
        return jsonify({'error': str(ve)}), 422
    except Exception as e:
        # Errores inesperados
        print(f"ERROR: {e}")
        return jsonify({'error': 'Ocurrió un error inesperado al procesar el PDF'}), 500
    finally:
        # Si hubo un error catastrófico, intentamos limpiar el archivo original
        if input_path and os.path.exists(input_path) and not os.path.exists(output_path):
            delete_files_delayed([input_path], delay=10)