from flask import render_template, request, redirect, url_for, Blueprint

from models.settings import db
from models.topic import Topic
from models.user import User
from models.comment import Comment

from utils.redis_helper import create_csrf_token, validate_csrf
from utils.auth_helper import user_from_session_token

comment_handlers = Blueprint("comment", __name__)


@comment_handlers.route("/topic/<topic_id>/create-comment", methods=["POST"])
def comment_create(topic_id):
    user = user_from_session_token()

    if not user:
        return redirect(url_for('auth.login'))

    csrf = request.form.get("csrf")

    if not validate_csrf(csrf, user.username):
        return "CSRF token is not valid!"

    text = request.form.get("text")
    topic = Topic.read(topic_id)

    Comment.create(topic=topic, text=text, author=user)

    return redirect(url_for('topic.topic_details', topic_id=topic_id))


@comment_handlers.route("/topic/<comment_id>/delete", methods=["GET"])
def topic_delete(comment_id):
    comment = db.query(Comment).get(int(comment_id))

    if request.method == "GET":

        db.delete(comment)
        db.commit()

        return redirect(url_for('index', comment=comment))


@comment_handlers.route("/comment/<comment_id>/edit", methods=["GET", "POST"])
def comment_edit(comment_id):
    comment = db.query(Comment).get(int(comment_id))  # get comment from db by ID

    # get current user
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    # check if user logged in & if user is author
    if not user:
        return redirect(url_for('auth.login'))
    elif comment.author.id != user.id:
        return "You can only edit your own comments!"

    # GET request
    if request.method == "GET":
        csrf_token = create_csrf_token(username=user.username)
        return render_template("comment/comment_edit.html", comment=comment, csrf_token=csrf_token)

    # POST request
    elif request.method == "POST":
        text = request.form.get("text")

        # check CSRF tokens
        csrf = request.form.get("csrf")

        if validate_csrf(csrf, user.username):
            # if it validates, edit the comment
            comment.text = text
            db.add(comment)
            db.commit()
            return redirect(url_for('topic.topic_details', topic_id=comment.topic.id))
        else:
            return "CSRF error: tokens don't match!"


@comment_handlers.route("/comment/<comment_id>/delete", methods=["POST"])
def comment_delete(comment_id):
    comment = db.query(Comment).get(int(comment_id))  # get comment from db by ID

    # get current user
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    # check if user logged in & if user is author
    if not user:
        return redirect(url_for('auth.login'))
    elif comment.author.id != user.id:
        return "You can only delete your own comments!"

    # check CSRF tokens
    csrf = request.form.get("csrf")

    if validate_csrf(csrf, user.username):
        # if it validates, delete the comment
        topic_id = comment.topic.id  # save the topic ID in a variable before you delete the comment

        db.delete(comment)
        db.commit()
        return redirect(url_for('topic.topic_details', topic_id=topic_id))
    else:
        return "CSRF error: tokens don't match!"