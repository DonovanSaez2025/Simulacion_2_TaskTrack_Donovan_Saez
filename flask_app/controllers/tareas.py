from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.libro import Libro
from flask_app.config.mysqlconnection import connectToMySQL

SCHEMA = 'esquema_certificacion'

def requerir_login():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para acceder.", "login_error")
        return False
    return True

@app.route('/libros')
def dashboard():
    if not requerir_login():
        return redirect('/')
    
    usuario_id = session['usuario_id']
    mis_libros = Libro.get_mis_libros(usuario_id)
    libros_comunidad = Libro.get_libros_comunidad(usuario_id)
    
    return render_template('libros.html', mis_libros=mis_libros, libros_comunidad=libros_comunidad)

@app.route('/libros/nuevo')
def nuevo_libro():
    if not requerir_login():
        return redirect('/')
    
    generos = connectToMySQL(SCHEMA).query_db("SELECT * FROM generos;") or []
    return render_template('agregar_libro.html', generos=generos)

@app.route('/libros/crear', methods=['POST'])
def crear_libro():
    if not requerir_login():
        return redirect('/')

    if not Libro.validar_libro(request.form):
        return redirect('/libros/nuevo')

    data = {
        'titulo_libro': request.form['titulo_libro'],
        'autor': request.form['autor'],
        'descripcion_libro': request.form['descripcion_libro'],
        'fecha_publicacion': request.form['fecha_publicacion'],
        'id_genero': request.form['id_genero'],
        'id_usuario': session['usuario_id']
    }
    
    Libro.save(data)
    return redirect('/libros')

@app.route('/libros/<int:id>')
def ver_libro(id):
    if not requerir_login():
        return redirect('/')

    libro = Libro.get_by_id(id)
    if not libro:
        return redirect('/libros')

    return render_template('ver_libro.html', libro=libro)

@app.route('/libros/editar/<int:id>')
def editar_libro(id):
    if not requerir_login():
        return redirect('/')

    libro = Libro.get_by_id(id)
    if not libro or libro.id_usuario != session['usuario_id']:
        return redirect('/libros')

    generos = connectToMySQL(SCHEMA).query_db("SELECT * FROM generos;") or []
    return render_template('editar_libro.html', libro=libro, generos=generos)

@app.route('/libros/actualizar/<int:id>', methods=['POST'])
def actualizar_libro(id):
    if not requerir_login():
        return redirect('/')

    libro = Libro.get_by_id(id)
    if not libro or libro.id_usuario != session['usuario_id']:
        return redirect('/libros')

    if not Libro.validar_libro(request.form):
        return redirect(f'/libros/editar/{id}')

    data = {
        'id_libro_user': id,
        'titulo_libro': request.form['titulo_libro'],
        'autor': request.form['autor'],
        'descripcion_libro': request.form['descripcion_libro'],
        'fecha_publicacion': request.form['fecha_publicacion'],
        'id_genero': request.form['id_genero'],
        'id_usuario': session['usuario_id']
    }

    Libro.update(data)
    return redirect('/libros')

@app.route('/libros/eliminar/<int:id>')
def eliminar_libro(id):
    if not requerir_login():
        return redirect('/')

    Libro.delete(id, session['usuario_id'])
    return redirect('/libros')

@app.route('/libros/favorito/<int:id>', methods=['POST'])
def agregar_favorito(id):
    if not requerir_login():
        return redirect('/')

    Libro.sumar_favorito(id)
    return redirect(f'/libros/{id}')