import os
import urllib2
import webapp2
import time
from google.appengine.api import images
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import urlfetch


import sys
sys.path.insert(0, 'libs')

from bs4 import BeautifulSoup


# --- Datastore declarations --- #
 
class Post(db.Model):
	uploaded_by = db.UserProperty(required=True)		
	title = db.StringProperty(required=True, multiline=True)
	body = db.TextProperty()
	url = db.LinkProperty()
	tags = db.StringListProperty(required=True)
	posted = db.DateTimeProperty(required=True, auto_now_add=True)
	answered = db.BooleanProperty(default=False)
	type = db.StringProperty(required=True)
	comments = db.IntegerProperty(default=0)
	likes = db.IntegerProperty(default=0)
	liked_by = db.StringListProperty()

class Comment(db.Model):
	posted_by = db.UserProperty(required=True)
	body = db.TextProperty(required=True)
	parent_post = db.IntegerProperty(required=True)	
	parent_comment = db.IntegerProperty()
	posted = db.DateTimeProperty(required=True, auto_now_add=True)
	likes = db.IntegerProperty(default=0)
'''	
class User(db.Model):
	username = db.StringProperty(required=True)
	#isbanned = db.BooleanProperty(default=False)
	#isadmin = db.BooleanProperty(default=False)
	#userID =  db.IntegerProperty(default=0)
	#avatar = db.BlobProperty()
	password = db.StringProperty(required=True)

'''
# --- End Datastore Declarations --- #


def MakeIndex(self, title):
	

	user = users.get_current_user()	
		
	posts_title = title
	
	html = template.render('templates/index.html', {'posts_title': posts_title, 'user': user, 'logout_url': users.create_logout_url('/'), 'login_url': users.create_login_url(self.request.uri),'sideposts':GetLatestPosts(5), 'latesttags':GetLatestTags(10)})	
	
	return html

def GetLatestPosts(num):
	posts = Post.all().order('-posted').fetch(num)
	return posts

def GetLatestTags(num):
	
	posts = GetLatestPosts(num)
	
	tags = []
		
	for post in posts:
		for tag in post.tags:
			if tag not in tags:
				tags.append(tag)
	return tags

class MainHandler(webapp2.RequestHandler):
	def get(self):		
		
		user = users.get_current_user()	
		
		posts_title = 'Latest'	

		html = MakeIndex(self, 'Latest')			

		html += template.render('templates/posts.html', {'posts':GetLatestPosts(1000)})
		html += template.render('templates/footer.html', {})
		self.response.write(html)

			
class WritePost(webapp2.RequestHandler):
	def get(self):
		
		type = self.request.get('type')
		
		user = users.get_current_user()
		
		if user:
			html = MakeIndex(self, 'Make a ' + type)
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
		
		user = users.get_current_user()
		
		type = self.request.get('type')		
		
		post_title = self.request.get('title',default_value='').lstrip()
		post_body = self.request.get('body',default_value='') 
		post_tags = self.request.get('tags',default_value='').lower().split()

		if type == 'link':
			url = post_title
			response = urllib2.urlopen(url)
			html = response.read()	
			soup = BeautifulSoup(html)		
			title = str(soup.title.string).lstrip()
			post_info = Post(type=type, title=title, body=post_body, tags=post_tags, uploaded_by=users.get_current_user(), url=url)
		else:
			post_info = Post(type=type, title=post_title, body=post_body, tags=post_tags, uploaded_by=users.get_current_user())	
		
		db.put(post_info)
		
		time.sleep(3) # wait for 3s to allow for entry to be added so it displays on redirect
		
		posts = Post.all().filter('uploaded_by =', user).order('-posted').fetch(1000)
		
		
		self.redirect('/view?post=' + str(posts[0].key().id()))

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
		
		html = MakeIndex(self, post.title)
		
		comments = Comment.all().filter('parent_post =', post.key().id()).fetch(1000)
		
		html += template.render('templates/view.html', {'post':post, 'comments':comments})

				
		html += template.render('templates/footer.html', {})
		self.response.write(html)
		
class Unanswered(webapp2.RequestHandler):
	def get(self):
			
		post_type = 'question'
		
		html = MakeIndex(self, 'Unanswered')
		#watch the space before = it is needed
		posts = Post.all().filter('type =', post_type).filter('answered =', False).order('-posted').fetch(10000)
		
		html += template.render('templates/posts.html', {'posts':posts})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)

class ViewTags(webapp2.RequestHandler):
	def get(self):
		
		html = MakeIndex(self, 'Tags')
		
		posts = Post.all().order('-posted').fetch(1000)
		
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
		
		tag = self.request.get('tag')
		
		html = MakeIndex(self, tag)
			
		posts = Post.all().filter('tags = ', tag).order('-posted').fetch(10)
		
		html += template.render('templates/posts.html', {'posts':posts})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)

		
class Search(webapp2.RequestHandler):
	def post(self):
		
		searchTerm = self.request.get('search').lower()		
	
		posts = Post.all().filter('tags =', searchTerm).order('-posted').fetch(1000)
		
		html = MakeIndex(self, 'Results')
		
		html += template.render('templates/posts.html', {'posts':posts})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)
		
		
class DeletePost(webapp2.RequestHandler):
	def post(self):
		pass

class MyQuestions(webapp2.RequestHandler):
	def get(self):

		user=users.get_current_user()
		
		posts = Post.all().filter('uploaded_by =', user).order('-posted').fetch(1000)
		
		html = MakeIndex(self, 'My Questions')
		
		html += template.render('templates/posts.html', {'posts':posts})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)

class AddLike(webapp2.RequestHandler):
	def get(self):
		id = long(self.request.get('id'))		
		
		user = users.get_current_user()
		
		post = Post.get_by_id(id)
		
		if user.user_id() in post.liked_by:
			pass
		else:
			post.likes += 1
			post.liked_by.append(user.user_id())
			post.put()
		'''elif type == 'comment':
			comment = Comment.get_by_id(id)	
			comment.likes += 1
			comment.put()'''
		self.redirect(self.request.referer)
		
class About(webapp2.RequestHandler):
	def get(self):
			
		html = MakeIndex(self, 'About')
		
		html += template.render('templates/about.html', {})
		
		html += template.render('templates/footer.html', {})
		
		self.response.write(html)
'''
class Register(webapp2.RequestHandler):
	def get(self):
		html = MakeIndex(self, 'Register')
		html += template.render('templates/register.html', {})
			
		html += template.render('templates/footer.html', {})
			
		self.response.write(html)
	def post(self):
		username = self.request.get('username',default_value='') 
		password = self.request.get('password',default_value='') 
		
		users = User.all().fetch(1000)
		
		for item in users:		
			if username == item.username:		
				self.redirect('/')
				
		user = User(username=username, password=password)		
		db.put(user)
		
		self.redirect('/')
'''
		
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/post', WritePost),
							   ('/makepost', MakePost),
							   ('/comment', AddComment),
							   ('/search', Search),
							   ('/view', ViewPost),
							   ('/delete', DeletePost),							   
							   ('/unanswered', Unanswered),
							   ('/myquestions', MyQuestions),
							   ('/tags', ViewTags),	
							   ('/tag', ViewTag),
							   #('/register', Register),
							   ('/like', AddLike),
							   ('/about', About),							   
							   ],
                              debug=True)

