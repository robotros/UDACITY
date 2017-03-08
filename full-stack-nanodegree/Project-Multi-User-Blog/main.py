""" Multi User Blog

Python webserver code to manage a multi-user blog
part of UDACITY Fullstack Nano-Degree

Author: Aron Roberts
Version: 0.92
Date Created: 3/1/2017
filename: main.py

Last Update:
Date: 3/4/2017
DESC:

"""

import os
import webapp2
import jinja2
import hashlib
import hmac
import random
import string
import re

from google.appengine.ext import db
from models.user import User
from models.post import Post
from models.comment import Comment

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

SECRET = "Arma virumque cano, Troiae qui primus ab oris Italiam, fato profugus"


# datastore management
def delete_all_comments():
    """ clears Comment table"""
    comments = Comment.all()
    for c in comments:
        c.delete()


def delete_all_post():
    """ Clears Post table """
    posts = Post.all()
    for p in posts:
        p.delete()


def delete_all_users():
    """ Clears User table """
    users = User.all()
    for u in users:
        u.delete()


def clear_db():
    """ Clears all tables """
    delete_all_comments()
    delete_all_post()
    delete_all_users()


# Handler Classes

class Handler(webapp2.RequestHandler):
    """ A class to add default handler functionality """
    def write(self, *a, **kw):
        """ Replaces response.out.write() for simplicity """
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """ renders HTML template into str """
        t = jinja_env.get_template(template)
        return t.render(params)

    def hash_str(self, s):
        """ Hash a string """
        return hmac.new(SECRET, s, hashlib.sha256).hexdigest()

    def make_secure_val(self, s):
        """ turn string to secure value """
        return "%s|%s" % (s, self.hash_str(s))

    def check_secure_val(self, h):
        """ validate hash matches string """
        val = h.split('|')[0]
        if h == self.make_secure_val(val):
            return val

    def render(self, template, **kw):
        """ Writes out template as a str """
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        """ sets a cookie with name and val """
        cookie_val = self.make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        """ reads a cookie with name """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and self.check_secure_val(cookie_val)

    def login(self, user):
        """ sets user_id cookie for login """
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        """ removes user_id cookie """
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def verify_user_login(self):
        """ verify user is logged in """
        if not self.user:
            self.redirect("/blog/login")

    def redirect_to_dashboard(self):
        """ redirects to welcome page """
        self.redirect("/blog/welcome")

    def retrieve_post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not post:
            self.error(404)
        else:
            return post

    def initialize(self, *a, **kw):
        """ verify login status using cookie """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.get_by_id(int(uid))


# Registration and Login | Logout Handlers
class Registration(Handler):
    """ Handler for signup page """

    def valid_username(self, username):
        """ validate username """
        user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return username and user_re.match(username)

    def valid_pw(self, pw):
        """ validate password """
        pass_re = re.compile(r"^.{3,20}$")
        return pw and pass_re.match(pw)

    def valid_email(self, email):
        """ validate email """
        email_re = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
        return email and email_re.match(email)

    def get(self):
        if self.user:
                self.redirect_to_dashboard()

        self.render("signup.html")

    def post(self):
        error_flag = False
        error = "has-error has-feedback"
        username = self.request.get("username").lower()
        first_name = self.request.get("first_name")
        last_name = self.request.get("last_name")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email").lower()

        params = dict(username=username,
                      first_name=first_name,
                      last_name=last_name,
                      email=email)

        # check username for errors
        if not self.valid_username(username):
            error_flag = True
            params['error_user'] = error
            params['error_user_msg'] = "Invalid username, username must be 3 - 20 characters in length"
        elif User.by_username(username):
            error_flag = True
            params['error_user'] = error
            params['error_user_msg'] = "username already exsists"

        # check password for errors
        if not self.valid_pw(password):
            error_flag = True
            params['error_pw'] = error
            params['error_pw_msg'] = "Invalid password, password must be 3 - 20 characters in length"
        elif password != verify:
            error_flag = True
            params['error_pw'] = error
            params['error_pw_msg'] = "Passwords did not match"

        # check email for errors
        if email and not self.valid_email(email):
            error_flag = True
            params['error_email'] = error
            params['error_email_msg'] = "Invalid email"

        if error_flag:
            self.render('signup.html', **params)
        else:
            # create new user
            u = User(username=username,
                     first_name=first_name,
                     last_name=last_name,
                     password=User.make_pw_hash(username, password),
                     email=email)
            u.put()

            # log new user in and redirect to welcome
            self.login(u)
            self.redirect_to_dashboard()


class Login(Handler):
    """ Handler for login """
    def get(self):
        if self.user:
            self.redirect_to_dashboard()

        self.render('login-form.html')

    def post(self):
        username = self.request.get('username').lower()
        password = self.request.get('password')

        params = dict(username=username)

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect_to_dashboard()
        else:
            params['error_msg'] = "invalid login : username or password is incorrect"
            self.render('login-form.html', **params)


class Logout(Handler):
    """ Handler for logout """
    def get(self):
        self.logout()
        self.redirect("/blog/login")


# Blog Handlers
class BlogFront(Handler):
    """ handler for front page of blog """
    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts=posts, user=self.user)


class Welcome(Handler):
    """ Handler for user dashboard """
    def get(self):
        if self.user:

            # get post made by user
            posts = self.user.posts
            likes = 0

            # calculate total likes for all posts
            for p in posts:
                likes = likes + p.likes

            self.render("welcome.html",
                        user=self.user,
                        posts=posts,
                        likes=likes)
        else:
            self.redirect("/blog/login")


