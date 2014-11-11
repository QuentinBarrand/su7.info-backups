#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

try:
	import swiftclient
except Exception as e:
	print 'The swiftclient package was not found. Please install the required dependencies using "pip install -r requirements.txt".'
	sys.exit(2)


class SwiftContainer:

	def __init__(self, authurl, auth_version, user, key, tenant_name, container_name, autocreate=True):
		self.authurl = authurl
		self.auth_version = auth_version
		self.user = user
		self.key = key
		self.tenant_name = tenant_name
		self.container_name = container_name
		self.autocreate = autocreate

		self.connection = swiftclient.client.Connection(
			authurl=self.authurl,
			auth_version=self.auth_version,
			user=self.user,
			key=self.key,
			tenant_name=self.tenant_name)


	def container_exists(self):
		for container in self.get_containers():
			if self.container_name == container['name']:
				return True

		return False


	def delete(self, filename):
		self.connection.delete_object(
			container=self.container_name,
			obj=filename)


	def get_containers(self):
		(_, containers) = self.connection.get_account()

		return containers


	def upload(self, filename):
		if not self.container_exists():
			self.connection.put_container(self.container_name)

		self.connection.put_object(
			container=self.container_name,
			obj=os.path.basename(filename),
			contents=open(filename, 'r'),
			content_type='application/x-gzip')
