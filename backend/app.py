import os
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

@app.route('/api/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Falta el archivo'}), 400
    
    file = request.files['file']

    title = request.form.get('title', file.filename)
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
            
            print(f"Convirtiendo {filename}...")
            pdf_to_epub(input_path, output_path, title, author)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)

        except Exception as e:
            print(f"Error en conversión: {str(e)}")
            return jsonify({'error': f'Error interno: {str(e)}'}), 500
            
    return jsonify({'error': 'Tipo de archivo no permitido (solo PDF)'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')