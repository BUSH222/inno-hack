from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_user, LoginManager, current_user, login_required, UserMixin, logout_user
from dbmanager import conn, cur, preload_db, create_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password, balance):
        self.id = id
        self.username = username
        self.password = password
        self.balance = balance

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

        


@app.route('/dashboard',methods=['GET'])
@login_required
def dashboard():
    if request.method == "POST":
        option = request.args.get("opt")
        if option == "new_reposidtory":
            redirect(url_for())
        if option == "join_reposidtory":
            redirect(url_for())
        if option == "my_reposidtoriers":
            redirect(url_for())
        
            
    return render_template

@app.route('/new_repository_edit')
@login_required
def n_editor():
    return render_template()



@app.route('/ex_repository_edit')
@login_required
def e_editor():
    return render_template()


if __name__ == '__main__':
    preload_db()
    app.run(host='0.0.0.0', port=8000)

