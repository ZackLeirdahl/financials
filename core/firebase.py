import firebase_admin, os
from firebase_admin import credentials, firestore

class Firebase:
	def __init__(self):
		try:
			firebase_admin.initialize_app(credentials.Certificate(os.path.join('\\'.join(os.path.dirname(__file__).split('\\')[:len(os.path.dirname(__file__).split('\\')) -1]) + '\\credentials','trader-3870e-firebase-adminsdk-ht79b-863abdb2e1.json')), {'projectId':'trader-3870e'})
		except:
			firebase_admin.initialize_app(credentials.Certificate(os.path.join('/'.join(os.path.dirname(__file__).split('/')[:len(os.path.dirname(__file__).split('/')) -1]) + '/credentials','trader-3870e-firebase-adminsdk-ht79b-863abdb2e1.json')), {'projectId':'trader-3870e'})
		self.db = firestore.client()

	def add_document(self, collection, key, data):
		self.db.collection(collection).document(key).set(data)

	def remove_document(self, collection, key):
		for doc in self.db.collection(collection).get():
			if doc.id == key: doc.reference.delete()

	def update_document(self, collection, key, data):
		self.db.collection(collection).document(key).update(data)

	def get_documents(self, collection):
		return [doc.id for doc in self.db.collection(collection).get()]
