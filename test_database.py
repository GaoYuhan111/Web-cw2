import os
import unittest

from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from app.models import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class TestDatabase(unittest.TestCase):
    def setUp(self):
        app.debug = True
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(BASE_DIR, 'blog.db')
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user(self):
        user = User(username="abc", tel="111-1111-1111", age=1, email="abc@cn")
        user.password_hash = generate_password_hash("123456")
        db.session.add(user)
        db.session.commit()

        ret_user = User.query.filter(User.username == "abc").first()

        self.assertIsNotNone(ret_user)
        self.assertEqual(ret_user.tel, "111-1111-1111")
        self.assertEqual(ret_user.age, 1)
        self.assertEqual(ret_user.email, "abc@cn")
        self.assertTrue(check_password_hash(ret_user.password_hash, "123456"))

        ret_user.password_hash = generate_password_hash("654321")
        db.session.add(ret_user)
        db.session.commit()
        ret_user = User.query.filter(User.username == "abc").first()

        self.assertTrue(check_password_hash(ret_user.password_hash, "654321"))

        db.session.delete(ret_user)
        db.session.commit()
        ret_user = User.query.filter(User.username == "abc").first()

        self.assertIsNone(ret_user)

    def test_blog_commenter(self):
        user = User(username="abc", tel="111-1111-1111", age=1, email="abc@cn")
        user.password_hash = generate_password_hash("123456")
        db.session.add(user)
        db.session.commit()

        blog = Blog(title="title", body="bodybodybody", username="abc", num=0)
        db.session.add(blog)
        db.session.commit()

        ret_blog = Blog.query.filter(Blog.title == "title").first()

        self.assertEqual(ret_blog.body, "bodybodybody")
        self.assertEqual(ret_blog.username, "abc")
        self.assertEqual(ret_blog.num, 0)

        commenter = Commenter(commenter="abc")
        db.session.add(commenter)
        db.session.commit()
        ret_blog.commenter.append(commenter)
        ret_commenter = Commenter.query.filter(Commenter.commenter == "abc").first()

        for commenters in blog.commenter:
            self.assertEqual(commenters.commenter, "abc")

        comment = Comment(commenter="abc", blog_title="title", comment="comment")
        db.session.add(comment)
        db.session.commit()

        ret_comment = Comment.query.filter(Comment.blog_title == "title", Comment.commenter == "abc").first()

        self.assertEqual(ret_comment.comment, "comment")

        db.session.delete(ret_comment)
        db.session.commit()
        db.session.delete(ret_blog)
        db.session.commit()
        db.session.delete(ret_commenter)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()

        ret_commenter = Commenter.query.filter(Commenter.commenter == "abc").first()
        ret_blog = Blog.query.filter(Blog.title == "title").first()
        ret_comment = Comment.query.filter(Comment.blog_title == "title", Comment.commenter == "abc").first()

        self.assertIsNone(ret_commenter)
        self.assertIsNone(ret_blog)
        self.assertIsNone(ret_comment)


if __name__ == '__main__':
    unittest.main()
