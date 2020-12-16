# from admin.admin import admin
from datetime import datetime
# from FDataBase import FDataBase
from flask import abort, flash, Flask, g, make_response, redirect, render_template, request, session, url_for
from flask_login import current_user, LoginManager, login_user, login_required, logout_user, UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from forms import AddPostForm, AmendPostForm, LoginForm, RegisterForm
import os
import requests as req
from sqlalchemy import desc, select
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false
import sqlite3
# from UserLogin import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash

__author__ = 'Marina Krivcun'
# конфигурация
# DATABASE = '/tmp/flsite.db'
DEBUG = True
# SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
# app.config.from_object(__name__)
# app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))
 
app.config['SECRET_KEY'] = 'fdgfh78@#5?>gfhf89dx,v06k'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flsite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# app.register_blueprint(admin, url_prefix='/admin')
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
# login_manager.login_message_category = "success"

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, unique=True)
    psw = db.Column(db.Text, nullable=True)
    # avatar = db.Column(db.LargeBinary, nullable=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"
    # def getName(self):
    #     return self.name
    # def getEmail(self):
    #     return self.email
    # def create(self, user):
    #     self.__user = user
    #     return self
    # def getAvatar(self, app):
    #     img = None
    #     if not self.avatar:
    #         try:
    #             with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f:
    #                 img = f.read()
    #         except FileNotFoundError as e:
    #             print("Не найден аватар по умолчанию: "+str(e))
    #     else:
    #         img = self.avatar
    #     return img
    # def verifyExt(self, filename):
    #     ext = filename.rsplit('.', 1)[1]
    #     if ext == "png" or ext == "PNG":
    #         return True
    #     return False

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=True)
    text = db.Column(db.Text, unique=True)
    url = db.Column(db.Text, nullable=True)
    # time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hidden = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<posts {self.id}>"

class Mainmenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<mainmenu {self.id}>"

# @login_manager.user_loader
# def load_user(user_id):
#     print("load_user")
#     return Users.query.filter_by(id=user_id).first()

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Users.query.get(int(user_id))

# def connect_db():
#     conn = sqlite3.connect(app.config['DATABASE'])
#     conn.row_factory = sqlite3.Row
#     return conn

# def create_db():
#     """Вспомогательная функция для создания таблиц БД"""
#     db = connect_db()
#     with app.open_resource('sq_db.sql', mode='r') as f:
#         db.cursor().executescript(f.read())
#     db.commit()
#     db.close()

# def get_db():
#     '''Соединение с БД, если оно еще не установлено'''
#     if not hasattr(g, 'link_db'):
#         g.link_db = connect_db()
#     return g.link_db

mainmenu = []
# dbase = None
@app.before_request
def before_request():
    # """Установление соединения с БД перед выполнением запроса"""
    # global dbase
    # db = get_db()
    # dbase = FDataBase(db)
    global mainmenu
    try:
        mainmenu = Mainmenu.query.all()
        # print(type(mainmenu))
        # print(mainmenu)
    except:
        print("Ошибка чтения mainmenu из БД")

# @app.teardown_appcontext
# def close_db(error):
#     '''Закрываем соединение с БД, если оно было установлено'''
#     if hasattr(g, 'link_db'):
#         g.link_db.close()

menu = [{'url': 'aindex', 'title': 'Панель'},
        # {'url': 'admin/listusers', 'title': 'Список пользователей'},
        {'url': 'listpubs', 'title': 'Список записей'},
        {'url': 'alogout', 'title': 'Выйти'}
        ]

def isLogged():
    return True if session.get('admin_logged') else False

def login_admin():
    session['admin_logged'] = 1

def logout_admin():
    session.pop('admin_logged', None)

@app.route('/admin/')
def aindex():
    if not isLogged():
        return redirect(url_for('alogin'))
    return render_template('/admin/index.html', menu=menu, title='Админ-панель')

@app.route('/admin/login/', methods=["POST", "GET"])
def alogin():
    if isLogged():
        return redirect(url_for('aindex'))
    form = LoginForm()
    print("form ",form)
    if form.validate_on_submit():
        print("form.email.data ",form.email.data)
        print("form.psw.data ",form.psw.data)
        if form.email.data == "a@dm.in" and form.psw.data == "12345":
            print("form..data")
            login_admin()
            print("login_admin")
            return redirect(url_for('aindex'))
        else:
            flash("Неверная пара логин/пароль", "error")
    return render_template('/admin/login.html', title='Админ-панель', form=form)

