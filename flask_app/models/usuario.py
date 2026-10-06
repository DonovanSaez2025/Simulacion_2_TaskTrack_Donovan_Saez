from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
SCHEMA = 'esquema_certificacion'

class Usuario:
    def __init__(self, data):
        self.id_usuario = data.get('id_usuario')
        self.nombre = data.get('nombre')
        self.apellido = data.get('apellido')
        self.email = data.get('email')
        self.password_hash = data.get('password_hash')
        self.create_at = data.get('create_at')
        self.updated_at = data.get('updated_at')

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO usuarios (nombre, apellido, email, password_hash) 
        VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password_hash)s);
        """
        return connectToMySQL(SCHEMA).query_db(query, data)

    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        results = connectToMySQL(SCHEMA).query_db(query, {'email': email})
        if not results:
            return False
        return cls(results[0])

    @classmethod
    def get_by_id(cls, id_usuario):
        query = "SELECT * FROM usuarios WHERE id_usuario = %(id_usuario)s;"
        results = connectToMySQL(SCHEMA).query_db(query, {'id_usuario': id_usuario})
        if not results:
            return None
        return cls(results[0])

    @staticmethod
    def validar_registro(usuario):
        is_valid = True
        
        if len(usuario.get('nombre', '').strip()) < 2:
            flash("El nombre debe tener al menos 2 caracteres.", "registro_nombre")
            is_valid = False
            
        if len(usuario.get('apellido', '').strip()) < 2:
            flash("El apellido debe tener al menos 2 caracteres.", "registro_apellido")
            is_valid = False

        if not EMAIL_REGEX.match(usuario.get('email', '')):
            flash("Formato de e-mail inválido.", "registro_email")
            is_valid = False
        elif Usuario.get_by_email(usuario.get('email', '')):
            flash("El e-mail ya se encuentra registrado.", "registro_email")
            is_valid = False

        if len(usuario.get('password', '')) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "registro_password")
            is_valid = False

        if usuario.get('password') != usuario.get('confirm_password'):
            flash("Las contraseñas no coinciden.", "registro_confirm")
            is_valid = False

        return is_valid