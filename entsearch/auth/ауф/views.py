# app, session, render_template

from flask import render_template, session

from entsearch import app


@app.route("/login", methods=["GET", "POST"])
def login_page():
    user_id = session.get("user_id")
    return render_template("login.html", user_id=user_id)
