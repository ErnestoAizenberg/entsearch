
from flask import render_template, session
from entity_serch import app, user_repo


@app.after_request
def add_cache_headers(response):
    response.cache_control.public = True
    response.cache_control.max_age = 30 * 24 * 60 * 60  #30 times will day past
    response.headers['Cache-Control'] = 'public, max-age={}'.format(30 * 24 * 60 * 60)
    return response

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
 

@app.route("/about")
def about():
    user_id = session.get('user_id')
    userinfo = user_repo.get_user_by_id(user_id)
    email = userinfo.email if userinfo else "without email"
    return render_template('about.html', email=email)


@app.route("/users/<int:passw>")
def users(passw):
    password = 111
    if passw == password:
        users = user_repo.get_all_users()
        return render_template('users.html', users=users)