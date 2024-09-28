from flask import Flask, redirect, render_template, request, url_for, abort
from flask_login import login_user, LoginManager, current_user, login_required, UserMixin, logout_user
from dbmanager import (conn, cur, preload_db, create_user, get_all_user_data_by_name,
                       get_all_user_data_by_id, check_access, create_repository,
                       get_repo_info, get_user_repos, add_user_to_repo, make_commit)
from oauthlib.oauth2 import WebApplicationClient
from helper import (GOOGLE_CLIENT_ID,
                    GOOGLE_CLIENT_SECRET,
                    GOOGLE_DISCOVERY_URL,
                    APPROVED_EMAILS)
import requests
import json


app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
client = WebApplicationClient(GOOGLE_CLIENT_ID)


class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    user_data = get_all_user_data_by_id(user_id)
    if user_data:
        return User(*user_data)
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Find out what URL to hit for Google login
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']
    #     user_data = get_all_user_data_by_name(username)
    #     if user_data:
    #         if user_data[2] == password and len(password) < 32:
    #             user = User(*user_data)
    #             login_user(user)
    #             return redirect(url_for('dashboard'))
    #         else:
    #             print("bruh")
    #     else:
    #         new_user_data = create_user(username, password)
    #         new_user = User(*new_user_data)
    #         login_user(new_user)
    #         return redirect(url_for('dashboard'))
    # else:
    #     return render_template('login.html')


@app.route("/login/callback")
def callback():
    """Get authorization code Google sent back to you"""
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # if not users_email.endswith('@edu.misis.ru'):
    #     abort(403)

    user = User(id_=unique_id, name=users_name, email=users_email)
    if user.email in APPROVED_EMAILS:  # give user admin
        user.adminst = 1
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, admin=1)
    login_user(user)
    return redirect(url_for("index"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == "POST":
        usr_input = request.json
        if usr_input["btn_type"] == "new_reposidtory":
            return redirect(url_for("new_repository_creator"))
        if usr_input["btn_type"] == "join_reposidtory":
            if check_access(usr_input["rep_id"], current_user.id):
                return redirect(url_for('repository_edit'), rep_id=usr_input['rep_id'])
            else:
                return render_template("error.html", change="error! you have no access")
        if usr_input["btn_type"] == "my_reposidtoriers":
            return redirect(url_for('my_repositories'))
    return render_template("error.html", change='')


@app.route('/my_repositories', methods=['GET', 'POST'])
@login_required
def my_reps():
    if request.method == "GET":
        info = get_user_repos(current_user.id)
    if request.method == "POST":
        usr_input = request.json
        if usr_input["btn_click"] == "edit_existing_repo":
            return redirect(url_for("repository_edit", usr_input["rep_id"]))
        elif usr_input["btn_click"] == "create_new_repo":
            return redirect(url_for("new_repository_creator"))
    return render_template("account.html", info=info)


@app.route('/new_repository_creator', methods=['GET', 'POST'])
@login_required
def n_creator():
    if request.method == "POST":
        info = request.json
        # check validity of info provided
        rep_id = create_repository(current_user.id, info["repository_name"])
        return redirect(url_for('repository_edit'), rep_id=rep_id)
    return render_template()  # maybe create and just open a new blank repository


@app.route('/repository_edit', methods=['GET', 'POST'])
@login_required
def e_editor():
    if request.method == "GET":
        rep_id = request.args.get("rep_id")
        user_id = current_user.id
        if check_access(rep_id, user_id):
            contains = get_repo_info(rep_id)
        else:
            abort(403)
    if request.method == "POST":
        user_choice = request.json
        if user_choice["btn_click"] == "new_commit":
            return redirect(url_for('new_commit', rep_id=rep_id))
        elif user_choice["btn_click"] == "add_users_to_repository":
            return redirect(url_for('add_users_to_repo'), rep_id=rep_id)
    return render_template("commit_list.html", contains=contains)


@app.route('/add_users_to_repo', method=["POST"])
@login_required
def add_users():
    change = ''
    if request.method == "POST":
        usr_input = request.json
        rep_id = request.args.get("rep_id")
        if check_access(rep_id, current_user.id):
            if usr_input["btn_click"] == "add":
                add_user_to_repo(rep_id, usr_input["user_id_to_add"])
                change = "Users added!"
            else:
                abort(403)
    return redirect(url_for('repository_edit', rep_id=rep_id))


@app.route('/new_commit', method=["POST"])
@login_required
def c_editor():
    change = ''
    if request.method == "POST":
        user_changes = request.json
        rep_id = request.args.get("rep_id")
        user_id = current_user.id
        if check_access(rep_id, user_id):
            if user_changes["btn_type"] == 'commit':
                make_commit(user_changes["text"], user_id, rep_id, user_changes["c_name"])
                change = 'Commited!'
        else:
            abort(403)
    return render_template("commit_new.html", change=change)


if __name__ == '__main__':
    preload_db()
    app.run(host='0.0.0.0', port=5000)
