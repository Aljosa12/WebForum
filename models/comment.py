from models.settings import db
from datetime import datetime
from utils.email_helper import send_email


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # User foreign key
    author = db.relationship("User")  # User relationship

    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))  # Topic foreign key
    topic = db.relationship("Topic")  # Topic relationship

    created = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, text, author, topic):
        comment = cls(text=text, author=author, topic=topic)
        db.add(comment)
        db.commit()

        # only send of topic author has her/his email in the database
        if topic.author.email_address:
            send_email(receiver_email=topic.author.email_address, subject="New comment for your topic!",
                       text="Your topic {} has a new comment.".format(topic.title))

        return comment

    @classmethod
    def read_all(cls, topic):
        comments = db.query(Comment).filter_by(topic=topic).all()

        return comments