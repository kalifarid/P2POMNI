import random
import string
from flask import Flask, render_template, request, send_file, jsonify
import io

app = Flask(__name__)

# Maksimum fayl ölçüsü limiti (32 MB)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

# Faylları RAM-da müvəqqəti saxlamaq üçün lüğət (In-Memory Buffer)
ACTIVE_ROOMS = {}

def generate_room_code():
    """Təkrarlanmayan 4 rəqəmli unikal kod generasiya edir."""
    while True:
        code = "".join(random.choices(string.digits, k=4))
        if code not in ACTIVE_ROOMS:
            return code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl seçilməyib!"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Faylın adı boşdur!"}), 400

    # Fayl məlumatlarını RAM-a (BytesIO) oxuyuruq (Diskə yazılmır!)
    file_stream = io.BytesIO(file.read())
    room_code = generate_room_code()

    ACTIVE_ROOMS[room_code] = {
        "file_name": file.filename,
        "file_data": file_stream,
        "mime_type": file.mimetype or "application/octet-stream"
    }

    return jsonify({"code": room_code, "file_name": file.filename})

@app.route('/download', methods=['POST'])
def download():
    code = request.form.get('code') or request.json.get('code')
    if not code:
        return jsonify({"error": "Zəhmət olmasa 4 rəqəmli kodu daxil edin!"}), 400
    
    code = code.strip()
    if code not in ACTIVE_ROOMS:
        return jsonify({"error": "Belə bir otaq kodu tapılmadı və ya vaxtı keçib!"}), 404

    file_info = ACTIVE_ROOMS[code]
    file_data = file_info["file_data"]
    file_data.seek(0) 

    return send_file(
        io.BytesIO(file_data.read()),
        mimetype=file_info["mime_type"],
        as_attachment=True,
        download_name=file_info["file_name"]
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)

