import os
import urllib2
import webapp2
import time
from google.appengine.api import images
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
#from time import strftime
from google.appengine.api import urlfetch

import sys
sys.path.insert(0, 'libs')

from bs4 import BeautifulSoup

# --- Datastore declarations --- #
 
class Post(db.Model):
	uploaded_by = db.UserProperty(required=True)		
	title = db.StringProperty(required=True)
	body = db.TextProperty()
	url = db.LinkProperty()
	tags = db.StringListProperty(required=True)
	posted = db.DateTimeProperty(required=True, auto_now_add=True)
	answered = db.BooleanProperty(default=False)
	type = db.StringProperty(required=True)
	comments = db.IntegerProperty(default=0)

class Comment(db.Model):
	posted_by = db.UserProperty(required=True)
	body = db.TextProperty(required=True)
	parent_post = db.IntegerProperty(required=True)	
	parent_comment = db.IntegerProperty()
	posted = db.DateTimeProperty(required=True, auto_now_add=True)
	
class LearnUsers(db.Model):
	pass

# --- End Datastore Declarations --- #


class MainHandler(webapp2.RequestHandler):
	def get(self):		
		
		user = users.get_current_user()	
		
		posts_title = 'Latest'		
		
		html = template.render('templates/index.html', {'posts_title': posts_title, 'user': user, 'logout_url': users.create_logout_url('/')})	
			
		posts = Post.all().fetch(1000)	
		#query().order

		html += template.render('templates/posts.html', {'posts':posts})
		html += template.render('templates/footer.html', {})
		self.response.write(html)
#		else:
			#self.redirect(users.create_login_url(self.request.uri))
			

			
class WritePost(webapp2.RequestHandler):
	def get(self):
		
		type = self.request.get('type')
		
		user = users.get_current_user()
		
		if user:
			html = template.render('templates/index.html', {'user': user, 'logout_url': users.create_logout_url('/')})
			if type == 'link':
				html += template.render('templates/make-link.html', {})
			elif type == 'post':
				html += template.render('templates/make-post.html', {})
			elif type == 'question':
				html += template.render('templates/make-question.html', {})
			html += template.render('templates/footer.html', {})
			self.response.write(html)			
		else:
			self.redirect(users.create_login_url(self.request.uri))
		
class MakePost(webapp2.RequestHandler):
	def post(self):
		
		type = self.request.get('type')		
		
		post_title = self.request.get('title',default_value='') 
		post_body = self.request.get('body',default_value='') 
		post_tags = self.request.get('tags',default_value='').lower().split()

		if type == 'link':
			url = post_title
			response = urllib2.urlopen(url)
			html = response.read()	
			soup = BeautifulSoup(html)		
			title = str(soup.title.string)
			post_info = Post(type=type, title=title, body=post_body, tags=post_tags, uploaded_by=users.get_current_user(), url=url)
		else:
			post_info = Post(type=type, title=post_title, body=post_body, tags=post_tags, uploaded_by=users.get_current_user())	
		
		db.put(post_info)
		
		time.sleep(3) # wait for 3s to allow for entry to be added so it displays on redirect
		
		self.redirect('/')

class AddComment(webapp2.RequestHandler):
	def post(self):
		
		#consider setting boolean hasChildren to each postcomment
		user = users.get_current_user()
		body = self.request.get('body')	
		parent = long(self.request.get('parent', default_value=1))
		parent_comment = long(self.request.get('parent_comment', default_value=1))		
		comment_info = Comment(posted_by=user, body=body, parent_post=parent, parent_comment=parent_comment)
		db.put(comment_info)
		post = Post.get_by_id(parent)
		comments = post.comments +1
		post.comments = comments 
		post.put()
		time.sleep(3)
		self.redirect('/view?post=' + str(parent))
		
class ViewPost(webapp2.RequestHandler):
	def get(self):
		post_id = long(self.request.get('post'))

		posts = Post.all()

		post = Post.get_by_id(post_id)
		user = users.get_current_user()
		
		html = template.render('templates/index.html', {'posts_title': post.title, 'user': user, 'logout_url': users.create_logout_url('/')})
		
		comments = Comment.all().filter('parent_post =', post.key().id()).fetch(1000)
		
		html += template.render('templates/view.html', {'post':post, 'comments':comments})

				
		html += template.render('templates/footer.html', {})
		self.response.write(html)
		
class Unanswered(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()		
		
		posts_title = 'Unanswered'		
		post_type = 'question'
		
		html = template.render('templates/index.html', {'posts_title': posts_title, 'user': user, 'logout_url': users.create_logout_url('/')})	
		#watch the space before = it is needed
		posts = Post.all().filter('type =', post_type).filter('answered =', False).fetch(10000)
		
		html += template.render('templates/posts.html', {'posts':posts})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)

class ViewTags(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		posts_title = "Tags"
		
		html = template.render('templates/index.html', {'posts_title': posts_title, 'user': user, 'logout_url': users.create_logout_url('/')})
		
		posts = Post.all().fetch(1000)
		
		tags = []
		
		for post in posts:
			for tag in post.tags:
				if tag not in tags:
					tags.append(tag)		
		
		html += template.render('templates/tags.html', {'tags':tags})
		
		html += template.render('templates/footer.html', {})
		self.response.write(html)


class ViewTag(webapp2.RequestHandler):
	def get(self):
		
		user = users.get_current_user()
		tag = self.request.get('tag')
		
		posts_title = tag
		
		html = template.render('templates/index.html', {'posts_title': posts_title, 'user': user, 'logout_url': users.create_logout_url('/')})
			
		posts = Post.all().filter('tags = ', tag)
		posts.fetch(10)
		
		html += template.render('templates/posts.html', {'posts':posts})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)

		
class Search(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		searchTerm = self.request.get('search').lower()
		
		posts_title = "Search Results"
		
		posts = Post.all().filter('tags =', searchTerm).fetch(1000)
		
		html = template.render('templates/index.html', {'posts_title': posts_title, 'user': user, 'logout_url': users.create_logout_url('/')})
		
		html += template.render('templates/posts.html', {'posts':posts})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)
		
		
class DeletePost(webapp2.RequestHandler):
	def post(self):
		pass
		
class About(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
		posts_title = "About"		
				
		html = template.render('templates/index.html', {'posts_title': posts_title, 'user': user, 'logout_url': users.create_logout_url('/')})
		
		html += template.render('templates/about.html', {})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)
		
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/post', WritePost),
							   ('/makepost', MakePost),
							   ('/comment', AddComment),
							   ('/search', Search),
							   ('/view', ViewPost),
							   ('/delete', DeletePost),							   
							   ('/unanswered', Unanswered),
							   ('/tags', ViewTags),	
							   ('/tag', ViewTag),
							   ('/about', About),							   
							   ],
                              debug=True)

