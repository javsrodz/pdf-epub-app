import os
import threading
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from converter import pdf_to_epub 

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_files_delayed(files, delay=300):
    """Borra los archivos después de un tiempo (por defecto 5 min)"""
    def task():
        time.sleep(delay)
        for f in files:
            try:
                if os.path.exists(f):
                    os.remove(f)
                    print(f"Archivo eliminado: {f}")
            except Exception as e:
                print(f"No se pudo borrar {f}: {e}")
    
    threading.Thread(target=task).start()

@app.route('/api/convert', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "message": "Servidor activo"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Falta el archivo'}), 400
    
    file = request.files['file']
    title = request.form.get('title', file.filename.replace('.pdf', ''))
    author = request.form.get('author', 'Anónimo')

    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            output_filename = filename.rsplit('.', 1)[0] + '.epub'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            pdf_to_epub(input_path, output_path, title, author)
            
            delete_files_delayed([input_path, output_path], delay=60) # 60 segundos
            
            return send_file(
                output_path, 
                as_attachment=True, 
                download_name=output_filename,
                mimetype='application/epub+zip'
            )

        except Exception as e:
            return jsonify({'error': f'Error interno: {str(e)}'}), 500
            
    return jsonify({'error': 'Tipo de archivo no permitido'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')