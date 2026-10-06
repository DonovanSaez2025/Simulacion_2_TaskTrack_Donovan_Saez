# Importaciones
import re
from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL

# Filtro de carácteres para el email
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Clase de usuario
class Usuario:
    # Método constructor
    def __init__(self, data):
        self.id_user = data['id_user']
        self.nombre = data['nombre']
        self.apellido = data['apellido']
        self.email = data['email']
        self.password_hash = data['password_hash']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    # Método para registrar usuarios
    @classmethod
    def registrar(cls, data):
        query = """INSERT INTO usuarios (nombre, apellido, email, password_hash)
                VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password_hash)s);"""
        return connectToMySQL().query_db(query, data)

    # Método para obtener un email
    @classmethod
    def obtener_por_email(cls, email):
        query = """SELECT * FROM usuarios
                WHERE email = %(email)s;"""
        data = {'email': email}
        resultado = connectToMySQL().query_db(query, data)
        if not resultado or len(resultado) < 1:
            return False
        return cls(resultado[0])

    # Método para obtener un id
    @classmethod
    def obtener_por_id(cls, user_id):
        query = """SELECT * FROM usuarios
                WHERE id_user = %(id_user)s;"""
        data = {'id_user': user_id}
        resultado = connectToMySQL().query_db(query, data)
        if not resultado or len(resultado) < 1:
            return False
        return cls(resultado[0])

    # Método para validar un registro
    @staticmethod
    def validar_registro(formulario):
        es_valido = True
        
        # Validar nombre
        if len(formulario['nombre']) < 2:
            flash("El nombre debe tener al menos 2 caracteres.", "registro")
            es_valido = False
            
        # Validar apellido
        if len(formulario['apellido']) < 2:
            flash("El apellido debe tener al menos 2 caracteres.", "registro")
            es_valido = False
        
        # Validar email
        if not EMAIL_REGEX.match(formulario['email']):
            flash("Formato de correo electrónico inválido.", "registro")
            es_valido = False
        else:
            if Usuario.obtener_por_email(formulario['email']):
                flash("El correo electrónico ya está registrado.", "registro")
                es_valido = False
                
        # Validar contraseña
        if len(formulario['password']) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "registro")
            es_valido = False
        if formulario['password'] != formulario['confirm_password']:
            flash("Las contraseñas no coinciden.", "registro")
            es_valido = False
        return es_valido