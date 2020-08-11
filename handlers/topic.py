import os

from flask import render_template, request, redirect, url_for, Blueprint

from models.settings import db
from models.topic import Topic
from models.comment import Comment

from utils.redis_helper import create_csrf_token, validate_csrf
from utils.auth_helper import user_from_session_token


topic_handlers = Blueprint("topic", __name__)


@topic_handlers.route("/create-topic", methods=["GET", "POST"])
def topic_create():
    user = user_from_session_token()

    # only logged in users can create topic
    if not user:
        return redirect(url_for('auth/login'))

    if request.method == "GET":
        csrf_token = create_csrf_token(user.username)

        return render_template("topics/topic_create.html", user=user, csrf_token=csrf_token)  # send CSRF token into HTML template

    elif request.method == "POST":
        csrf = request.form.get("csrf")  # csrf from HTML

        if validate_csrf(csrf, user.username):  # if they match, allow user to create a topic
            title = request.form.get("title")
            text = request.form.get("text")

            # create a topic object
            topic = Topic.create(title=title, text=text, author=user)

            return redirect(url_for('index'))

        else:
            return "CSRF token is not valid"


@topic_handlers.route("/topic/<topic_id>", methods=["GET"])
def topic_details(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    user = user_from_session_token()
    comments = db.query(Comment).filter_by(topic=topic).all()

    # START test background tasks (TODO: delete this code later)
    if os.getenv('REDIS_URL'):
        from task import get_random_num
        get_random_num()
    # END test background tasks €wsee¸dx;:

    return render_template("topics/topic_details.html", topic=topic, user=user,
                           csrf_token=create_csrf_token(user.username), comments=comments)


@topic_handlers.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    if request.method == "GET":
        return render_template("topics/topic_edit.html", topic=topic)

    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        user = user_from_session_token()

        # check if user is logged in and user is author
        if not user:
            redirect(url_for("auth/login"))
        elif topic.author_id != user.id:
            return "You are not an author"
        else:
            # update the topic fields
            topic.title = title
            topic.text = text
            db.add(topic)
            db.commit()

        return redirect(url_for('topic.topic_details', topic_id=topic_id))


@topic_handlers.route("/topic/<topic_id>/delete", methods=["GET", "POST"])
def topic_delete(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    if request.method == "GET":
        return render_template("topics/topic_delete.html", topic=topic)

    elif request.method == "POST":
        # get current user (author)
        user = user_from_session_token()

        # check if user is logged in and user is author
        if not user:
            return redirect(url_for('auth/login'))
        elif topic.author_id != user.id:
            return "You are not the author!"
        else:  # if user IS logged in and current user IS author
            # delete topic
            db.delete(topic)
            db.commit()
            return redirect(url_for('index'))


""" Moj način deletanja topica 
@app.route("/topic/<topic_id>/delete", methods=["GET"])
def topic_delete(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    if request.method == "GET":

        db.delete(topic)
        db.commit()

        return redirect(url_for('index'))"""