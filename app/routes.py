from flask import *
# from datetime import *
from sqlalchemy import *
from flask_moment import *
from flask_paginate import *
from werkzeug.security import check_password_hash, generate_password_hash

from app import app
from app.models import *

db.create_all()
moment = Moment(app)


@app.route('/')
@app.route('/home')
def home():
    username = None
    if request.cookies.get("username"):
        username = request.cookies.get("username")
    page = request.args.get('page', 1, type=int)
    per_page = 5  # current_app.config['PERSONALBLOG_POST_PER_PAGE']
    pagination = Blog.query.order_by(Blog.timestamp.desc()).paginate(page, per_page=per_page)
    blogs = pagination.items
    return render_template('index.html', username=username, blogs=blogs, pagination=pagination)


@app.route('/signIn', methods=['POST', 'GET'])
def signin():
    error = None
    if request.method == 'POST':
        username = request.form['userid']
        password = request.form['psw']
        user = User.query.filter(and_(User.username == username)).first()
        if user:
            psd = check_password_hash(user.password_hash, password)
            if psd:
                temp = render_template('result.html')
                resp = make_response(temp)
                resp.set_cookie("username", username)
                app.logger.info(username + ' sign in successfully.')
                return resp
            else:
                app.logger.warning('type in wrong password for' + username)
                error = 'Wrong password!'
        else:
            error = 'Wrong username!'
    return render_template('signin.html', error=error)


