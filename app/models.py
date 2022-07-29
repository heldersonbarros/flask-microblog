from app import db, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app import login
from flask_login import UserMixin

import json

from time import time
import jwt

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

tagTable = db.Table('tags', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
    )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index= True, unique= True)
    email = db.Column(db.String(120), index = True, unique= True)
    since = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.Float, default=time)
    last_notification_read_time = db.Column(db.Float, default= 0)
    points = db.relationship("Point", backref="author", lazy="dynamic")
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    arribas = db.relationship("Arriba", backref="author", lazy="dynamic")
    muertes = db.relationship("Muerte", backref="author", lazy="dynamic")
    arriba_comments = db.relationship("ArribaComment", backref="author")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")

    def arriba_post(self, post):
        user = User.query.filter_by(id= post.author.id).first()
        if not self.has_arriba_post(post):
            arriba = Arriba(post=post, user_id=self.id)
            db.session.add(arriba)
            point = Point(user_id=post.user_id)
            db.session.add(point)
            if self.id != post.author.id:
                user.add_notification('liked_post', {'user_id': self.id, 'post_id': post.id, 'post_title': post.title})
        else:
            arriba = Arriba.query.filter_by(post=post, user_id=self.id).delete()
            point = Point.query.filter_by(user_id=post.user_id).first()
            db.session.delete(point)
            if self.id != post.author.id:
                user.add_notification('liked_post', {'user_id': self.id, 'post_id': post.id, 'post_title': post.title})

        db.session.commit()
    
    def muerte_post(self, post):
        user = User.query.filter_by(id= post.author.id).first()
        if not self.has_arriba_post(post):
            arriba = Arriba(post=post, user_id=self.id)
            db.session.add(arriba)
            point = Point(user_id=post.user_id)
            db.session.add(point)
            if self.id != post.author.id:
                user.add_notification('liked_post', {'user_id': self.id, 'post_id': post.id, 'post_title': post.title})
        else:
            arriba = Arriba.query.filter_by(post=post, user_id=self.id).delete()
            point = Point.query.filter_by(user_id=post.user_id).first()
            db.session.delete(point)
            if self.id != post.author.id:
                user.add_notification('liked_post', {'user_id': self.id, 'post_id': post.id, 'post_title': post.title})

        db.session.commit()

    def arriba_comment(self, comment):
        user = User.query.filter_by(id= comment.author.id).first()
        if not self.has_arriba_comment(comment):
            arribaComment = ArribaComment(comment=comment, user_id=self.id)
            db.session.add(arribaComment)
            point = Point(user_id=comment.user_id)
            db.session.add(point)
            #if self.id != post.author.id:
                #user.add_notification('liked_post', {'user_id': self.id, 'post_id': post.id, 'post_title': post.title})
        else:
            arribaComment = ArribaComment.query.filter_by(comment=comment, user_id=self.id).delete()
            point = Point.query.filter_by(user_id=comment.user_id).first().delete()
            #if self.id != post.author.id:
                #user.add_notification('liked_post', {'user_id': self.id, 'post_id': post.id, 'post_title': post.title})

        db.session.commit()

    def has_arriba_post(self, post):
        return Arriba.query.filter(
            Arriba.user_id == self.id,
            Arriba.post_id == post.id).count() > 0

    def has_arriba_comment(self, comment):
        return ArribaComment.query.filter(
            ArribaComment.user_id == self.id,
            ArribaComment.comment_id == comment.id).count() > 0

    def __repr__(self):
        return '<User {}>'.format(self.username) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_notification(self, type, data):
        if type == 'liked_post':
            notification = Notification.query.filter_by(type=type, payload_json=json.dumps(data), user=self).delete()
            if notification:
                return notification
        n = Notification(type=type, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n #nao sei porque tem que retornar, lembrar de testar sem

    def get_reset_password_token(self, expire_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expire_in}, app.config["SECRET_KEY"], algorithm="HS256")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
            print(id)
        except:
            return
        return User.query.get(id)

    def new_messages(self):
        last_read_time = self.last_notification_read_time or datetime(1900, 1, 1) #apagar se deletar o banco de dados
        return Notification.query.filter_by(user=self).filter(Notification.timestamp > last_read_time).count()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tag = db.relationship("Tag", secondary=tagTable, backref="posts", lazy="dynamic")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comments = db.relationship("Comment", backref="post", lazy="dynamic")
    arribas = db.relationship("Arriba", backref="post", lazy="dynamic")
    muertes = db.relationship("Muerte", backref="post", lazy="dynamic")

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    arribas = db.relationship("ArribaComment", backref="comment", lazy="dynamic")

class Arriba(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    type = db.Column(db.String(128), index= True)
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.Float, index=True, default=time)
    timestamp_datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    payload_json = db.Column(db.Text)

    def get_data(self):
        payload_dic = json.loads(str(self.payload_json))
        user_id = payload_dic['user_id']
        payload_dic['user_id'] = {"name": User.query.get(user_id).username,
                                "photo_id": user_id}
        return payload_dic

class ArribaComment(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Point(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Muerte(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

