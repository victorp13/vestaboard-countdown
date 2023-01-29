from flask import Flask
import parsecsv
app = Flask(__name__)

@app.route('/updateboard')
def index():
    parsecsv.update_vestaboard()
    return "Vestaboard updated!"

app.run(host='0.0.0.0', port=5000, debug=True)
