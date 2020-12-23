import unittest
import json

from werkzeug.security import generate_password_hash

from app import app
import os
from app.models import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class TestApplication(unittest.TestCase):
    def setUp(self):
        app.debug = True
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(BASE_DIR, 'blog.db')
        db.drop_all()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_signup(self):
        sent = {"userid": "abc", "usrtel": "111-1111-1111", "email": "abc@cn", "age": 1, "psw": "123456"}
        response = self.client.post("/signUp", data=sent)
        self.assertTrue(response)

    def test_signin(self):
        sent = {"userid": "abc", "psw": "123456"}
        response = self.client.post("/signIn", data=sent)
        self.assertTrue(response)

    def test_write_blog(self):
        sent = {"title": "title", "body": "bodybodybody"}
        response = self.client.post("/write_blog", data=sent)
        self.assertTrue(response)

    def test_write_comment(self):
        sent = {"message": "message"}
        response = self.client.post("/write_comment/title", data=sent)
        self.assertTrue(response)

    def test_change_psw(self):
        sent = {"userid": "abc", "old_psw": "123456", "new_psw": "654321"}
        response = self.client.post("/change_psw", data=sent)
        self.assertTrue(response)

    def test_search(self):
        sent = {"search": "title"}
        response = self.client.post("/search", data=sent)
        self.assertTrue(response)

    def test_logout(self):
        response = self.client.post("/logOut")
        self.assertTrue(response)


if __name__ == '__main__':
    unittest.main()
