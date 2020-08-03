from flask import render_template, request, redirect, url_for, make_response, Blueprint

from models.settings import db
from models.user import User
from utils.auth_helper import user_from_session_token

import hashlib
import uuid

auth_handlers = Blueprint("auth", __name__)


@auth_handlers.route("/logout")
def logout():
    user = user_from_session_token()

    user.session_token = ""
    db.add(user)
    db.commit()

    return redirect(url_for('index'))


@auth_handlers.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        repeat = request.form.get("repeat")

        if password != repeat:
            return "Passwords don't match please try again"

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = User(
            username=username,
            password_hash=password_hash,
            session_token=str(uuid.uuid4())
        )
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie(
            "session_token",
            user.session_token,
            httponly=True,
            samesite='Strict'
        )

        return response


@auth_handlers.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(username=username).first()

        if not user:
            return "This user does not exist"
        else:
            if password_hash == user.password_hash:
                user.session_token = str(uuid.uuid4())  # if password hashes match, create a session token
                db.add(user)
                db.commit()

                # save user's session token into a cookie
                response = make_response(redirect(url_for('index')))
                response.set_cookie("session_token", user.session_token, httponly=True, samesite='Strict')

                return response
            else:
                return "Your password is incorrect!"


