from flask import request
from models.settings import db
from models.user import User


def user_from_session_token():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    return user
