import redis
import json

class Data:

	def __init__(self):
		self.redis = redis.StrictRedis()
		self.name = self.__class__.__name__.lower()

	def set(self, key, value):
		self.redis.set('{0}.{1}'.format(self.name, key), value)
		self.redis.save()

	def get(self, key):
		return self.redis.get('{0}.{1}'.format(self.name, key))

	def set_list(self, key, list):
		encoded_list = json.dumps(list)

		self.set(key, encoded_list)

	def get_list(self, key):
		encoded_list = self.get(key).decode('utf-8')
		list = json.loads(encoded_list)

		return list if list is not None else []

class Permissible(Data):

	def check_permission(self, id):
		return id in self.get_list('permission')

	def give_permission(self, ids=None):
		permission = self.get_list('permission')

		if hasattr(ids, '__iter__') and not isinstance(ids, str):
			permission.extend(ids)

		else:
			permission.append(ids)

		self.set_list('permission', permission)

	def remove_permission(self, ids=None):
		permission = self.get_list('permission')

		if hasattr(ids, '__iter__') and not isinstance(ids, str):
			for id in ids:
				permission.remove(id)

		else:
			permission.remove(id)

		self.set_list('permission', permission)