from . import auth
from app import db
from .forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from flask_login import current_user, logout_user, login_user
from flask import render_template, redirect, url_for, flash

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("core.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Senha ou nome do usuário inválido!", "error")
            return redirect(url_for("auth.login"))

        login_user(user, form.remember_me.data)

        return redirect(url_for('core.index'))

    return render_template("auth/login.html", title="Login", loginForm=form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("core.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email= form.email.data)
        user.set_password(form.password1.data)
        flash("Registrado com sucesso!", "success")

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("core.index"))

    return render_template("auth/register.html", title = "Registrar", form= form)

@auth.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("core.index"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email= form.email.data).first()
        if user:
            #Enviar email
            flash("Verifique seu email para mais informações.", "success")
            return redirect(url_for("auth.login"))
    
    return render_template("auth/reset_password_request.html", title= "Recuperar conta", form=form)

@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("core.index"))

    form = ResetPasswordForm()
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("core.index"))

    if form.validate_on_submit():
        user.set_password(form.password1.data)
        db.session.commit()
        flash("Sua senha foi alterada com sucesso!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", title= "Resete sua senha", form = form)

@auth.route("/get_token/<id>")
def get_test_token(id):
    user = User.query.get(id)
    return user.get_reset_password_token()
