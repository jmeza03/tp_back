from flask import Flask
from routes.socios import socios_bp
from routes.deportes import deportes_bp
from routes.estados import estados_bp

app = Flask(__name__)
app.register_blueprint(socios_bp)
app.register_blueprint(deportes_bp)
app.register_blueprint(estados_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)