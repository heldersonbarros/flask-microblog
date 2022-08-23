from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Mantenha-me conectado")
    submit = SubmitField("Entrar")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password1 = PasswordField("Senha", validators=[DataRequired()])
    password2 = PasswordField("Repita a senha", validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField("Registrar")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor escolha um nome de usuário diferente')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor escolha um email diferente')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Enviar")

class ResetPasswordForm(FlaskForm):
    password1 = PasswordField("Senha", validators=[DataRequired()])
    password2 = PasswordField("Repita sua senha", validators=[DataRequired(), EqualTo("password1")])
    submit = SubmitField("Resetar senha")
