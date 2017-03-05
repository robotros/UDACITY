""" Post

Author: Aron Roberts
Version: 1.00
Date Created: 3/4/2017
filename: post.py

Last Update:
Date: 3/4/2017
DESC:

"""

import jinja2
import os

from google.appengine.ext import db
from models.user import User

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Post(db.Model):
	""" Entity class for post """
	author = db.ReferenceProperty(User, required = True, collection_name = 'posts')
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	liked_by = db.ListProperty(str)
	# implicit property comments

	def render_str(self, template, **params):
		""" renders HTML template into str """
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self):
		""" render text for more practical html """
		self._render_text = self.content.replace('\n', '<br>')
		return self.render_str("post.html", p = self)

	def get_author_name(self):
		if self.author:
			return ('%s %s' % (self.author.first_name, self.author.last_name))

	def get_likes(self):
		if self.liked_by:
			return len(self.liked_by)
		else:
			return 0