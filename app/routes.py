from app import app, login, db
from app.forms import LoginForm, RegisterForm, PostForm, EditProfileForm, CommentForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post, Tag, Comment, Arriba, Notification, Point, ArribaComment
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, redirect, url_for, flash, jsonify, abort, send_from_directory
from sqlalchemy import func
from time import time
from datetime import datetime, timedelta
import os
import imghdr

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = time()
        db.session.commit()

@app.errorhandler(404)
def not_found_error(error):
    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        return login_function(loginForm)
    
    return render_template('error.html', message="Essa página não existe ou não está disponível", 
                            error_type="404",postForm=postForm, loginForm=loginForm), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', message="Erro do servidor interno",
                            error_type="500",postForm=postForm, loginForm=loginForm), 500

@app.errorhandler(401)
def not_authorized_error(error):
    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        return login_function(loginForm)
    
    return render_template('error.html', message="Acesso não autorizado", 
                            error_type="401",postForm=postForm, loginForm=loginForm), 404

@app.route("/")
def index():
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    return render_template("index.html", title="Trending", loginForm=loginForm, postForm=postForm)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        return login_function(loginForm)

    return render_template("login.html", title="Login", loginForm=loginForm, postForm=postForm)

def login_function(loginForm):
    user = User.query.filter_by(username=loginForm.username.data).first()
    if user is None or not user.check_password(loginForm.password.data):
        flash("Senha ou nome do usuário inválido!", "error")
        return redirect(url_for("login"))

    login_user(user, loginForm.remember_me.data)

    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email= form.email.data)
        user.set_password(form.password1.data)
        flash("Registrado com sucesso!", "success")

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("register.html", title = "Registrar", form= form, loginForm=loginForm,
                            postForm=postForm)

@app.route("/user/<username>", methods=["GET", "POST"])
def user(username):
    order = request.args.get("order", "top", type=str)
    user = User.query.filter_by(username=username).first_or_404()
    postForm = PostForm()

    posts = user.posts
    if order=="top":
        #filtrar usuário
        posts = db.session.query(Post).join(Arriba).group_by(Post.id).filter(Post.user_id == user.id).order_by(func.count().desc()).all()
    elif order=="novos":
        posts = Post.query.filter(Post.user_id == user.id).order_by(Post.timestamp.desc())


    liked_id = []

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    if postForm.validate_on_submit():
        add_post(postForm)
    
    if current_user.is_authenticated:
        for post in user.posts:
            for arriba in post.arribas:
                if arriba in current_user.arribas:
                    liked_id.append(post.id)
    
    return render_template("user.html", user=user, posts=posts, liked_id=liked_id, order=order, 
                            loginForm=loginForm, postForm=postForm)

@app.route("/user/<username>/details")
def user_detail(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user_popover.html", user=user)

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

def add_post(postForm):
    if current_user.is_anonymous:
        return redirect(url_for("login"))

    post = Post(title=postForm.title.data, author=current_user)
    tag = Tag.query.filter_by(name=postForm.tag.data).first()
    if tag is None:
        tag = Tag(name=postForm.tag.data)

    image = request.files['image']
    file_extension = os.path.splitext(image.filename)[1]
    if file_extension not in app.config["ALLOWED_IMAGE_EXTENSIONS"] or file_extension != validate_image(image.stream):
        abort(400)
        
    basedir= os.path.abspath(os.path.dirname(__file__))
    image.save(os.path.join(basedir, app.config['UPLOAD_PATH'], str(post.id) + file_extension))

    post.tag.append(tag)

    db.session.add(post)
    db.session.commit()

    current_user.arriba_post(post)

    flash("Postagem feita com sucesso!", "success")
    return redirect(url_for("new_posts"))

@app.route("/uploads/<post_id>")
def uploads(post_id):
    return send_from_directory(app.config["UPLOAD_PATH"], post_id + ".jpg")

@app.route("/uploads/avatars/<user_id>")
def avatars_profile(user_id):
    return send_from_directory(app.config["AVATAR_UPLOAD_PATH"], str(user_id) + ".jpg")

@app.route("/new", methods=["GET", "POST"])
def new_posts():
    posts = Post.query.order_by(Post.timestamp.desc())
    liked_id = []

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)
        
    if current_user.is_authenticated:
        for post in posts:
            for arriba in post.arribas:
                if arriba in current_user.arribas:
                    liked_id.append(post.id)

    return render_template("new_posts.html", title="Últimas", posts=posts.all(), liked_id=liked_id, postForm=postForm, loginForm=loginForm)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    if form.validate_on_submit():
        current_user.username= form.username.data
        db.session.commit()

        avatar = request.files['avatar']
        print(avatar.filename)
        file_extension = os.path.splitext(avatar.filename)[1]
        if file_extension not in app.config["ALLOWED_IMAGE_EXTENSIONS"] or file_extension != validate_image(avatar.stream):
            abort(400)
        
        basedir= os.path.abspath(os.path.dirname(__file__))
        avatar.save(os.path.join(basedir, app.config['AVATAR_UPLOAD_PATH'], str(current_user.id)) + file_extension)

        flash("Informações alteradas com sucesso!")

        return redirect(url_for("edit_profile", loginForm=loginForm, postForm=postForm))

    elif request.method=="GET":
        form.username.data = current_user.username
        pass

    return render_template("edit_profile.html", title="Editar Perfil", form=form, loginForm=loginForm, postForm=postForm)

