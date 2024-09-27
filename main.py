from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def dashboard():
    return render_template("main.html")

@app.route('/login')
def login():
    return "ok"

@app.route('/signup')
def signup():
    return "ok"

@app.route('/logout')
def logout():
    return "ok"

@app.route('/account')
def account():
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
