# Importaciones
from datetime import datetime
from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL

# Clase tarea
class Tarea:
    # Método constructor
    def __init__(self, data):
        self.id_tarea = data['id_tarea']
        self.titulo = data['titulo']
        self.fecha_limite = data['fecha_limite']
        self.desc_tarea = data['desc_tarea']
        self.id_categoria = data['id_categoria']
        self.id_prioridad = data['id_prioridad']
        self.id_estado = data['id_estado']
        self.id_user = data['id_user']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        # Atributos obtenidos por el método join
        self.nombre_categoria = data.get('nombre_categoria')
        self.nombre_prioridad = data.get('nombre_prioridad')
        self.nombre_estado = data.get('nombre_estado')
        self.creador_nombre = data.get('creador_nombre')

    # Método para guardar la tarea
    @classmethod
    def guardar(cls, data):
        query = """INSERT INTO tareas (titulo, fecha_limite, desc_tarea, id_categoria, id_prioridad, id_estado, id_user)
                VALUES (%(titulo)s, %(fecha_limite)s, %(desc_tarea)s, %(id_categoria)s, %(id_prioridad)s, %(id_estado)s, %(id_user)s);"""
        return connectToMySQL().query_db(query, data)

    # Método para 
    @classmethod
    def obtener_todas_con_relaciones(cls):
        query = """SELECT tareas.*, categorias.nombre_categoria, prioridades.nombre_prioridad, estados.nombre_estado 
                FROM tareas
                JOIN categorias ON tareas.id_categoria = categorias.id_categoria
                JOIN prioridades ON tareas.id_prioridad = prioridades.id_prioridad
                JOIN estados ON tareas.id_estado = estados.id_estado
                ORDER BY tareas.fecha_limite ASC;"""
        resultados = connectToMySQL().query_db(query)
        tareas = []
        if resultados:
            for fila in resultados:
                tareas.append(cls(fila))
        return tareas

    # Método para obtener el id con el creador
    @classmethod
    def obtener_por_id_con_creador(cls, id_tarea):
        query = """
            SELECT tareas.*, categorias.nombre_categoria, prioridades.nombre_prioridad, estados.nombre_estado,
            CONCAT(usuarios.nombre, ' ', usuarios.apellido) AS creador_nombre
            FROM tareas
            JOIN categorias ON tareas.id_categoria = categorias.id_categoria
            JOIN prioridades ON tareas.id_prioridad = prioridades.id_prioridad
            JOIN estados ON tareas.id_estado = estados.id_estado
            JOIN usuarios ON tareas.id_user = usuarios.id_user
            WHERE tareas.id_tarea = %(id_tarea)s;
        """
        data = {'id_tarea': id_tarea}
        resultado = connectToMySQL().query_db(query, data)
        if not resultado or len(resultado) < 1:
            return False
        return cls(resultado[0])

    # Método para validar una tarea
    @staticmethod
    def validar_tarea(formulario):
        es_valido = True
        
        # Validar que no hayan campos esté vacío
        if not formulario.get('titulo') or not formulario.get('id_categoria') or not formulario.get('id_prioridad') or not formulario.get('fecha_limite') or not formulario.get('desc_tarea'):
            flash("Todos los campos son obligatorios.", "tarea")
            return False

        # Validar título
        if len(formulario['titulo']) < 3:
            flash("El título debe tener al menos 3 caracteres.", "tarea")
            es_valido = False

        # Validar la descripción
        if len(formulario['desc_tarea']) < 10:
            flash("La descripción debe tener al menos 10 caracteres.", "tarea")
            es_valido = False

        # Validar fecha límite
        try:
            fecha_ingresada = datetime.strptime(formulario['fecha_limite'], '%Y-%m-%d').date()
            if fecha_ingresada < datetime.now().date():
                flash("La fecha límite no puede ser una fecha pasada.", "tarea")
                es_valido = False
        except ValueError:
            flash("Formato de fecha inválido.", "tarea")
            es_valido = False

        return es_valido