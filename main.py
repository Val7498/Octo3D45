from flask import Flask, request, jsonify
from waitress import serve
import requests
import os

app = Flask("Octo3D45")
app.config['PRINTER_ADDRESS'] = os.getenv("PRINTER_ADDRESS")


@app.route('/api/version', methods=['GET'])
def get_version():
    print("Sending version information")
    # Mocked version information
    return jsonify(api="0.1", text="OctoPrint 1.7.2"), 200

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
        #Code modified from https://github.com/dabosch/Dremel-3D45-Undocumented/blob/master/Control_3D45_video.py
        gcode = {'print_file': (file.filename, file.stream, "multipart/form-data")}
        try:
            print("Sending %s to 3D45 Printer..." % file.filename)
            res = requests.post(app.config["PRINTER_ADDRESS"] + "/print_file_uploads", files=gcode, timeout=20.0)
            if(res.status_code == 200):
                print("Sent gcode to printer")
                if request.form["print"] == "true":
                    print("Sending command to print %s" % file.filename)
                    res2 = requests.post(app.config["PRINTER_ADDRESS"] + '/command', data={'PRINT': file.filename},timeout=20.0)
                    if(res2.status_code == 200):
                        print("print job started")
                        return jsonify(message="Print job started"), 200
                else:
                    return jsonify(message="Successfully uploaded file to 3D45 Printer"), 200
            else:
                return jsonify(error="Failed to upload file to the 3D45 Printer"), 500
        except:
            return jsonify(error="3D45 Printer Timed out."), 500
            


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80)