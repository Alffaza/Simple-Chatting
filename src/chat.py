import base64
import sys
import os
import json
import uuid
import logging
import json
import time
from queue import  Queue
from os import listdir
from os.path import isfile, join, dirname, realpath

user_dir = "../users"
private_dir = "../privates"
group_dir = "../groups"

def error_message(message):
	return {"status": 'ERROR', 'message': message}

def ok_message(message):
	return {"status": 'OK', 'message': message}

def ok_token(token):
	return {"status": 'OK', 'tokenid': token}

class Chat:
	def __init__(self):
		self.sessions={}
		self.users = {}
		# users[username] = {nama: "", negara: "", password: ""}]}
		self.privates = {}
		# private[userxy] = {userx: "", usery: "", message_history: [{from, message}]}]
		self.groups = {}
		# groups[id] = {members: [], message_history: [{from, message}]}]}
		if not os.path.exists(user_dir):
			os.makedirs(user_dir)
		for filename in listdir(user_dir):
			filepath = user_dir + "/" + filename
			file = open(filepath,'r')
			deserialized_json = json.load(file)
			username = filename.split('.')[0]
			self.users[username] = deserialized_json
			# print(username)
			# print(deserialized_json)

		if not os.path.exists(private_dir):
			os.makedirs(private_dir)
		for filename in listdir(private_dir):
			filepath = private_dir + "/" + filename
			file = open(filepath,'r')
			deserialized_json = json.load(file)
			username = filename.split('.')[0]
			# self.privates[username]['incoming'] = deserialized_json
			self.privates[username] = deserialized_json
			# print(username)
			# print(deserialized_json)

		if not os.path.exists(group_dir):
			os.makedirs(group_dir)
		for filename in listdir(group_dir):
			filepath = group_dir + "/" + filename
			file = open(filepath,'r')
			deserialized_json = json.load(file)
			username = filename.split('.')[0]
			self.groups[username] = deserialized_json
			# print(username)
			# print(deserialized_json)

	def save_user(self, name):
		filepath = user_dir + "/" + str(name) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.users[name], outfile)

	def save_private(self, name):
		filepath = private_dir + "/" + str(name) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.privates[name], outfile)

	def save_group(self, id):
		filepath = group_dir + "/" + str(id) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.groups[id], outfile)

	def delete_group(self, id):
		filepath = group_dir + "/" + str(id) + ".json"
		if (open( filepath, "w")):
			os.remove(filepath)

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
			
			elif (command=='sendfile'):
				sessionid = j[1].strip()
				usernameto = j[2].strip()
				filepath = j[3].strip()
				encoded_file = j[4].strip()
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send file from {} to {}" . format(sessionid, usernamefrom, usernameto))
				return self.send_file(sessionid,usernamefrom,usernameto,filepath, encoded_file)
			
			elif (command=='register'):
				username = j[1].strip()
				real_name = j[2].strip()
				password = j[3].strip()
				country = j[4].strip()

				if (username in self.users):
					return error_message('User already exists')
				self.users[username] = {'nama': real_name, "negara": country, "password": password}
				self.save_user(username)
				return ok_message("Account successfully registered")
			
			elif (command=='creategroup'):
				sessionid = j[1].strip()
				group_name = j[2].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("CREATEGROUP: session {} user {} has created group {}" . format(sessionid, user_me, group_name))
				return self.create_group(sessionid, user_me, group_name)
			
			elif (command=='listgroup'):
				sessionid = j[1].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("LISTGROUP: session {} user {} has requested list of groups" . format(sessionid, user_me))
				return self.get_groups_with_user(sessionid, user_me)
			
			elif (command=='sendgroup'):
				sessionid = j[1].strip()
				group_id = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SENDGROUP: session {} send message from {} to group {}" . format(sessionid, usernamefrom, group_id))
				return self.send_message_group(sessionid, usernamefrom, group_id, message)
			
			elif (command=='sendfilegroup'):
				sessionid = j[1].strip()
				group_id = j[2].strip()
				filepath = j[3].strip()
				encoded_file = j[4].strip()
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SENDGROUP: session {} send file from user {} to group {}" . format(sessionid, usernamefrom, group_id))
				return self.send_file_group(sessionid, usernamefrom, group_id, filepath, encoded_file)
			
			elif (command=='leavegroup'):
				# session id, group id
				sessionid = j[1].strip()
				group_id = j[2].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("LEAVEGROUP: session {} user {} has left group {}" . format(sessionid, user_me, group_id))
				return self.leave_group(sessionid, user_me, group_id)
			
			elif (command=='invitegroup'):
				sessionid = j[1].strip()
				group_id = j[2].strip()
				invited_username = j[3].strip()
				invitation_from = self.sessions[sessionid]['username']
				logging.warning("INVITEGROUP: session {} {} invited {} to group {}" . format(sessionid, invitation_from, invited_username, group_id))
				return self.invite_user_to_group(sessionid, invitation_from, invited_username, group_id)

			elif (command=='inbox'):
				sessionid = j[1].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("INBOX: session {} user {} has requested inbox" . format(sessionid, user_me))
				return self.get_inbox(sessionid, user_me)
			
			elif (command=='inboxgroup'):
				sessionid = j[1].strip()
				group_id = j[2].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("INBOXGROUP: session {} user {} has requested inbox group {}" . format(sessionid, user_me, group_id))
				return self.get_group_messages(sessionid, user_me, group_id)
			else:
				return error_message('Incorrect command')
		# except KeyError:
		# 	return error_message('Missing Information')
		except IndexError:
			return error_message('Incorrect command arguments')
		

	def autentikasi_user(self, username, password):
		if (username not in self.users):
			return error_message('User not found')
		if (self.users[username]['password']!= password):
			return error_message('Incorrect password')
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return ok_token(tokenid)
	
	def get_user(self, username):
		if (username not in self.users):
			return False
		return self.users[username]
	
	def get_group(self, group_id):
		if (group_id not in self.groups):
			return False
		return self.groups[group_id]
	
	def send_message_group(self, sessionid, username_from, group_id, message):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		s_fr = self.get_user(username_from)
		g_to = self.get_group(group_id)
		if (s_fr==False or g_to==False):
			return error_message('Group not found')
		message_log = { 'msg_from': s_fr['nama'], 'msg_to': g_to['nama'], 'msg': message }
		self.groups[group_id]['message_history'].append({"sender": username_from, "message": message})
		print(self.groups[group_id])
		self.save_group(group_id)
		return ok_message('Message sent')

	def send_message(self, sessionid, username_from, username_dest, message):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		
		if (s_fr==False or s_to==False):
			return error_message('User not found')

		# message_log = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
		sorted_user = sorted([username_from, username_dest])
		userxy = f"{sorted_user[0]}_{sorted_user[1]}"
		if (userxy not in self.privates):
			self.privates[userxy] = {'userx': sorted_user[0], 'usery': sorted_user[1], 'message_history': [{}]}
		self.privates[userxy]['message_history'].append({"sender": username_from, "message": message})
		print(self.privates[userxy])
		self.save_private(userxy)
		return ok_message('Message sent')
	
	def send_file(self, sessionid, username_from, username_dest, filepath, encoded_file):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		
		if (s_fr==False or s_to==False):
			return error_message('User not found')

		filename = os.path.basename(filepath)
		message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'file_name': filename, 'file': encoded_file }
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
		
		#simpan file dalam folder files/<user_to>/dest_filename dengan nama <tanggal>-<user_from>-<user_to>-<filename>.<ekstensi>
		#misal 2017-04-05-messi-henderson-funny.gif
		filedest = join(dirname(realpath(__file__)), "files/")
		os.makedirs(filedest, exist_ok=True)
		filedest = join(filedest, username_dest)
		os.makedirs(filedest, exist_ok=True)
		time_now = time.strftime("%Y%m%d-%H%M%S")
		filesum = f"{time_now}_{username_from}_{username_dest}_{filename}"
		filedest = join(filedest, filesum)

		decode_content = base64.decodebytes(encoded_file.encode('utf-8'))
		with open(filedest, "wb") as f:
			f.write(decode_content)

		return ok_message('File sent')
	
	def send_file_group(self, sessionid, username_from, group_id, filepath, encoded_file):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		s_fr = self.get_user(username_from)
		g_to = self.get_group(group_id)
		if (s_fr==False or g_to==False):
			return error_message('Group not found')
		filename = os.path.basename(filepath)
		time_now = time.strftime("%Y%m%d-%H%M%S")
		filesum = f"{time_now}_{username_from}_{group_id}_{filename}"
		self.groups[group_id]['message_history'].append({"sender": username_from, "filename": filesum, "file": encoded_file})
		self.save_group(group_id)
		
		#simpan file dalam folder files/<user_to>/dest_filename dengan nama <tanggal>-<user_from>-<user_to>-<filename>.<ekstensi>
		#misal 2017-04-05-messi-henderson-funny.gif
		filedest = join(dirname(realpath(__file__)), "files/")
		os.makedirs(filedest, exist_ok=True)
		filedest = join(filedest, group_id)
		os.makedirs(filedest, exist_ok=True)
		filedest = join(filedest, filesum)

		decode_content = base64.decodebytes(encoded_file.encode('utf-8'))
		with open(filedest, "wb") as f:
			f.write(decode_content)

		return ok_message('File sent')
	
	def get_groups_with_user(self, sessionid, username):
		if (sessionid not in self.sessions):
			return error_message('Session not found')	
		available_groups = {}
		for group in self.groups:
			if (username in self.groups[group]['members']):
				available_groups[group] = self.groups[group]['nama']
		return {'status': 'OK' , 'groups' : available_groups}
	
	def leave_group(self, sessionid, user_me, group_id):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (group_id not in self.groups or user_me not in self.groups[group_id]['members']):
			return error_message('Group not found')
		self.groups[group_id]['members'].remove(user_me)
		if(len(self.groups[group_id]['members']) == 0):
			self.delete_group(group_id)
		else:
			self.save_group(group_id)
		return ok_message('Successfully left the group')
	
	def create_group(self, sessionid, user_me, group_name):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		group_id = str(time.time()).split('.')[0]
		if(group_id in self.groups):
			return error_message('Failed to make group')
		self.groups[group_id] = {"nama": group_name, "message_history": [], "members": [user_me]}
		self.save_group(group_id)
		return ok_message('Successfully created group' + group_name)

	def invite_user_to_group(self, sessionid, invitation_from, invited_username, group_id):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (invited_username not in self.users):
			return error_message('The invited user does not exist')
		if (group_id not in self.groups or invitation_from not in self.groups[group_id]['members']):
			return error_message('Group not found')
		self.groups[group_id]['members'].append(invited_username)
		self.save_group(group_id)
		return ok_message('Seccessfully invited '+ invited_username+ ' to ' + self.groups[group_id]['nama'])

	def get_group_messages(self, sessionid, user_me, group_id):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (group_id not in self.groups or user_me not in self.groups[group_id]['members']):
			return error_message('Group not found')
		group_messages = self.groups[group_id]['message_history']
		return ok_message(group_messages)
	
	def get_inbox(self,sessionid, username):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		s_fr = self.get_user(username)
		incoming = s_fr['incoming']
		msgs={}
		for users in incoming:
			msgs[users]=[]
			while not incoming[users].empty():
				msgs[users].append(s_fr['incoming'][users].get_nowait())
			
		return ok_message(msgs)


if __name__=="__main__":
	j = Chat()
	sesi = j.proses("auth messi surabaya")
	print(sesi)
	#print sesi
	tokenid = sesi['tokenid']

	#testing
	print(j.leave_group(tokenid, '1686417836'))
	# print(j.invite_user_to_group(tokenid, '1686418078', 'faza'))

	# print(j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid)))
	# print(j.proses("send {} messi hello gimana kabarnya mess " . format(tokenid)))

	#print j.send_message(tokenid,'messi','henderson','hello son')
	#print j.send_message(tokenid,'henderson','messi','hello si')
	#print j.send_message(tokenid,'lineker','messi','hello si dari lineker')


	# print("isi mailbox dari messi")
	# print(j.get_inbox('messi'))
	# print("isi mailbox dari henderson")
	# print(j.get_inbox('henderson'))
