class PostPage(Handler):
    """ handler for individual post """
    def get(self, post_id):

        # retrieve post
        post = self.retrieve_post(post_id)
        if not post:
            return

        self.render("permalink.html", user=self.user, post=post)


class NewPost(Handler):
    """ Handler for inputing new post """
    def get(self):
        if self.user:
            self.render("newpost.html", user=self.user)
        else:
            self.redirect("/blog/login")

    def post(self):
        # verify user is logged in
        self.verify_user_login()

        # retrieve post subject and content
        subject = self.request.get("subject")
        content = self.request.get("content")

        params = dict(subject=subject, content=content, user=self.user)

        # error checking
        error_flag = False
        error = "has-error has-feedback"

        # check for subject error
        if not subject:
            error_flag = True
            params['error_subj'] = error
            params['error_subj_msg'] = "A subject is required"

        # check for content error
        if not content:
            error_flag = True
            params['error_con'] = error
            params['error_con_msg'] = "Content is required"

        if error_flag:
            self.render("newpost.html", **params)
        else:
            p = Post(subject=subject, content=content, author=self.user)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))


class LikePost(Handler):
    """ Handler to like post """
    def post(self, post_id):
        # verify user is logged in
        self.verify_user_login()

        # retrieve post
        post = self.retrieve_post(post_id)
        if not post:
            return

        liked_by = post.liked_by

        # get logged in users id and username
        uid = str(self.user.key().id())
        username = self.user.username

        # check is user is post author or previously liked the post
        if username != post.author.username and uid not in post.liked_by:
            post.liked_by.append(uid)
            post.put()

        self.redirect('/blog/%s' % str(post_id))


class UpdatePost(Handler):
    """ Handler to update a post """
    def get(self, post_id):
        # verify user is logged in
        self.verify_user_login()

        # retrieve post
        post = self.retrieve_post(post_id)
        if not post:
            return

        # verify logged in user is post author
        if self.user.username == post.author.username:
            params = dict(user=self.user,
                          post=post,
                          subject=post.subject,
                          content=post.content)
            self.render("updatepost.html", **params)
        else:
            self.redirect_to_dashboard()

    def post(self, post_id):
        # verify user is logged in
        self.verify_user_login()

        # retrieve post
        post = self.retrieve_post(post_id)
        if not post:
            return

        # verify logged in user is post author
        if self.user.username != post.author.username:
            self.redirect_to_dashboard()

        # get subject and content
        subject = self.request.get("subject")
        content = self.request.get("content")

        params = dict(subject=subject, content=content, user=self.user)

        # error checking and validation
        error_flag = False
        error = "has-error has-feedback"

        # check for subject error
        if not subject:
            error_flag = True
            params['error_subj'] = error
            params['error_subj_msg'] = "A subject is required"

        # check for content error
        if not content:
            error_flag = True
            params['error_con'] = error
            params['error_con_msg'] = "Content is required"

        if error_flag:
            self.render("newpost.html", **params)
        else:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))


class DeletePost(Handler):
    def post(self, post_id):
        # verify user is logged in
        self.verify_user_login()

        # retrieve post
        post = self.retrieve_post(post_id)
        if not post:
            return

        # verify logged in user is post author
        if post.author.username == self.user.username:
            post.delete()

        self.redirect_to_dashboard()


class NewComment(Handler):
    def get(self, post_id):
        self.verify_user_login()

        # retrieve post
        post = self.retrieve_post(post_id)
        if not post:
            return

        self.render("newcomment.html", user=self.user, post=post)

    def post(self, post_id):
        self.verify_user_login()

        # retrieve post
        post = self.retrieve_post(post_id)
        if not post:
            return

        # create comment
        comment = self.request.get('comment')

        if comment:
            c = Comment(comment=comment, post=post, author=self.user)
            c.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            self.render("newcomment.html", user=self.user, post=post)


class DeleteComment(Handler):
    def post(self, comment_id):
        self.verify_user_login()

        comment = Comment.get_by_id(int(comment_id))

        if comment and comment.author.username == self.user.username:
            comment.delete()
            self.redirect('/blog/')
        else:
            self.redirect('/blog')


class MainPage(Handler):
    """ Handler for main page of Blog """
    def get(self):

        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        visit_cookie_str = self.request.cookies.get('visits', '0')
        if visit_cookie_str:
                cookie_val = self.check_secure_val(visit_cookie_str)
                if cookie_val:
                    visits = int(cookie_val)

        visits += 1

        new_cookie_val = self.make_secure_val(str(visits))
        self.response.headers.add_header('Set-Cookie',
                                         'visits=%s' % new_cookie_val)

        self.write("You've been here %s times" % visits)

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/blog/?', BlogFront),
                              ('/blog/([0-9]+)', PostPage),
                              ('/blog/newpost', NewPost),
                              ('/blog/signup', Registration),
                              ('/blog/login', Login),
                              ('/blog/logout', Logout),
                              ('/blog/welcome', Welcome),
                              ('/blog/([0-9]+)/newcomment', NewComment),
                              ('/blog/deletecomment/([0-9]+)', DeleteComment),
                              ('/blog/deletepost/([0-9]+)', DeletePost),
                              ('/blog/updatepost/([0-9]+)', UpdatePost),
                              ('/blog/likepost/([0-9]+)', LikePost)],
                              debug=True)