@app.route("/tag/<name>")
def tag(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    posts = []
    for post in tag.posts:
        posts.append(post)

    return render_template("new_posts.html", title=name, posts=posts)

@app.route("/tags")
def tags():
    tags = Tag.query.all()

    return render_template("tags.html", title="Tags", tags=tags)

@app.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = CommentForm()
    
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    if form.validate_on_submit():
        comment = Comment(user_id=current_user.id, post_id=id, text=form.text.data)
        if post.user_id != current_user.id:
            user = User.query.filter_by(id=post.user_id).first()
            user.add_notification('comment_post', {'user_id': current_user.id, 'post_id': post.id, 'post_title': post.title})
        if post.user_id != current_user.id and '@' in form.text.data:
            mentioned = form.text.data[form.text.data.find('@'):].split()[0][1:]
            user = User.query.filter_by(username= mentioned).first()
            if user:
                user.add_notification('mention_post', {'user_id': current_user.id, 'post_id': post.id, 'post_title': form.text.data})

        db.session.add(comment)
        db.session.commit()

        current_user.arriba_comment(comment)

        redirect(url_for("post", id=id))


    like_id = []
    likeComment_id = []
    if current_user.is_authenticated:
        for arriba in post.arribas:
            if arriba in current_user.arribas:
                like_id.append(post.id)

        for comment in post.comments:
            for arriba in comment.arribas:
                if arriba.user_id == current_user.id:
                    likeComment_id.append(comment.id)

    highlights_comments = db.session.query(Comment).join(ArribaComment).group_by(Comment.id).order_by(func.count().desc()).limit(2).all()
    last_comments = Comment.query.filter(Comment.id != highlights_comments[0].id).filter(Comment.id != highlights_comments[1].id).order_by(Comment.timestamp.desc()).all()

    return render_template("post.html", title=post.title, post=post, form=form, liked_id=like_id,
                            comments=last_comments, highlights_comments=highlights_comments, likeComment_id=likeComment_id, loginForm=loginForm, 
                            postForm= postForm)

@app.route("/my_comments", methods=["GET", "POST"])
@login_required
def my_comments():
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)
    
    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)
    
    return render_template("my_comments.html", title="Meus comentários", comments=current_user.comments, 
                            loginForm=loginForm, postForm=postForm)

@app.route("/add_comment", methods=["POST"])
@login_required
def add_comment():
    return jsonify({'text': "",
        'date': "",
        'user': "",
        })

@app.route("/arriba_post", methods=["POST"])
def arriba_post():
    post = Post.query.filter_by(id=request.form['post_id']).first()
    if post:
        current_user.arriba_post(post)
        return jsonify({'count': post.arribas.count(), 'result': 'success'})
    else:
        return jsonify({'result': 'failed'})

@app.route("/muerte_post", methods=["POST"])
def muerte_post():
    post = Post.query.filter_by(id=request.form['post_id']).first()
    if post:
        current_user.muerte_Post(post)
        return jsonify({'count': post.muerte.count(), 'result': 'success'})
    else:
        return jsonify({'result': 'failed'})

@app.route("/arriba_comment", methods=["POST"])
def arriba_comment():
    comment = Comment.query.filter_by(id=request.form['comment_id']).first()
    if post:
        current_user.arriba_comment(comment)
        return jsonify({'count': comment.arribas.count(), 'result': 'success'})
    else:
        return jsonify({'result': 'failed'})

@app.route("/my_arribas", methods=["GET", "POST"])
@login_required
def my_arribas():
    #gambiarra
    arribas = Arriba.query.filter_by(user_id= current_user.id)
    posts = []
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)
    
    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)
    for arriba in arribas:
        posts.append(Post.query.get(arriba.post_id))

    liked_id = []
    if current_user.is_authenticated:
        for post in posts:
            for arriba in post.arribas:
                if arriba in current_user.arribas:
                    liked_id.append(post.id)

    return render_template("my_arribas.html", title="Meus arribas", posts = posts, liked_id=liked_id, loginForm=loginForm,
                            postForm=postForm)

