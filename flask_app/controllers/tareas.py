# Importaciones
from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.tarea import Tarea
from flask_app.config.mysqlconnection import connectToMySQL

# Ruta para ver todos los libros en el dashboard
@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect("/")
    todas_tareas = Tarea.obtener_todas_con_relaciones()
    resumen = {"totales": len(todas_tareas),
        "pendientes": len([t for t in todas_tareas if t.nombre_estado == "Pendiente"]),
        "en_progreso": len([t for t in todas_tareas if t.nombre_estado == "En progreso"]),
        "completadas": len([t for t in todas_tareas if t.nombre_estado == "Completada"])}
    return render_template("dashboard.html", tareas=todas_tareas, resumen=resumen)

# Ruta para ver los detalles de una tarea específica
@app.route("/tareas/<int:id_tarea>")
def ver_detalle_tarea(id_tarea):
    if "usuario_id" not in session:
        return redirect("/") 
    tarea = Tarea.obtener_por_id_con_creador(id_tarea)
    if not tarea:
        flash("La tarea solicitada no existe.", "dashboard")
        return redirect("/dashboard")
    query_comments = """SELECT comentarios.*, usuarios.nombre, usuarios.apellido 
        FROM comentarios 
        JOIN usuarios ON comentarios.id_user = usuarios.id_user 
        WHERE id_tarea = %(id_tarea)s ORDER BY comentarios.created_at DESC;"""
    comentarios = connectToMySQL().query_db(query_comments, {"id_tarea": id_tarea})
    return render_template("tarea_ver.html", tarea=tarea, comentarios=comentarios)

# Ruta para el formulario de creación de las careas
@app.route("/tareas/nueva")
def nueva_tarea():
    if "usuario_id" not in session:
        return redirect("/")
    categorias = connectToMySQL().query_db("SELECT * FROM categorias;")
    prioridades = connectToMySQL().query_db("SELECT * FROM prioridades;")
    return render_template("crear_tarea.html", categorias=categorias, prioridades=prioridades)

# Ruta para crear una tarea
@app.route("/tareas/crear", methods=["POST"])
def crear_tarea():
    if "usuario_id" not in session:
        return redirect("/")
    if not Tarea.validar_tarea(request.form):
        return redirect("/tareas/nueva")  
    data = {"titulo": request.form["titulo"],
        "fecha_limite": request.form["fecha_limite"],
        "desc_tarea": request.form["desc_tarea"],
        "id_categoria": request.form["id_categoria"],
        "id_prioridad": request.form["id_prioridad"],
        "id_estado": 1,
        "id_user": session["usuario_id"]}
    Tarea.guardar(data)
    return redirect("/dashboard")

# Ruta para el formulario de edición de tareas
@app.route("/tareas/editar/<int:id_tarea>")
def editar_tarea(id_tarea):
    if "usuario_id" not in session:
        return redirect("/")
    tarea = Tarea.obtener_por_id_con_creador(id_tarea)
    if not tarea or tarea.id_user != session["usuario_id"]:
        flash("Acceso denegado. No tienes permisos para modificar esta tarea.", "dashboard")
        return redirect("/dashboard")
    categorias = connectToMySQL().query_db("SELECT * FROM categorias;")
    prioridades = connectToMySQL().query_db("SELECT * FROM prioridades;")
    return render_template("editar_tarea.html", tarea=tarea, categorias=categorias, prioridades=prioridades)

# Ruta para actualizar la tarea
@app.route("/tareas/actualizar/<int:id_tarea>", methods=["POST"])
def procesar_actualizacion(id_tarea):
    if "usuario_id" not in session:
        return redirect("/")
    tarea = Tarea.obtener_por_id_con_creador(id_tarea)
    if not tarea or tarea.id_user != session["usuario_id"]:
        return redirect("/dashboard")
    if not Tarea.validar_tarea(request.form):
        return redirect(f"/tareas/editar/{id_tarea}")     
    data = {"id_tarea": id_tarea,
        "titulo": request.form["titulo"],
        "fecha_limite": request.form["fecha_limite"],
        "desc_tarea": request.form["desc_tarea"],
        "id_categoria": request.form["id_categoria"],
        "id_prioridad": request.form["id_prioridad"]}
    Tarea.actualizar(data)
    return redirect("/dashboard")

# Ruta para marcar una tarea como completada
@app.route("/tareas/completar/<int:id_tarea>")
def marcar_completada(id_tarea):
    if "usuario_id" not in session:
        return redirect("/")
    tarea = Tarea.obtener_por_id_con_creador(id_tarea)
    if not tarea or tarea.id_user != session["usuario_id"]:
        return redirect("/dashboard")
    query = "UPDATE tareas SET id_estado = 3 WHERE id_tarea = %(id_tarea)s;"
    connectToMySQL().query_db(query, {"id_tarea": id_tarea})
    return redirect("/dashboard")

# Ruta para eliminar una tarea
@app.route("/tareas/eliminar/<int:id_tarea>")
def eliminar_tarea(id_tarea):
    if "usuario_id" not in session:
        return redirect("/")
    tarea = Tarea.obtener_por_id_con_creador(id_tarea)
    if not tarea or tarea.id_user != session["usuario_id"]:
        flash("No puedes eliminar tareas pertenecientes a otros perfiles.", "dashboard")
        return redirect("/dashboard")
    
    # Eliminar los comentarios de la tarea borrada
    connectToMySQL().query_db("DELETE FROM comentarios WHERE id_tarea = %(id_tarea)s;", {"id_tarea": id_tarea})
    Tarea.eliminar(id_tarea)
    return redirect("/dashboard")