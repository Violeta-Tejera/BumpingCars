from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitamos CORS para permitir peticiones desde el frontend

# al entrar en -> http://localhost:7007/ se ejecuta la función welcome
@app.route('/', methods=['GET'])
def welcome():
    # devuelvo HTML en un string pero no os rayéis que no es lo común
    # solo para que se vea bonito el nombre de la app con un nombre muy simple
    
    html_str = "<p>Welcome to the <strong>tl</strong> backend!</p>"
    html_str += "<br><br>"
    html_str += "<br>Try to do <a href=\"http://localhost:7007/hello\">http://localhost:7007/hello<a> ;)</p>"
    
    return html_str


# al entrar en -> http://localhost:7007/hello se ejecuta la función hello
@app.route('/hello', methods=['GET'])
def hello():
    return "Hello, world!"

# Pending meter más endpoints para que concuerde con la demo del frontend de react


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7007, debug=True)