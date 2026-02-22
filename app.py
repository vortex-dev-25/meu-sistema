from flask import Flask, render_template_string, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave_super_secreta_123"

admin_user = "marrom"
admin_password_hash = generate_password_hash("Marrom@2026#Forte")

usuarios = []

login_page = """
<h2>Login</h2>
<form method="POST">
Usuário: <input type="text" name="username"><br>
Senha: <input type="password" name="password"><br>
<input type="submit" value="Entrar">
</form>
"""

admin_page = """
<h2>Painel Admin</h2>
<p>Bem-vindo, {{user}}</p>
<a href="/usuarios">Ver Usuários</a><br>
<a href="/logout">Sair</a>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        if user == admin_user and check_password_hash(admin_password_hash, password):
            session["user"] = user
            return redirect(url_for("admin"))

    return render_template_string(login_page)

@app.route("/admin")
def admin():
    if "user" in session:
        return render_template_string(admin_page, user=session["user"])
    return redirect(url_for("login"))

@app.route("/usuarios")
def listar_usuarios():
    if "user" in session:
        return "<br>".join(usuarios) if usuarios else "Nenhum usuário"
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()