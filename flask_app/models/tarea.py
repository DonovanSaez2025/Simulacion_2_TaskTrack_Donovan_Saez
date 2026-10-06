from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from datetime import datetime

SCHEMA = 'esquema_certificacion'

class Libro:
    def __init__(self, data):
        self.id_libro_user = data.get('id_libro_user')
        self.id_libro_comunidad = data.get('id_libro_comunidad')
        self.titulo_libro = data.get('titulo_libro')
        self.autor = data.get('autor')
        # Maneja tanto 'descripcion_libro' como 'descripcion' según la tabla de procedencia
        self.descripcion_libro = data.get('descripcion_libro') or data.get('descripcion')
        self.fecha_publicacion = data.get('fecha_publicacion')
        self.favoritos = data.get('favoritos', 0)
        self.id_usuario = data.get('id_usuario')
        self.id_genero = data.get('id_genero')
        
        # Atributos poblados con JOINs
        self.nombre_genero = data.get('nombre_genero', '')
        self.publicado_por = data.get('publicado_por', '')

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO libros_de_usuario (titulo_libro, autor, descripcion_libro, fecha_publicacion, favoritos, id_usuario, id_genero)
        VALUES (%(titulo_libro)s, %(autor)s, %(descripcion_libro)s, %(fecha_publicacion)s, 0, %(id_usuario)s, %(id_genero)s);
        """
        return connectToMySQL(SCHEMA).query_db(query, data)

    @classmethod
    def get_mis_libros(cls, id_usuario):
        query = """
        SELECT l.*, g.nombre_genero
        FROM libros_de_usuario l
        LEFT JOIN generos g ON l.id_genero = g.id_genero
        WHERE l.id_usuario = %(id_usuario)s;
        """
        results = connectToMySQL(SCHEMA).query_db(query, {'id_usuario': id_usuario})
        return [cls(row) for row in results] if results else []

    @classmethod
    def get_libros_comunidad(cls, id_usuario):
        query = """
        SELECT lc.*, g.nombre_genero, CONCAT(u.nombre, ' ', u.apellido) AS publicado_por
        FROM libros_comunidad lc
        JOIN usuarios u ON lc.id_usuario = u.id_usuario
        LEFT JOIN generos g ON lc.id_genero = g.id_genero
        WHERE lc.id_usuario != %(id_usuario)s;
        """
        results = connectToMySQL(SCHEMA).query_db(query, {'id_usuario': id_usuario})
        return [cls(row) for row in results] if results else []

    @classmethod
    def get_by_id(cls, id_libro_user):
        query = """
        SELECT l.*, g.nombre_genero, CONCAT(u.nombre, ' ', u.apellido) AS publicado_por
        FROM libros_de_usuario l
        JOIN usuarios u ON l.id_usuario = u.id_usuario
        LEFT JOIN generos g ON l.id_genero = g.id_genero
        WHERE l.id_libro_user = %(id_libro_user)s;
        """
        results = connectToMySQL(SCHEMA).query_db(query, {'id_libro_user': id_libro_user})
        if not results:
            return None
        return cls(results[0])

    @classmethod
    def update(cls, data):
        query = """
        UPDATE libros_de_usuario 
        SET titulo_libro = %(titulo_libro)s, autor = %(autor)s, descripcion_libro = %(descripcion_libro)s, 
            fecha_publicacion = %(fecha_publicacion)s, id_genero = %(id_genero)s
        WHERE id_libro_user = %(id_libro_user)s AND id_usuario = %(id_usuario)s;
        """
        return connectToMySQL(SCHEMA).query_db(query, data)

    @classmethod
    def delete(cls, id_libro_user, id_usuario):
        query = "DELETE FROM libros_de_usuario WHERE id_libro_user = %(id_libro_user)s AND id_usuario = %(id_usuario)s;"
        return connectToMySQL(SCHEMA).query_db(query, {'id_libro_user': id_libro_user, 'id_usuario': id_usuario})

    @classmethod
    def sumar_favorito(cls, id_libro_user):
        query = "UPDATE libros_de_usuario SET favoritos = favoritos + 1 WHERE id_libro_user = %(id_libro_user)s;"
        return connectToMySQL(SCHEMA).query_db(query, {'id_libro_user': id_libro_user})

    @staticmethod
    def validar_libro(data):
        is_valid = True
        
        if len(data.get('titulo_libro', '').strip()) < 2:
            flash("El título debe tener al menos 2 caracteres.", "libro_titulo")
            is_valid = False

        if len(data.get('autor', '').strip()) < 2:
            flash("El autor debe tener al menos 2 caracteres.", "libro_autor")
            is_valid = False

        if not data.get('id_genero'):
            flash("Debe seleccionar un género.", "libro_genero")
            is_valid = False

        if not data.get('fecha_publicacion'):
            flash("Debe ingresar la fecha de publicación.", "libro_fecha")
            is_valid = False
        else:
            fecha_pub = datetime.strptime(data['fecha_publicacion'], '%Y-%m-%d').date()
            if fecha_pub > datetime.now().date():
                flash("La fecha de publicación no puede ser en el futuro.", "libro_fecha")
                is_valid = False

        if len(data.get('descripcion_libro', '').strip()) < 10:
            flash("La descripción debe tener al menos 10 caracteres.", "libro_descripcion")
            is_valid = False

        return is_valid