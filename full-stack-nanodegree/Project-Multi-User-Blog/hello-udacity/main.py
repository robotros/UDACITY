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

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)
SECRET = "Arma virumque cano"

def render_str(template, **params):
	""" renders HTML template into str """
	t = jinja_env.get_template(template)
	return t.render(params)

def hash_str(s):
	""" Hash a string """
	return hmac.new(SECRET, s, hashlib.sha256).hexdigest()

def make_secure_val(s):
	""" turn string to secure value """
	return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
	""" validate hash matches string """
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

def make_salt(n=5):
	""" returns generated salt """
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))

def make_pw_hash(name, pw, salt=""):
	""" Make a storable hash of the password """
	# check if salt param set
	if not salt:
		salt = make_salt()

	# convert key and msg from unicdoe str to byte str
	key = bytearray(salt+SECRET, 'utf-8')
	msg = bytearray(name+pw, 'utf-8')

	# create hash
	h = hmac.new(key, msg, hashlib.sha256).hexdigest()

	#return hmac.new(salt+SECRET, name+pw, hashlib.sha256).hexdigest()+','+salt
	return "%s,%s" % (h, salt)

def valid_pw(name, pw, h):
	""" validates user password """
	salt = h.split(',')[1]
	if h == make_pw_hash(name, pw, salt):
		return True

def delete_all_post():
 	posts = Post.all()
	for p in posts:
		p.delete()


# Entity Classes
class User(db.Model):
	""" Entinty class for user """
	username = db.StringProperty(required = True)
	first_name = db.StringProperty(required = False)
	last_name = db.StringProperty(required = False)
	password = db.StringProperty(required = True)
	email = db.StringProperty()
	# implicit Property posts
	# implicit property comments

	@classmethod
	def by_id(cls, uid):
		return cls.get_by_id(uid)

	@classmethod
	def by_username(cls, username):
		u = cls.all().filter('username =', username).get()
		return u

	@classmethod
	def login(cls, username, pw):
		u = cls.by_username(username)
		if u and valid_pw(username, pw, u.password):
			return u 


class Post(db.Model):
	""" Entity class for post """
	author = db.ReferenceProperty(User, required = True, collection_name = 'posts')
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	liked_by = db.ListProperty(str)
	# implicit property comments

	def render(self):
		""" render text for more practical html """
		self._render_text = self.content.replace('\n', '<br>')
		return render_str("post.html", p = self)

	def get_author_name(self):
		if self.author:
			return ('%s %s' % (self.author.first_name, self.author.last_name))

	def get_likes(self):
		if self.liked_by:
			return len(self.liked_by)
		else:
			return 0

class Comment(db.Model):
	""" Entity class for Comment """
	post = db.ReferenceProperty(Post, required = True, collection_name = 'comments')
	author = db.ReferenceProperty(User, required = True, collection_name = 'comments')
	comment = db.StringProperty(required = True)

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

	def render(self, template, **kw):
		""" Writes out template as a str """
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		""" sets a cookie with name and val """
		cookie_val = make_secure_val(val)
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		""" reads a cookie with name """
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		""" sets user_id cookie for login """
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		""" removes user_id cookie """
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		""" verify login status using cookie """
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.get_by_id(int(uid))

# Registration and Login | Logout Handlers
class Registration(Handler):
	""" Handler for signup page """
	def render_signup(self, username="", first_name="", last_name="", password="", verify="", email="", error="", errorMessage=""):
		self.render("signup.html", username = username, first_name = first_name, last_name = last_name, 
			password = password, verify = verify, email = email, error=error, errorMessage=errorMessage)

	def get(self):
		if self.user:
				self.redirect("/blog/welcome")

		self.render_signup()

	def post(self):
		username = self.request.get("username")
		first_name = self.request.get("first_name")
		last_name = self.request.get("last_name")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		if username and password and verify == password:
			u = User.by_username(username)
			if u:
				errorMessage = "User Already Exsist"
				self.render_signup(errorMessage=errorMessage)
			else:
				a = User(username = username, first_name = first_name,
					last_name = last_name, password = make_pw_hash(username, password), 
					email = email)
				a.put()
				self.login(a)
				self.redirect('/blog/')
		elif password != verify:
			errorMessage = "Passwords did not match"
			self.render_signup(username,first_name, last_name, "", "", email , error, errorMessage)
		else:
			errorMessage = "please complete required fields"
			error ="has-error has-feedback"
			self.render_signup(username,first_name, last_name, "", "", email , error, errorMessage)

