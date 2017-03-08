**Table of Contents** 

- [PROJECT](#project)
	- [Multi-User-Blog](#multi-user-blog)
		- [Description](#description)
		- [What is Included](#what-is-included)
		- [Dependencies](#dependencies)
		- [Quickstart](#quickstart)
		- [Footnotes](#footnotes)


# **PROJECT **
## Multi-User-Blog

### Description

Multi-user Blog built on Google app engine
users can register and login and view post.
logged in users can logout write and edit post
like and comment posts.

users cannot like their own post or delete other users post.

### What is Included

* main.py
* app.yaml
* /models/user.py
* /models/post.py
* /models/comment.py
* /templates/base.html
* /templates/front.html
* /templates/login-form.html
* /templates/newcomment.html
* /templates/newpost.html
* /templates/permalink.html
* /templates/post.html
* /templates/signup.html
* /templates/updatepost.html
* /templates/welcome.html
* static/main.css
* README.MD

### Dependencies

The following will be required to run this program

1. [Python 2.7](https://www.python.org/downloads/release/python-2710/)
2. [Google App Engine](https://cloud.google.com/appengine/)
3. modern browser

### Quickstart

1. Open google SDk Shell in working directory
2. run command `dev_appserver.py .`
3. open localhost:8080/blog in browser



### Footnotes

* Project Requirements can be found at [UDACITY.com](http://www.UDACITY.com/)
* Project can be found running at [Google Ap Enging](https://hello-world-158219.appspot.com/blog/)
