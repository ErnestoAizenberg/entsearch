from flask import abort, render_template, session

from entsearch import app, user_repo


@app.route("/about")
def about():
    user_id = session.get("user_id")
    userinfo = user_repo.get_user_by_id(user_id)
    email = userinfo.email if userinfo else "without email"
    return render_template("about.html", email=email)


@app.route("/users/<int:passw>")
def users(passw):
    user_id = session.get("user_id")
    if user_id is None:
        return abort(401)
    password = 111
    if passw == password:
        users = user_repo.get_all_users()
        return render_template("users.html", users=users, user_id=user_id)


@app.route("/demo")
def demo():
    user_id = session.get("user_id")
    return render_template("demo.html", user_id=user_id)