@app.route('/admin/logout/', methods=["POST", "GET"])
def alogout():
    if not isLogged():
        return redirect(url_for('alogin'))
    logout_admin()
    return redirect(url_for('alogin'))

@app.route('/list-pubs/')
def listpubs():
    if not isLogged():
        return redirect(url_for('alogin'))
    posts = []
    posts = Posts.query.order_by(desc(Posts.time)).all()
    return render_template('/admin/listpubs.html', title='Список записей', menu=menu, list=posts)

@app.route("/amend-pubs/<alias>", methods=["POST", "GET"])
def amendpubs(alias):
    if not isLogged():
        return redirect(url_for('alogin'))
    post = Posts.query.filter(Posts.url.ilike(f'%{alias}%')).first()
    print("obj", post)
    form = AmendPostForm(obj=post)
    if form.validate_on_submit():
        d = form.delete.data
        print("d", d)
        if d:
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('listpubs'))
        try:
            print("form.title.data", form.title.data)
            form.populate_obj(post)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Ошибка изменения записи', category='error')
        return render_template('amend-pubs.html', menu=mainmenu, form=form, title="Запись изменена")
    return render_template('amend-pubs.html', menu=mainmenu, form=form, title="Изменение записи")


@app.route("/")
@app.route('/index/', methods=['GET'])
def index():
    # p = Posts.query.order_by(desc(Posts.time)).all()
    p = Posts.query.filter(Posts.hidden==false()).order_by(desc(Posts.time)).all()
    # p = Posts.query.all()
    print(p)
    return render_template('index.html', menu=mainmenu, posts=p)

@app.route("/add_post/", methods=["POST", "GET"])
def addPost():
    form = AddPostForm()
    user = current_user
    print(user)
    userid = current_user.id
    print(userid)
    if form.validate_on_submit():
        try:
            print("form.title.data", form.title.data)
            p = Posts(title=form.title.data, url=form.url.data, text=form.text.data, user_id=userid)
            print("p", p)
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
    # if request.method == "POST":
    #     if len(request.form['name']) > 4 and len(request.form['post']) > 10:
    #         res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
    #         if not res:
    #             flash('Ошибка добавления статьи', category = 'error')
    #         else:
    #             flash('Статья добавлена успешно', category='success')
    #     else:
            flash('Ошибка добавления записи', category='error')
        return redirect(url_for('index'))
        # mainmenu = ["Установка", "Первое приложение", "Обратная связь"]
        # return render_template('add_post.html', menu=mainmenu, form=form, title="Добавление статьи")
    # mainmenu = ["Установка", "Первое приложение", "Обратная связь"]
    return render_template('add_post.html', menu=mainmenu, form=form, title="Добавление записи")

@app.route("/amend_post/<alias>", methods=["POST", "GET"])
@login_required
def amendPost(alias):
    post = Posts.query.filter(Posts.url.ilike(f'%{alias}%')).first()
    print("obj", post)
    form = AmendPostForm(obj=post)
    # form = AmendPostForm()
    # if not form.is_submitted():
    #     form = AmendPostForm.populate_obj(post)
    # else:
    #     form = AmendPostForm() # will populate from submitted data
    if form.validate_on_submit():
        # d = form.delete.data
        # print("d", d)
        # if d:
        #     db.session.delete(post)
        #     db.session.commit()
        #     return redirect(url_for('index'))
        try:
            print("form.title.data", form.title.data)
            # p = Posts(title=form.title.data, url=form.url.data, text=form.text.data, hidden=form.hidden.data)
            # print("p", p)
            form.populate_obj(post)
            # db.session.add(post)
            db.session.commit()
            # flash('Запись изменена')
        except:
            db.session.rollback()
            flash('Ошибка изменения записи', category='error')
        return render_template('amend_post.html', menu=mainmenu, form=form, title="Запись изменена")
    return render_template('amend_post.html', menu=mainmenu, form=form, title="Изменение записи")

