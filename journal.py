from contextlib import closing
import os
from passlib.hash import pbkdf2_sha256
import psycopg2
from flask import abort
from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for


DB_SCHEMA = """
DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    text TEXT
)
"""

DB_ENTRY_INSERT = """
INSERT INTO entries (title, text) VALUES (%s, %s)
"""

DB_ENTRIES_LIST = """
SELECT id, title, text FROM entries ORDER BY id DESC
"""


app = Flask(__name__)

app.config['DATABASE'] = os.environ.get(
    'DATABASE_URL', 'dbname=flask_journal user=cewing'
)
app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_SECRET_KEY', 'sooperseekritvaluenooneshouldknow'
)
app.config['ADMIN_USERNAME'] = os.environ.get(
    'ADMIN_USERNAME', 'admin'
)
app.config['ADMIN_PASSWORD'] = os.environ.get(
    'ADMIN_PASSWORD', pbkdf2_sha256.encrypt('admin')
)

def connect_db():
    return psycopg2.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()


def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = db = connect_db()
    return db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def write_entry(title, text):
    if not title or not text:
        raise ValueError("Title and text required for writing an entry")
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_ENTRY_INSERT, [title, text])
    con.commit()


def get_all_entries():
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_ENTRIES_LIST)
    keys = ('id', 'title', 'text')
    return (dict(zip(keys, row)) for row in cur.fetchall())


def do_login(username, passwd):
    import pdb; pdb.set_trace()
    if username != app.config['ADMIN_USERNAME']:
        raise ValueError
    hashed = app.config['ADMIN_PASSWORD']
    if not pbkdf2_sha256.verify(passwd, hashed):
        raise ValueError
    session['logged_in'] = True


@app.route('/')
def show_entries():
    entries = get_all_entries()
    return render_template('list_entries.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            do_login(request.form['username'].encode('utf-8'),
                     request.form['password'].encode('utf-8'))
        except ValueError:
            error = "Invalid Login"
        else:
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('show_entries'))


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in', False):
        abort(401)
    write_entry(request.form['title'], request.form['text'])
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    from flask.ext.sass import Sass
    app.config['SASS_BIN_PATH'] = '/usr/bin/sass'
    Sass(app)
    app.run(debug=True)
