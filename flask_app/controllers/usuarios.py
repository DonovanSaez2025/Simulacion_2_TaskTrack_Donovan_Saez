# Importaciones
from flask import render_template, redirect, request, session, flash
from flask_app import app, bcrypt
from flask_app.models.usuario import Usuario

# Ruta principal
@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect("/dashboard")
    return render_template("index.html")

# Ruta para registar un usuario con el método post
@app.route("/registrar", methods=["POST"])
def procesar_registro():
    if not Usuario.validar_registro(request.form):
        return redirect("/")

    # Encriptar contraseña
    pw_hash = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

    data = {"nombre": request.form["nombre"],
        "apellido": request.form["apellido"],
        "email": request.form["email"],
        "password_hash": pw_hash}
    user_id = Usuario.registrar(data)

    session["usuario_id"] = user_id
    session["usuario_nombre"] = data["nombre"]
    return redirect("/dashboard")

# Ruta para iniciar sesión
@app.route("/login", methods=["POST"])
def procesar_login():
    usuario = Usuario.obtener_por_email(request.form["email"])
    if not usuario:
        flash("El email no está registrado.", "login")
        return redirect("/")

    if not bcrypt.check_password_hash(usuario.password_hash, request.form["password"]):
        flash("La contraseña es incorrecta.", "login")
        return redirect("/")

    session["usuario_id"] = usuario.id_user
    session["usuario_nombre"] = usuario.nombre
    return redirect("/dashboard")

# Ruta para cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")