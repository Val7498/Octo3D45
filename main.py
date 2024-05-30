from flask import Flask, request, jsonify
from waitress import serve
import requests
import os

app = Flask("Octo3D45")
app.config['PRINTER_ADDRESS'] = os.getenv("PRINTER_ADDRESS")


@app.route('/api/version', methods=['GET'])
def get_version():
    # Mocked version information
    return jsonify(api="0.1", text="OctoPrint 1.7.2")

@app.route('/api/files/local', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print('No file part in the request')
        return jsonify(error="No file part in the request"), 400
    
    file = request.files['file']
    
    if file.filename == '':
        print('No selected file')
        return jsonify(error="No selected file."), 400
    
    if file:
        #Code taken from https://github.com/dabosch/Dremel-3D45-Undocumented/blob/master/Control_3D45_video.py
        print("Sending to 3D45 Printer...")
        gcode = {'file': (file.filename, file.stream, file.content_type)}
        try:
            res = requests.post(app.config["PRINTER_ADDRESS"] + "/print_file_uploads", files=gcode, timeout=20.0)
            if(eval(res.text)["error_code"] == 200):
                if request.form["print"] == "true":
                    data = {'PRINT':file.filename}
                    res2 = requests.post(app.config["PRINTER_ADDRESS"] + '/command', data=data,timeout=20.0)
                    if(eval(res2.text)["error_code"] == 200):
                        return jsonify(message="Printing..."), 200
                else:
                    return jsonify(message="Successfully uploaded file to 3D45 Printer")
            else:
                return jsonify(error="Failed to upload file to the 3D45 Printer"), 500
        except:
            return jsonify(error="3D45 Printer Timed out."), 500
            


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80)