@app.route("/tops", methods=["GET", "POST"])
def tops():
    order = request.args.get("order", "hoje", type=str)
    today_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    
    if order=="sempre":
        posts = db.session.query(Post).join(Arriba).group_by(Post.id).order_by(func.count().desc()).all()
    else:
        if order=="hoje":
            date = today_datetime
        elif order=="semana":
            date = today_datetime - timedelta(days=7)
        elif order=="mes":
            date = today_datetime - timedelta(days=30)
        
        posts = db.session.query(Post).join(Arriba).group_by(Post.id).filter(Arriba.timestamp >= date).order_by(func.count().desc()).all()

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    liked_id = []
    if current_user.is_authenticated:
        for post in posts:
            for arriba in post.arribas:
                if arriba in current_user.arribas:
                    liked_id.append(post.id)

    return render_template("tops.html", title = "Tops", posts=posts, loginForm=loginForm,
                            postForm=postForm, liked_id=liked_id, order=order)

@app.route("/ranking", methods=["GET", "POST"])
def ranking():
    order = request.args.get("order", "hoje", type=str)

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    today_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)

    if order=="sempre":
        users = db.session.query(User).join(Point).group_by(User.id).order_by(func.count().desc()).all()
    else:
        if order=="hoje":
            date = today_datetime
        elif order=="semana":
            date = today_datetime - timedelta(days=7)
        elif order=="mes":
            date = today_datetime - timedelta(days=30)
        
        users = db.session.query(User).join(Point).group_by(User.id).filter(Point.timestamp >= date).order_by(func.count().desc()).all()
    
    types = [] 
    for user in users:
        today = Point.query.filter(Point.user_id == user.id).filter(Point.timestamp >= today_datetime).count()
        week = Point.query.filter(Point.user_id == user.id).filter(Point.timestamp >= today_datetime - timedelta(days=7)).count()
        month = Point.query.filter(Point.user_id == user.id).filter(Point.timestamp >= today_datetime - timedelta(days=30)).count()
        types.append({"today": today, "week": week, "month": month})

    return render_template("ranking.html", title = "Ranking", users=users, order=order,loginForm=loginForm, 
                            postForm=postForm, types=types)

@app.route("/notifications")
@login_required
def notification():
    since = request.args.get("since", 0.0, type=float)
    notifications = current_user.notifications.filter(Notification.timestamp>since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.type,
        'data': n.get_data(),
        'timestamp': n.timestamp,
        'message_count': current_user.new_messages()
        } for n in notifications])

@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email= form.email.data).first()
        if user:
            #Enviar email
            flash("Verifique seu email para mais informações.", "success")
            return redirect(url_for("login"))
    
    return render_template("reset_password_request.html", title= "Recuperar conta", form=form,
                            loginForm=loginForm, postForm=postForm)

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = ResetPasswordForm()
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("index"))

    if form.validate_on_submit():
        user.set_password(form.password1.data)
        db.session.commit()
        flash("Sua senha foi alterada com sucesso!", "success")
        return redirect(url_for("login"))

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    postForm = PostForm()
    if postForm.validate_on_submit():
        add_post(postForm)

    return render_template("reset_password.html", title= "Resete sua senha", form = form,
                            loginForm=loginForm, postForm=postForm)

@app.route("/get_token/<id>")
def get_test_token(id):
    user = User.query.get(id)
    return user.get_reset_password_token()

@app.route("/my_notifications", methods=["GET", "POST"])
@login_required
def my_notifications():
    postForm = PostForm()
    
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        login_function(loginForm)

    if postForm.validate_on_submit():
        add_post(postForm)
    current_user.last_notification_read_time = time()
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    notifications = current_user.notifications.filter(Notification.read == 0).order_by(Notification.timestamp.desc()).paginate(
        page, 8, True)
    if notifications.has_next:
        next_url = url_for('my_notifications', page= notifications.next_num)
    else:
        next_url = None

    if notifications.has_prev:
        prev_url = url_for('my_notifications', page = notifications.prev_num)
    else:
        prev_url = None
    return render_template("my_notifications.html", title="Notificações", notifications=notifications.items, next_url= next_url,
        prev_url = prev_url, loginForm=loginForm, postForm=postForm)

@app.route("/add_notification/<recepient>/<post_id>", methods=["GET" ,"POST"])
def add_notification(recepient, post_id):
    user = User.query.filter_by(username= recepient).first()
    user.add_notification('liked', {'user_id': current_user.id, 'post_id': post_id})
    db.session.commit()
    return "OK!"

