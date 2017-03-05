""" User

Author: Aron Roberts
Version: 1.00
Date Created: 3/4/2017
filename: user.py

Last Update:
Date: 3/4/2017
DESC:

"""

import hashlib
import hmac
import random
import string

from google.appengine.ext import db

SECRET = "Arma virumque cano, Troiae qui primus ab oris Italiam, fato profugus"
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
	def make_salt(cls, n=5):
		""" returns generated salt """
		return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))

	@classmethod
	def make_pw_hash(cls, name, pw, salt=""):
		""" Make a storable hash of the password """
		# check if salt param set
		if not salt:
			salt = cls.make_salt()

		# convert key and msg from unicdoe str to byte str
		key = bytearray(salt+SECRET, 'utf-8')
		msg = bytearray(name+pw, 'utf-8')

		# create hash
		h = hmac.new(key, msg, hashlib.sha256).hexdigest()

		#return hmac.new(salt+SECRET, name+pw, hashlib.sha256).hexdigest()+','+salt
		return "%s,%s" % (h, salt)

	@classmethod
	def valid_pw(cls, username, pw, h):
		salt = h.split(',')[1]
		if h == cls.make_pw_hash(username, pw, salt):
			return True

	@classmethod
	def login(cls, username, pw):
		u = cls.by_username(username)
		#if u and valid_pw(username, pw, u.password):
		if u and cls.valid_pw(username, pw, u.password):
			return u 