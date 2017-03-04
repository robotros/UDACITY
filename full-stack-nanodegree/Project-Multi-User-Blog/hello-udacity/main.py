""" Multi User Blog

Python webserver code to manage a multi-user blog
part of UDACITY Fullstack Nano-Degree

Author: Aron Roberts
Version: 0.92
Date Created: 3/1/2017
filename: main.py

Last Update:
Date: 3/3/2017
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
	salt = h.split(',')[1]
	if h == make_pw_hash(name, pw, salt):
		return True

# Entity Classes
class Post(db.Model):
	""" Entity class for post """
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	user = db.StringProperty()
	last_modified = db.DateTimeProperty(auto_now = True)

	def render(self):
		""" render text for more practical html """
		self._render_text = self.content.replace('\n', '<br>')
		return render_str("post.html", p = self)

	def get_author_name(self):
		if self.user:
			author_id = str(self.user)
			u = User.get_by_id(int(author_id))
			return ('%s %s' % (u.first_name, u.last_name))

class User(db.Model):
	""" Entinty class for user """
	username = db.StringProperty(required = True)
	first_name = db.StringProperty(required = False)
	last_name = db.StringProperty(required = False)
	password = db.StringProperty(required = True)
	email = db.StringProperty()

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
		cookie_val = make_secure_val(val)
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.get_by_id(int(uid))


class BlogFront(Handler):
	""" handler for front page of blog """
	def get(self):
		posts = Post.all().order('-created')
		#posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC limit 10 ")
		self.render('front.html', posts = posts)

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
			a = Post(subject = subject, content = content, user = str(self.user.key().id()))
			a.put()
			self.redirect('/blog/%s' % str(a.key().id()))
		else:
			errorMessage = "we need both subject and some content!"
			error = "has-error has-feedback" 
			self.render_new_post(subject, content, error, errorMessage)

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
	def get(self):
		self.logout();
		self.redirect('/blog/signup')

class Welcome(Handler):
	def get(self):
		if self.user:
			name = self.user.first_name+" "+self.user.last_name
			uid = str(self.user.key().id())
			
			p = Post.all().filter('user =', uid)

			self.render("welcome.html", name = name, posts = p)
		else:		
			self.redirect("/blog/login")


class MainPage(Handler):
	""" Handler for main page of Blog """
	def get(self):
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
							('/blog/welcome', Welcome)
							], 
							debug=True)