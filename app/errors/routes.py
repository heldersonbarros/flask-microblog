from app import db
from . import errors
from flask_login import current_user
from flask import render_template
from time import time

@errors.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = time()
        db.session.commit()

@errors.errorhandler(404)
def not_found_error(error):
    return render_template('errors/error.html', message="Essa página não existe ou não está disponível", 
                            error_type="404"), 404

@errors.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/error.html', message="Erro do servidor interno",
                            error_type="500"), 500

@errors.errorhandler(401)
def not_authorized_error(error):
    return render_template('errors/error.html', message="Acesso não autorizado", 
                            error_type="401"), 404