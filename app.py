from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key_2026")

DB = "database.db"

def conectar():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def criar_banco():
    conn = conectar()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        tipo TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

criar_banco()

def criar_admin():
    conn = conectar()
    admin = conn.execute("SELECT * FROM usuarios WHERE username = ?", ("marrom",)).fetchone()
    if not admin:
        senha_hash = generate_password_hash("Marrom@2026#UltraForte")
        conn.execute(
            "INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)",
            ("marrom", senha_hash, "admin")
        )
        conn.commit()
    conn.close()

criar_admin()

# ROTAS

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        conn = conectar()
        usuario = conn.execute("SELECT * FROM usuarios WHERE username = ?", (user,)).fetchone()
        conn.close()

        if usuario and check_password_hash(usuario["password"], password):
            session["user"] = usuario["username"]
            session["tipo"] = usuario["tipo"]
            return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = conectar()
            conn.execute("INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)",
                         (user, password, "user"))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            return "Usuário já existe"

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"], tipo=session["tipo"])

@app.route("/admin")
def admin():
    if "user" not in session or session["tipo"] != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/api/users")
def api_users():
    conn = conectar()
    usuarios = conn.execute("SELECT username, tipo FROM usuarios").fetchall()
    conn.close()

    return jsonify([dict(u) for u in usuarios])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()