from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
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

class PostForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired()])
    image = FileField("Meme", validators=[DataRequired()])
    tag = StringField("Tags")
    submit = SubmitField("Postar")

class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    avatar = FileField("Avatar")
    submit = SubmitField("Salvar")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if self.original_username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user != None:
                raise ValidationError('Por favor escolhe um nome de usuário diferente')

class CommentForm(FlaskForm):
    text = TextAreaField("Comentário", validators=[DataRequired()])
    submit = SubmitField("Enviar comentário")

class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Enviar")

class ResetPasswordForm(FlaskForm):
    password1 = PasswordField("Senha", validators=[DataRequired()])
    password2 = PasswordField("Repita sua senha", validators=[DataRequired(), EqualTo("password1")])
    submit = SubmitField("Resetar senha")
