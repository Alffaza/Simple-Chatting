import sys
import os
import json
import uuid
import logging
import json
from queue import  Queue
from os import listdir
from os.path import isfile, join

user_dir = "../users"
group_dir = "../groups"


class Chat:
	def __init__(self):
		self.sessions={}
		self.users = {}
		self.groups = {}
		# groups[id] = {members: [], message_history: [{from, message}]}]}
		for filename in listdir(user_dir):
			filepath = user_dir + "/" + filename
			file = open(filepath,'r')
			deserialized_json = json.load(file)
			username = filename.split('.')[0]
			self.users[username] = deserialized_json
			print(username)
			print(deserialized_json)

		for filename in listdir(group_dir):
			filepath = group_dir + "/" + filename
			file = open(filepath,'r')
			deserialized_json = json.load(file)
			username = filename.split('.')[0]
			self.groups[username] = deserialized_json
			print(username)
			print(deserialized_json)

	def save_user(self, name):
		filepath = user_dir + "/" + str(name) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.users[name], outfile)
	def save_group(self, id):
		filepath = group_dir + "/" + str(id) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.groups[id], outfile)

	def proses(self,data):
		j=data.split(" ")
		try:
			command=j[0].strip()
			if (command=='auth'):
				username=j[1].strip()
				password=j[2].strip()
				logging.warning("AUTH: auth {} {}" . format(username,password))
				return self.autentikasi_user(username,password)
			elif (command=='send'):
				sessionid = j[1].strip()
				usernameto = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
				return self.send_message(sessionid,usernamefrom,usernameto,message)
			elif (command=='sendg'):
				sessionid = j[1].strip()
				group_id = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,group_id))
				return self.send_message_group(sessionid,usernamefrom,group_id,message)
			elif (command=='inbox'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				logging.warning("INBOX: {}" . format(sessionid))
				return self.get_inbox(username)
			else:
				return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
		except KeyError:
			return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
		except IndexError:
			return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}
	def autentikasi_user(self,username,password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
		if (self.users[username]['password']!= password):
			return { 'status': 'ERROR', 'message': 'Password Salah' }
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }
	def get_user(self,username):
		if (username not in self.users):
			return False
		return self.users[username]
	def get_group(self,group_id):
		if (group_id not in self.groups):
			return False
		return self.groups[group_id]
	def send_message_group(self, sessionid, username_from, group_id, message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		g_to = self.get_group(group_id)

		if (s_fr==False or g_to==False):
			return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}

		message_log = { 'msg_from': s_fr['nama'], 'msg_to': g_to['nama'], 'msg': message }
		outqueue_sender = s_fr['outgoing']
		# inqueue_receiver = g_to['incoming']
		try:	
			outqueue_sender[username_from].put(message_log)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message_log)
		# try:
		# 	inqueue_receiver[username_from].put(message_log)
		# except KeyError:
		# 	inqueue_receiver[username_from]=Queue()
		# 	inqueue_receiver[username_from].put(message_log)
		
		self.groups[group_id]['message_history'].append({"sender": username_from, "mesasge": message})
		print(self.groups[group_id])
		self.save_group(group_id)

		return {'status': 'OK', 'message': 'Message Sent'}

	def send_message(self,sessionid,username_from,username_dest,message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		
		if (s_fr==False or s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_to['incoming']
		try:	
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)
		return {'status': 'OK', 'message': 'Message Sent'}

	def get_inbox(self,username):
		s_fr = self.get_user(username)
		incoming = s_fr['incoming']
		msgs={}
		for users in incoming:
			msgs[users]=[]
			while not incoming[users].empty():
				msgs[users].append(s_fr['incoming'][users].get_nowait())
			
		return {'status': 'OK', 'messages': msgs}


if __name__=="__main__":
	j = Chat()
	sesi = j.proses("auth messi surabaya")
	print(sesi)
	#sesi = j.autentikasi_user('messi','surabaya')

	#print sesi
	tokenid = sesi['tokenid']
	print(j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid)))
	print(j.proses("send {} messi hello gimana kabarnya mess " . format(tokenid)))

	#print j.send_message(tokenid,'messi','henderson','hello son')
	#print j.send_message(tokenid,'henderson','messi','hello si')
	#print j.send_message(tokenid,'lineker','messi','hello si dari lineker')


	print("isi mailbox dari messi")
	print(j.get_inbox('messi'))
	print("isi mailbox dari henderson")
	print(j.get_inbox('henderson'))
