@app.route("/post/<alias>")
@login_required
def showPost(alias):
    # title, post = dbase.getPost(alias)
    # query_all = Posts.query.all()
    # print("all",query_all)
    # title, post = select([title, text]).where(posts.c.url.ilike(f'%{alias}%'))
    title, post, byuser, hidden = Posts.query.filter(Posts.url.ilike(f'%{alias}%')).with_entities(Posts.title, Posts.text, Posts.user_id, Posts.hidden).first()
    # output = Posts.query(Posts).filter(Posts.url.ilike('%' + alias + '%'))
    # print("filter",output)
    # stmt = self.posts.c.url.ilike('%alias%')
    # print("self",stmt)
    if not title:
        abort(404)
    print(" title ",title)
    print(" post ",post)
    # print(" byuser ",byuser)
    print(" hidden ",hidden)
    # print(" current_user ",current_user)
    # # cu = Users.query.filter_by(id=byuser).first()
    # # print(" cu ",cu)
    # cid = current_user.id
    # print(" cid ",cid)
    # # if cu == current_user:
    # #     print("cu == current_user (ok but the other is simpler)")
    # if byuser == cid:
    #     print("byuser == cid")
    return render_template('post.html', menu=mainmenu, title=title, post=post, hidden=hidden)

@app.route("/login/", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
# getUserByEmail(self, email):
#         try:
#             self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
#             res = self.__cur.fetchone()
#             if not res:
#                 print("Пользователь не найден")
#                 return False
#             return res
#         except sqlite3.Error as e:
#             print("Ошибка получения данных из БД "+str(e))
#         return False
        user = Users.query.filter_by(email=form.email.data).first()
        print("user",user)
        # user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user.psw, form.psw.data):
            # userlogin = Users.create(user=user)
            # userlogin = Users.query.filter_by(email=email).first()
            # print("userlogin",userlogin)
            rm = form.remember.data
            print("rm",rm)
            # login_user(userlogin, remember=rm)
            login_user(user, remember=rm)
            # return redirect(request.args.get("next") or url_for("index"))
            return redirect(request.args.get("next") or url_for("profile"))
        flash("Неверная пара логин/пароль", "error")
    return render_template("login.html", menu=mainmenu, title="Авторизация", form=form)

@app.route("/register/", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            print(form.psw.data)
            hash = generate_password_hash(form.psw.data)
            u = Users(name=form.name.data, email=form.email.data, psw=hash)
            print(u)
            db.session.add(u)
            db.session.commit()
            flash("Вы успешно зарегистрированы", "success")
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
        return redirect(url_for('profile'))
    return render_template("register.html", menu=mainmenu, title="Регистрация", form=form)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile/')
@login_required
def profile():
    posts = []
    posts = Posts.query.filter_by(user_id=current_user.id).order_by(desc(Posts.time)).all()
    return render_template("profile.html", menu=mainmenu, title="Профиль", user=current_user, posts=posts)


@app.route('/contacts/')
def contacts():
  return render_template('contacts.jinja2', menu=mainmenu, title="Контакты")

@app.route('/courses/')
def courses():
  return render_template('courses.jinja2', menu=mainmenu, title="Образовательная программа")

@app.route('/teachers/')
def teachers():
  return render_template('teachers.jinja2', menu=mainmenu, title="Сотрудники")

# @app.route('/userava')
# @login_required
# def userava():
#     img = current_user.getAvatar(app)
#     if not img:
#         return ""

#     h = make_response(img)
#     h.headers['Content-Type'] = 'image/png'
#     return h

# @app.route('/upload', methods=["POST", "GET"])
# @login_required
# def upload():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and current_user.verifyExt(file.filename):
#             try:
#                 img = file.read()
#                 try:

# # UPDATE Users SET name = 'user' WHERE id = '3'
# # user = Users.query.filter_by(email=form.email.data).first()
# #         print("user",user)
#                     a_user = Users.query.filter(id == current_user.get_id()).one()
#                     # binary = sqlite3.Binary(avatar)
#                     # a_user.avatar = binary
#                     a_user.avatar = img
#                     session.commit()
#                 except:
#                     db.session.rollback()
#                     print("Ошибка добавления в БД")
#     # def updateUserAvatar(self, avatar, user_id):
#     #     if not avatar:
#     #         return False
#     #     try:
#     #         binary = sqlite3.Binary(avatar)
#     #         self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
#     #         self.__db.commit()
#     #     except sqlite3.Error as e:
#     #         print("Ошибка обновления аватара в БД: "+str(e))
#     #         return False
#     #     return True
#                 # res = dbase.updateUserAvatar(img, current_user.get_id())
#                 # if not res:
#                 #     flash("Ошибка обновления аватара", "error")
#                 flash("Аватар обновлен", "success")
#             except FileNotFoundError as e:
#                 flash("Ошибка чтения файла", "error")
#         else:
#             flash("Ошибка обновления аватара", "error")
#     return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True)
