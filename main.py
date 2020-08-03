from flask import Flask, render_template, request

from models.user import User
from models.settings import db
from models.topic import Topic

from handlers.auth import auth_handlers
from handlers.topic import topic_handlers
from handlers.comment import comment_handlers

app = Flask(__name__)
app.register_blueprint(auth_handlers)
app.register_blueprint(topic_handlers)
app.register_blueprint(comment_handlers)
db.create_all()

# Handler/controller
@app.route('/', methods=["GET", "POST"])
def index():
    # check if user is authenticated based on session_token
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    # get all topics from db
    topics = db.query(Topic).all()

    return render_template("topics/index.html", user=user, topics=topics)


if __name__ == '__main__':
    app.run()

