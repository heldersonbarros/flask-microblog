from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, ValidationError
from app.models import User

class PostForm(FlaskForm):
    title = StringField("Titulo", validators=[DataRequired()])
    image = FileField("Imagem", validators=[DataRequired()])
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