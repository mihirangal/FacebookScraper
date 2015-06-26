
import facebook
import MySQLdb
import pdb

class FBView:
	"""
	Retrieves data from Facebook in form of JSON
	"""
	def __init__(self, oauth):
		self.oauth=oauth

	def parse_feed(self, profile_name):
		try:
			self.graph= facebook.GraphAPI(self.oauth)
			self.profile=self.graph.get_object(profile_name)
			self.posts = self.graph.get_connections(self.profile['id'], 'posts',fields='from,message,status_type,picture,source')
			return self.posts['data']
		except facebook.GraphAPIError:
			return ""

class FBPost:
	"""
	superclass for posts
	"""
	def __init__(self,post):
		if post.has_key('message'):
			self.message=post['message'].encode('utf-8') 
		else:	 
			self.message=""
		self.user =post['from']['name'].encode('utf-8')
		self.status_type= post['status_type'].encode('utf-8')
		self.data= ""
	def get_type(self):
		return self.status_type
	def get_user(self):
		return self.user
	def get_message(self):
		return self.message
	def get_data(self):
		return self.data

class PicturePost(FBPost):
	"""
	this class is a FBPost but returns a url for picture data
	"""
	def __init__(self, post):
		FBPost.__init__(self,post)
		self.data= post['picture']
class VideoPost(FBPost):
	"""
	this class is a FBPost but returns a url for video data
	"""
	def __init__(self, post):
		FBPost.__init__(self,post)
		self.data= post['source']

class FBModel:
	def __init__(self, host,user):
		"""
		set up the tables and databases if they dont exist
		"""
		db = MySQLdb.connect(host,user)
		self.cursor= db.cursor()
		dbsql= """ CREATE DATABASE IF NOT EXISTS Facebook"""
		usesql=""" USE Facebook"""
		charsetsql= """ALTER DATABASE Facebook CHARACTER SET utf8 COLLATE utf8_unicode_ci"""
		createsql ="""CREATE TABLE IF NOT EXISTS Post(ID int NOT NULL AUTO_INCREMENT,Author varchar(255)
			NOT NULL,Message TEXT,Typ varchar(255),Data_val varchar(4096),PRIMARY KEY (ID)) """
		charsetsqltbl= """ALTER TABLE Post CONVERT TO CHARACTER SET utf8 COLLATE utf8_unicode_ci"""
		self.cursor.execute(dbsql)
		self.cursor.execute(usesql)
		self.cursor.execute(createsql)


	def add_post(self, post):
		"""
		take FBPost object and add it to databases
		"""
		insertsql= """INSERT INTO Post(Author, Message, Typ, Data_val) VALUES ('{user}', '{msg}', '{typ}', '{dataval}' )"""\
			.format(user=post.get_user().replace("'",''),msg= post.get_message().replace("'",''), typ=post.get_type().replace("'",''), dataval=post.get_data().replace("'",''))
		self.cursor.execute(insertsql)
	def get_all_posts(self):
		"""
		return all the posts
		"""
		pdb.set_trace()
		getsql= """SELECT * FROM  Post"""
		res= self.cursor.execute(getsql)
		return self.cursor.fetchall()
	def commit(self):
		"""
		finish tranactions
		"""
		self.cursor.execute("""commit""")


def FBController( profile ):
	"""
	Controller, takes JSON from View and makes FBPost objects for it. Also adds post to DB
	"""
	parser= FBView('CAACEdEose0cBAJfFvEueEKJlGzDxkhAZCGObd8BQTHqfl1KAljbhtF6FQyz4voobnGjjue7sLyCZCq8Oiuea5y4zTFqB3dEOv2JMZA6urZBp7szxGcUCZC9CW7SGPfZAKRra0WzHHsr9wA9QUheDiWMwBvyntp5pgPvLKlO5QAfasjK1sZAZBwKxI7iqaxvDpGsm7UVgQEKeEHZC7uKZByuTW5')
	posts = parser.parse_feed(profile)
	post_list= list()
	for post in posts:
		if post['status_type']=='added_photos':
			post_list.append(PicturePost(post))
		if post['status_type']=='added_video':
			post_list.append(VideoPost(post))
	db_connector= FBModel('localhost','mihir')
	for post in post_list:
		db_connector.add_post(post)
	db_connector.commit()


if __name__=='__main__':
	"""
	Testing
	"""
	FBController("nike")
	db = MySQLdb.connect("localhost","mihir")
	cursor = db.cursor()
	cursor.execute("""USE Facebook""")
	cursor.execute(""" SELECT * From Post""")
	res = cursor.fetchall()
	for row in res:
		print row









