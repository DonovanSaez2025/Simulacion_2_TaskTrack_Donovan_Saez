# Importaciones
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Cargar dotenv
load_dotenv()

# Guardar la llave secreta
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
bcrypt = Bcrypt(app)
