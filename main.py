from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def dashboard():
    return render_template("login_with.html")


@app.route('/login_password')
def login_password():
    return render_template("login_password.html")


@app.route('/account')
def account():
    return render_template("account.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)