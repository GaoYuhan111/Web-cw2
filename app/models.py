from app import db
from datetime import datetime

tb_commenter_blog = db.Table('tb_commenter_blog',
                             db.Column('id', db.Integer, primary_key=True, autoincrement=True),
                             db.Column('commenter_id', db.Integer, db.ForeignKey('commenter.id')),
                             db.Column('blog_title', db.String(128), db.ForeignKey('blog.title')))


class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(64), index=True, unique=True, primary_key=True)
    tel = db.Column(db.String(13), index=True, unique=True)
    age = db.Column(db.Integer)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    blogs = db.relationship('Blog', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Username:{}>'.format(self.username)


class Blog(db.Model):
    __tablename__ = 'blog'
    title = db.Column(db.String(128), unique=True, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    username = db.Column(db.String(64), db.ForeignKey('user.username'))
    num = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Title {}>'.format(self.title)


class Commenter(db.Model):
    __tablename__ = 'commenter'
    id = db.Column(db.Integer, index=True, unique=True, autoincrement=True, primary_key=True)
    commenter = db.Column(db.String(64), unique=True)

    comments = db.relationship('Blog', secondary=tb_commenter_blog, backref='commenter', lazy='dynamic')

    def __repr__(self):
        return '<Commenter {}>'.format(self.commenter)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, index=True, unique=True, autoincrement=True, primary_key=True)
    commenter = db.Column(db.String(64), db.ForeignKey('commenter.commenter'))
    blog_title = db.Column(db.String(128), db.ForeignKey('blog.title'))
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    blogs = db.relationship('Blog', backref='comment')
    commenters = db.relationship('Commenter', backref='comment')

    def __repr__(self):
        return '<Comment {}>'.format(self.comment)
