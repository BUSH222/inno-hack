from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_user, LoginManager, current_user, login_required, UserMixin, logout_user
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

conn = psycopg2.connect(database='slotmachine',
                        user='postgres',
                        host='localhost',
                        password='12345678',
                        port=5432)
cur = conn.cursor()

schema_obj = open('schema.sql', 'r')
schema = schema_obj.read()
schema_obj.close()

@app.route('/')
def dashboard():
    return render_template("main.html")
@login_manager.user_loader
def load_user(user_id):
    cur.execute("SELECT id, name, password, balance FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    if user_data:
        return User(*user_data)
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT id, name, password, balance FROM users WHERE name = %s", (username,))
        user_data = cur.fetchone()
        if user_data:
            if user_data[2] == password and len(password) < 32:
                user = User(*user_data)
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                print("bruh")
        else:
            cur.execute("SELECT MAX(id) FROM users")
            maxid = int(cur.fetchone()[0])
            cur.execute("INSERT INTO users (id, name, password) VALUES (%s, %s, %s) RETURNING id",
                        (maxid+1, username, password))
            new_user_id = cur.fetchone()[0]
            conn.commit()
            cur.execute("SELECT id, name, password, balance FROM users WHERE id = %s", (new_user_id,))
            new_user_data = cur.fetchone()
            new_user = User(*new_user_data)
            login_user(new_user)
            return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}! Your balance is {current_user.balance}.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