class Login(Handler):
	""" Handler for login """
	def get(self):
		if self.user:
			self.redirect("/blog/welcome")
		
		self.render('login-form.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		u = User.login(username, password)
		if u:
			self.login(u)
			self.redirect('/blog')
		else:
			errorMessage = "invalid login"
			self.render('login-form.html', errorMessage = errorMessage)

class Logout(Handler):
	""" Handler for logout """
	def get(self):
		self.logout();
		self.redirect('/blog/signup')


class BlogFront(Handler):
	""" handler for front page of blog """
	def get(self):
		posts = Post.all().order('-created')
		#posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC limit 10 ")
		self.render('front.html', posts = posts)

class Welcome(Handler):
	""" Handler for user dashboard """
	def get(self):
		if self.user:
			name = self.user.first_name+" "+self.user.last_name			
			posts = self.user.posts
			likes = 0
			for p in posts:
				likes = likes + p.get_likes()

			self.render("welcome.html", name = name, posts = posts, likes = likes)
		else:		
			self.redirect("/blog/login")

class PostPage(Handler):
	""" handler for individual post """
	def get(self, post_id):
		post = Post.get_by_id(int(post_id))

		#error checking 
		if not post:
			self.error(404)
			return

		self.render("permalink.html", post = post)

class NewPost(Handler):
	""" Handler for inputing new post """
	def render_new_post(self, subject = "", content = "", error = "", errorMessage = ""):
		""" renders new post page from template """
		self.render("newpost.html", subject = subject, content = content, error = error, errorMessage = errorMessage)

	def get(self):
		if self.user:
			self.render_new_post()
		else:
			self.redirect("/blog/login")

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			a = Post(subject = subject, content = content, author = self.user)
			a.put()
			self.redirect('/blog/%s' % str(a.key().id()))
		else:
			errorMessage = "we need both subject and some content!"
			error = "has-error has-feedback" 
			self.render_new_post(subject, content, error, errorMessage)

class LikePost(Handler):
	def post(self, post_id):
		if not self.user:
			self.redirect("/blog/login")
			return

		post = Post.get_by_id(int(post_id))
		liked_by = post.liked_by
		uid = str(self.user.key().id())

		if self.user.username != post.author.username and not uid in post.liked_by:
			post.liked_by.append(uid)
			post.put()

		self.redirect('/blog/%s' % str(post_id))

class UpdatePost(Handler):
	def get(self, post_id):
		if not self.user:
			return

	def post(self, post_id):
		if not self.user:
			return

class DeletePost(Handler):
	def post(self, post_id):
		if not self.user:
			self.redirect("/blog/login")
			return

		post = Post.get_by_id(int(post_id))
		uid = str(self.user.key().id())

		if post.author.username == self.user.username:
			post.delete()
			self.redirect('/blog/welcome')
		else:
			self.redirect('/blog/welcome')

class NewComment(Handler):
    def get(self, post_id):
        if not self.user:
            self.redirect("/blog/login")
            return
        
        post = Post.get_by_id(int(post_id))
        
        self.render("newcomment.html", post = post)

    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        
        if not post:
            self.error(404)
            return
       
        if not self.user:
            self.redirect('login')

        # create comment
        comment = self.request.get('comment')
        uid = str(self.user.key().id())
        if comment:
            c = Comment(comment = comment, post = post_id, user = uid)
            c.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            self.render("newcomment.html", post = post)

class DeleteComment(Handler):
    def get(self, comment_id):

        comment = Comment.get_by_id(int(comment_id))
        uid = str(self.user.key().id())
        if comment and comment.user == uid:
            comment.delete()
            self.redirect('/blog/')
        else:
            self.redirect('/blog')


class MainPage(Handler):
	""" Handler for main page of Blog """
	def get(self):
		delete_all_post()

		self.response.headers['Content-Type'] = 'text/plain'
		visits = 0
		visit_cookie_str = self.request.cookies.get('visits', '0')
		if visit_cookie_str:
				cookie_val = check_secure_val(visit_cookie_str)
				if cookie_val:
					visits = int(cookie_val)

		visits += 1

		new_cookie_val = make_secure_val(str(visits))
		self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)

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
							('/blog/([0-9]+)/deletepost', DeletePost),
							('/blog/([0-9]+)/updatepost', UpdatePost),
							('/blog/([0-9]+)/likepost', LikePost)
							], 
							debug=True)