import firebase_admin, os
from firebase_admin import credentials, firestore
from utils import authorization
class Firebase:
	def __init__(self):
		firebase_admin.initialize_app(credentials.Certificate(authorization('firebase')), authorization('firebase_project'))
		self.db = firestore.client()

	def add_document(self, collection, key, data):
		self.db.collection(collection).document(key).set(data)

	def remove_document(self, collection, key):
		for doc in self.db.collection(collection).get():
			if doc.id == key: doc.reference.delete()

	def update_document(self, collection, key, data):
		self.db.collection(collection).document(key).update(data)

	def get_documents(self, collection):
		return {doc.id: doc.to_dict() for doc in self.db.collection(collection).get()}
