from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.usuario import Usuario
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect('/libros')
    return render_template('index.html')

@app.route('/registro', methods=['POST'])
def registro():
    if not Usuario.validar_registro(request.form):
        return redirect('/')

    pw_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    
    data = {
        "nombre": request.form['nombre'],
        "apellido": request.form['apellido'],
        "email": request.form['email'],
        "password_hash": pw_hash
    }
    
    id_usuario = Usuario.save(data)
    session['usuario_id'] = id_usuario
    session['usuario_nombre'] = request.form['nombre']
    
    return redirect('/libros')

@app.route('/login', methods=['POST'])
def login():
    usuario = Usuario.get_by_email(request.form['email'])
    
    if not usuario or not bcrypt.check_password_hash(usuario.password_hash, request.form['password']):
        flash("Credenciales inválidas.", "login_error")
        return redirect('/')

    session['usuario_id'] = usuario.id_usuario
    session['usuario_nombre'] = usuario.nombre
    return redirect('/libros')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')