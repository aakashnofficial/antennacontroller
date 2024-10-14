from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock current position
current_position = {
    'azimuth': 0,
    'elevation': 0
}

@app.route('/get_current_position', methods=['GET'])
def get_current_position():
    return jsonify(current_position)

@app.route('/set_position', methods=['POST'])
def set_position():
    data = request.get_json()
    current_position['azimuth'] = data.get('azimuth', current_position['azimuth'])
    current_position['elevation'] = data.get('elevation', current_position['elevation'])
    return jsonify({'status': 'success'})

def runFlaskApp():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    runFlaskApp()
