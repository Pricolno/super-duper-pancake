from flask import Flask, url_for, render_template, request, flash, session, redirect, abort, g
import sqlite3
import os
from FDataBase import FDataBase

app = Flask(__name__)

# конфигурация app.config['__']
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
USERNAME = 'admin'
PASSWORD = '123'

app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

menu = [{"name": "Установка", "url": "install-flask"},
        {"name": "Первое приложение", "url": "first-app"},
        {"name": "Обратная связь", "url": "contact"},
        {"name": "Профиль", "url": "login"}]


# sql

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    # conn.row_factory = sqlite3.Row
    conn.row_factory = dict_factory

    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sql_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


# routing
@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()

    dbase = FDataBase(db)
    print(dbase.getMenu())
    print(dbase.getMenu()[0]['title'])

    # return render_template('simple.html', menu=menu, title='Flask_|||')
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce(), title='Про Flask')


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu)


@app.route("/login", methods=["POST", "GET"])
def login():
    print(request.form)
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif 'username' in request.form and 'psw' in request.form and request.form['username'] == "selfedu" and \
            request.form['psw'] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title="Авторизация", menu=menu)


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)

    return f"Пользователь: {username}"


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<int:id_post>")
def showPost(id_post):
    db = get_db()
    dbase = FDataBase(db)
    # title, text
    post = dbase.getPost(id_post)
    print(post)
    if not post:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title='', post=post)


if __name__ == '__main__':
    app.run(debug=True)