@app.route('/signUp', methods=['POST', 'GET'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['userid']
        telnum = request.form['usrtel']
        email = request.form['email']
        age = request.form['age']
        password = request.form['psw']
        # print(username + telnum + email + age + password)
        user = User.query.filter(or_(User.username == username)).first()
        emailif = User.query.filter(or_(User.email == email)).first()
        telif = User.query.filter(or_(User.tel == telnum)).first()
        if not user:
            if not emailif:
                if not telif:
                    if len(username) >= 3 or len(username) <= 60:
                        if len(password) >= 6 or len(password) <= 99:
                            newuser = User(username=username, email=email, age=age, tel=telnum)
                            newuser.password_hash = generate_password_hash(password)
                            db.session.add(newuser)
                            db.session.commit()
                            app.logger.debug("A new user has been added.")
                            app.logger.info(username + ' sign up successfully.')
                            return redirect(url_for('signin'))
                        else:
                            error = 'The password is too short or too long!'
                    else:
                        error = 'The username is too short or too long!'
                else:
                    error = 'The phone number has been signed!'
            else:
                error = 'The email address has been signed!'
        else:
            error = 'The username has been signed!'
    return render_template('signup.html', error=error)


@app.route('/blogs/<blog_title>', methods=['POST', 'GET'])
def show_post(blog_title):
    username = None
    if request.cookies.get("username"):
        username = request.cookies.get("username")
    blog = Blog.query.filter(Blog.title == blog_title).first()
    comments = Comment.query.filter(and_(Comment.blog_title == blog_title)).all()
    # commenters = Commenter.query.filter(and_(Commenter.id == comments.commenter_id)).all()
    return render_template('single.html', username=username, blog=blog, comments=comments)


@app.route('/write_comment/<blog_title>', methods=['POST', 'GET'])
def write_comment(blog_title):
    username = None
    if request.cookies.get("username"):
        username = request.cookies.get("username")
    if request.method == 'POST':
        if username:
            message = request.form['message']
            blog = Blog.query.filter(and_(Blog.title == blog_title)).first()
            blog.num = blog.num + 1
            db.session.add(blog)
            db.session.commit()
            app.logger.debug("The number of comment of " + blog_title + " has been increased.")
            commenter = Commenter.query.filter(and_(Commenter.commenter == username)).first()
            if not commenter:
                commenter = Commenter(commenter=username)
                db.session.add(commenter)
                db.session.commit()
                app.logger.debug("A new commenter of " + blog_title + " has been added.")
            blog.commenter.append(commenter)
            time = datetime.now()
            comment = Comment(commenter=commenter.commenter, blog_title=blog_title, comment=message, timestamp=time)
            db.session.add(comment)
            db.session.commit()
            app.logger.debug("A new comment of " + blog_title + "has been added.")
            flash("Add comment successfully!")
            app.logger.info(username + ' write comment to ' + blog_title)
            return redirect(url_for('show_post', blog_title=blog_title))
        else:
            flash("You need to sign in firstly!")
            return redirect(url_for('show_post', blog_title=blog_title))


@app.route('/my_blog')
def show_my_blog():
    username = None
    if request.cookies.get("username"):
        username = request.cookies.get("username")
    page = request.args.get('page', 1, type=int)
    per_page = 5  # current_app.config['PERSONALBLOG_POST_PER_PAGE']
    pagination = Blog.query.filter(and_(Blog.username == username)).order_by(Blog.timestamp.desc()).paginate(page,
                                                                                                             per_page=per_page)
    blogs = pagination.items
    return render_template('my_blog.html', username=username, blogs=blogs, pagination=pagination)


@app.route('/write_blog', methods=['POST', 'GET'])
def write_blog():
    username = None
    error = None
    if request.cookies.get("username"):
        username = request.cookies.get("username")
    if not username:
        error = "You have not signed in!"
    elif request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if not title:
            error = "Title can not be null!"
        elif not body:
            error = "Body can not be null!"
        else:
            oldtitle = Blog.query.filter(or_(Blog.title == title)).first()
            if oldtitle:
                error = "The title has been used, please change it!"
            else:
                time = datetime.now()
                blog = Blog(title=title, body=body, username=username, timestamp=time)
                db.session.add(blog)
                db.session.commit()
                flash("Write blog successfully!")
                app.logger.debug("A new blog has been added.")
                app.logger.info(username + ' write a new blog successfully.')
                return redirect(url_for('show_my_blog'))
    return render_template('write_blog.html', username=username, error=error)


@app.route('/my_info')
def my_info():
    username = None
    if request.cookies.get("username"):
        username = request.cookies.get("username")
    user = User.query.filter(or_(User.username == username)).first()
    return render_template('my_info.html', username=username, user=user)


@app.route('/change_psw', methods=['POST', 'GET'])
def change_psw():
    error = None
    if request.method == 'POST':
        username = request.form['userid']
        old_psw = request.form['old_psw']
        new_psw = request.form['new_psw']
        user = User.query.filter(and_(User.username == username)).first()
        if user:
            psd = check_password_hash(user.password_hash, old_psw)
            if not psd:
                error = "Wrong old password for the username!"
                app.logger.warning(username + 'type in wrong old password.')
            else:
                user.password_hash = generate_password_hash(new_psw)
                db.session.add(user)
                db.session.commit()
                app.logger.debug("A user's password has been changed.")
                app.logger.info(username + ' has changed the password.')
                return redirect(url_for('home'))
        else:
            error = "Wrong username!"
    return render_template('change_psw.html', error=error)


@app.route('/search', methods=['POST', 'GET'])
def search():
    username = None
    num = None
    blogs = None
    pagination = None
    if request.cookies.get("username"):
        username = request.cookies.get("username")
    if request.method == 'POST':
        search_word = request.form['search']
        if search_word == '':
            return redirect(url_for('home'))
        elif search_word.isspace():
            return redirect(url_for('home'))
        else:
            num = Blog.query.filter(and_(Blog.title.contains(search_word))).count()
            page = request.args.get('page', 1, type=int)
            per_page = 5  # current_app.config['PERSONALBLOG_POST_PER_PAGE']
            pagination = Blog.query.filter(and_(Blog.title.contains(search_word))).order_by(Blog.timestamp.desc()).paginate(
                page, per_page=per_page)
            blogs = pagination.items
    return render_template('search.html', username=username, blogs=blogs, num=num,  pagination=pagination)


@app.route('/logOut')
def logout():
    temp = render_template('logOut.html')
    resp = make_response(temp)
    resp.delete_cookie("username")
    app.logger.info('The user has logged out.')
    return resp


@app.route('/blog_delete/<blog_title>', methods=['POST', 'GET'])
def blog_delete(blog_title):
    if request.method == 'POST':
        blog = Blog.query.filter(and_(Blog.title == blog_title)).first()
        comments = Comment.query.filter(and_(Comment.blog_title == blog_title)).all()
        for comment in comments:
            db.session.delete(comment)
            db.session.commit()
        for commenter in blog.commenter:
            blog.commenter.remove(commenter)
        db.session.delete(blog)
        db.session.commit()
        flash("Delete successfully!")
        app.logger.debug('A blog has been deleted.')
        app.logger.info('A blog has been deleted.')
    return redirect(url_for('show_my_blog'))


@app.route('/comment_delete/<comment_id>', methods=['POST', 'GET'])
def comment_delete(comment_id):
    blog_title = None
    if request.method == 'POST':
        comment = Comment.query.filter(and_(Comment.id == comment_id)).first()
        blog_title = comment.blog_title
        blog = Blog.query.filter(and_(Blog.title == blog_title)).first()
        blog.num = blog.num - 1
        db.session.add(blog)
        db.session.commit()
        db.session.delete(comment)
        db.session.commit()
        flash("Delete comment successfully!")
        app.logger.debug('A comment has been deleted.')
        app.logger.info('A comment has been deleted.')
    return redirect(url_for('show_post', blog_title=blog_title))
