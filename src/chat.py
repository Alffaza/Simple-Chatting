import base64
import socket
import sys
import os
import json
import threading
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
realm_dir = "../realms"

def error_message(message):
	return {"status": 'ERROR', 'message': message}

def ok_message(message):
	return {"status": 'OK', 'message': message}

def ok_token(token):
	return {"status": 'OK', 'tokenid': token}


class RealmThreadCommunication(threading.Thread):
    def __init__(self, chats, realm_dest_address, realm_dest_port):
        self.chats = chats
        self.chat = {}
        self.realm_dest_address = realm_dest_address
        self.realm_dest_port = realm_dest_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.realm_dest_address, self.realm_dest_port))
        threading.Thread.__init__(self)

    def sendstring(self, string):
        try:
            self.sock.sendall(string.encode())
            receivedmsg = ""
            while True:
                data = self.sock.recv(1024)
                print("diterima dari server", data)
                if (data):
                    receivedmsg = "{}{}" . format(receivedmsg, data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivedmsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivedmsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}

class Chat:
	def __init__(self):
		self.sessions={}
		self.users = {}
		# users[username] = {nama: "", negara: "", password: ""}]}
		self.privates = {}
		# privates[id] = {userx: "", usery: "", message_history: [{from, message}]}]}
		self.groups = {}
		self.realms = {}
		# groups[id] = {members: [], message_history: [{from, message}]}]}
		for filename in os.listdir(user_dir):
			filepath = os.path.join(user_dir, filename)
			if os.path.isfile(filepath):  # Check if the path is a file
				with open(filepath, 'r') as file:
					deserialized_json = json.load(file)
					username = filename.split('.')[0]
					self.users[username] = deserialized_json
					# print(username)
					# print(deserialized_json)

		for filename in listdir(private_dir):
			filepath = os.path.join(private_dir, filename)
			if os.path.isfile(filepath):
				with open(filepath, 'r') as file:
					deserialized_json = json.load(file)
					username = filename.split('.')[0]
					self.privates[username] = deserialized_json
					# print(username)
					# print(deserialized_json)

		for filename in listdir(group_dir):
			filepath = os.path.join(group_dir, filename)
			if os.path.isfile(filepath):
				with open(filepath, 'r') as file:
					deserialized_json = json.load(file)
					group_id = filename.split('.')[0]
					self.groups[group_id] = deserialized_json
					# print(group_id)
					# print(deserialized_json)

		for filename in listdir(realm_dir):
			filepath = os.path.join(realm_dir, filename)
			if os.path.isfile(filepath):
				with open(filepath, 'r') as file:
					deserialized_json = json.load(file)
					realm_id = filename.split('.')[0]
					self.realms[realm_id] = deserialized_json
					# print(realm_id)
					# print(deserialized_json)

	def save_user(self, name):
		filepath = user_dir + "/" + str(name) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.users[name], outfile)

	def save_private(self, userx, usery):
		# sorted str of userx and usery as id
		id = ''.join(sorted([userx, usery]))
		filepath = private_dir + "/" + str(id) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.privates[id], outfile)

	def save_private_realm(self, userx, usery, realm_id):
		# sorted str of userx and usery as id
		id = ''.join(sorted([userx, usery])) + "-" + realm_id
		filepath = private_dir + "/" + str(id) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.privates[id], outfile)

	def save_group(self, id):
		filepath = group_dir + "/" + str(id) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.groups[id], outfile)

	def delete_group(self, id):
		filepath = group_dir + "/" + str(id) + ".json"
		if (open( filepath, "w")):
			os.remove(filepath)

	def save_realm(self, id):
		filepath = realm_dir + "/" + str(id) + ".json"
		with open( filepath, "w") as outfile:
			json.dump(self.realms[id], outfile)

	def proses(self,data):
		j=data.split(" ")
		# print("data: {}" . format(j))
		try:
			command=j[0].strip()
			# print("command: {}" . format(command))
			if (command=='auth'):
				username=j[1].strip()
				password=j[2].strip()
				logging.warning("AUTH: auth {} {}" . format(username,password))
				return self.autentikasi_user(username,password)
			
			elif (command=='listpc'):
				sessionid = j[1].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("LISTPRIVATECHAT: session {} user {} has requested list of private messages" . format(sessionid, user_me))
				return self.get_private_chat(sessionid, user_me)
			
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
				return self.list_group(sessionid, user_me)
			
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
			
			elif (command=='addrealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				realm_dest_address = j[3].strip()
				realm_dest_port = int(j[4].strip())
				logging.warning("ADDREALM: session {} add realm {} with address {} and port {}" . format(sessionid, realm_id, realm_dest_address, realm_dest_port))
				return self.add_realm(realm_id, realm_dest_address, realm_dest_port, data)
			
			elif (command=='recvrealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				realm_dest_address = j[3].strip()
				realm_dest_port = int(j[4].strip())
				logging.warning("RECVREALM: session {} recv realm {} with address {} and port {}" . format(sessionid, realm_id, realm_dest_address, realm_dest_port))
				return self.recv_realm(realm_id, realm_dest_address, realm_dest_port)
			
			elif (command=='listrealm'):
				sessionid = j[1].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("LISTREALM: session {} user {} has requested list of realms" . format(sessionid, user_me))
				return self.list_realm(sessionid)
			
			elif (command=='sendpcrealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				usernameto = j[3].strip()
				message=""
				for w in j[4:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SENDPRIVATEREALM: session {} send message from {} to {} in realm {}" . format(sessionid, usernamefrom, usernameto, realm_id))
				return self.send_message_realm(sessionid, realm_id, usernamefrom, usernameto, message)
			
			elif (command=='listpcrealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("LISTPRIVATECHATREALM: session {} user {} has requested list of private messages in realm {}" . format(sessionid, user_me, realm_id))
				return self.list_pc_realm(sessionid, realm_id, user_me)
			
			elif (command=='sendpcfilerealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				usernameto = j[3].strip()
				filepath = j[4].strip()
				encoded_file = j[5].strip()
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SENDREALM: session {} send file from {} to {} in realm {}" . format(sessionid, usernamefrom, usernameto, realm_id))
				return self.send_file_realm(sessionid, realm_id, usernamefrom, usernameto, filepath, encoded_file)
			
			elif (command=='creategrouprealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				group_name = j[3].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("CREATEGROUPREALM: session {} user {} has created group {} in realm {}" . format(sessionid, user_me, group_name, realm_id))
				return self.create_group_realm(sessionid, realm_id, user_me, group_name)
			
			elif (command=='listgrouprealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("LISTGROUPREALM: session {} user {} has requested list of groups in realm {}" . format(sessionid, user_me, realm_id))
				return self.list_group_realm(sessionid, realm_id, user_me)
			
			elif (command=='invitegrouprealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				group_id = j[3].strip()
				invited_username = j[4].strip()
				invitation_from = self.sessions[sessionid]['username']
				logging.warning("INVITEGROUPREALM: session {} {} invited {} to group {} in realm {}" . format(sessionid, invitation_from, invited_username, group_id, realm_id))
				return self.invite_user_to_group_realm(sessionid, realm_id, invitation_from, invited_username, group_id)
			
			elif (command=='sendgrouprealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				group_id = j[3].strip()
				message=""
				for w in j[4:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SENDGROUPREALM: session {} send message from {} to group {} in realm {}" . format(sessionid, usernamefrom, group_id, realm_id))
				return self.send_message_group_realm(sessionid, realm_id, usernamefrom, group_id, message)
			
			elif (command=='sendgroupfilerealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				group_id = j[3].strip()
				filepath = j[4].strip()
				encoded_file = j[5].strip()
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SENDGROUPREALM: session {} send file from user {} to group {} in realm {}" . format(sessionid, usernamefrom, group_id, realm_id))
				return self.send_file_group_realm(sessionid, realm_id, usernamefrom, group_id, filepath, encoded_file)

			elif (command=='inbox'):
				sessionid = j[1].strip()
				inbox_with = j[2].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("INBOX: session {} user {} has requested inbox with {}" . format(sessionid, user_me, inbox_with))
				return self.get_inbox(sessionid, user_me, inbox_with)
			
			elif (command=='inboxgroup'):
				sessionid = j[1].strip()
				group_id = j[2].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("INBOXGROUP: session {} user {} has requested inbox group {}" . format(sessionid, user_me, group_id))
				return self.get_group_messages(sessionid, user_me, group_id)
			
			elif (command=='inboxrealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				inbox_with = j[3].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("INBOXREALM: session {} user {} has requested inbox with {} in realm {}" . format(sessionid, user_me, inbox_with, realm_id))
				return self.get_inbox_realm(sessionid, realm_id, user_me, inbox_with)
			
			elif (command=='inboxgrouprealm'):
				sessionid = j[1].strip()
				realm_id = j[2].strip()
				group_id = j[3].strip()
				user_me = self.sessions[sessionid]['username']
				logging.warning("INBOXGROUPREALM: session {} user {} has requested inbox group {} in realm {}" . format(sessionid, user_me, group_id, realm_id))
				return self.get_group_messages_realm(sessionid, realm_id, user_me, group_id)
			else:
				return error_message('Incorrect command')
		except KeyError:
			return error_message('Missing Information')
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
	
	def get_private(self, user):
		# ambil semua nama pada file private, pada setiap iterasi, jika user ada di nama file tersebut, catat nama filenya, kemudian return kumpulan nama file tersebut
		available_private_chat = []
		for private in self.privates:
			if (user in private):
				available_private_chat.append(private.replace(user, ""))
		return available_private_chat
	
	def get_private_realm(self, user, realm_id):
		# ambil semua nama pada file private, pada setiap iterasi, jika user ada di nama file tersebut, catat nama filenya, kemudian return kumpulan nama file tersebut
		available_private_chat = []
		for private in self.privates:
			if (user in private) and ("-" + realm_id in private):
				available_private_chat.append(private.replace(user, ""))
		return available_private_chat
	
	def get_group(self, group_id):
		if (group_id not in self.groups):
			return False
		return self.groups[group_id]
	
	def get_private_chat(self, sessionid, username):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		available_privat_chat = self.get_private(username)
		return {'status': 'OK' , 'private_chat' : available_privat_chat}
	
	def send_message_group(self, sessionid, username_from, group_id, message):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (group_id not in self.groups or username_from not in self.groups[group_id]['members']):
			return error_message('Group not found')
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
		message_log = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
		id = ''.join(sorted([username_from, username_dest]))
		if (id not in self.privates):
			self.privates[id] = {"userx": username_from, "usery": username_dest, "message_history": []}
		self.privates[id]['message_history'].append({"sender": username_from, "message": message})
		print(self.privates[id])
		self.save_private(username_from, username_dest)
		return ok_message('Message sent')
	
	def send_file(self, sessionid, username_from, username_dest, filepath, encoded_file):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		if (s_fr==False or s_to==False):
			return error_message('User not found')
		filename = os.path.basename(filepath)
		time_now = time.strftime("%Y%m%d-%H%M%S")
		id = ''.join(sorted([username_from, username_dest]))
		filesum = f"{time_now}_{username_from}_{id}_{filename}"
		if (id not in self.privates):
			self.privates[id] = {"userx": username_from, "usery": username_dest, "message_history": []}
		self.privates[id]['message_history'].append({"sender": username_from, "filename": filesum, "file": encoded_file})
		self.save_private(username_from, username_dest)

		#simpan file dalam folder files/<id>/dest_filename dengan nama <tanggal>-<user_from>-<user_to>-<filename>.<ekstensi>
		#misal 2017-04-05-messi-henderson-funny.gif
		filedest = join(dirname(realpath(__file__)), "files/")
		os.makedirs(filedest, exist_ok=True)
		filedest = join(filedest, id)
		os.makedirs(filedest, exist_ok=True)
		filedest = join(filedest, filesum)

		decode_content = base64.decodebytes(encoded_file.encode('utf-8'))
		with open(filedest, "wb") as f:
			f.write(decode_content)

		return ok_message('File sent')
		

	def send_file_group(self, sessionid, username_from, group_id, filepath, encoded_file):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (group_id not in self.groups or username_from not in self.groups[group_id]['members']):
			return error_message('Group not found')
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
	
	def list_group(self, sessionid, username):
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
	
	def add_realm(self, realm_id, realm_dest_address, realm_dest_port, data):
		j = data.split()
		j[0] = "recvrealm"
		data = ' '.join(j)
		data += "\r\n"
		if realm_id in self.realms:
			return error_message('Realm already exists')
          
		self.realms[realm_id] = RealmThreadCommunication(self, realm_dest_address, realm_dest_port)
		result = self.realms[realm_id].sendstring(data)
		return result
	
	def recv_realm(self, realm_id, realm_dest_address, realm_dest_port):
		self.realms[realm_id] = RealmThreadCommunication(self, realm_dest_address, realm_dest_port)
		self.realms[realm_id] = {"address": realm_dest_address, "port": realm_dest_port}
		self.save_realm(realm_id)
		return ok_message('Realm ' + realm_id + ' successfully added')
	
	def list_realm(self, sessionid):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		available_realms = {}
		for realm in self.realms:
			available_realms[realm] = self.realms[realm]['address'] + ":" + str(self.realms[realm]['port'])
		return {'status': 'OK' , 'realms' : available_realms}
	
	def send_message_realm(self, sessionid, realm_id, username_from, username_dest, message):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		if (s_fr==False or s_to==False):
			return error_message('User not found')
		message_log = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
		# tambahkan penanda bahwa username_from dan username_dest berada di realm_id dengan menambahkan "-realm_id" di belakang id
		id = ''.join(sorted([username_from, username_dest])) + "-" + realm_id
		if (id not in self.privates):
			self.privates[id] = {"userx": username_from, "usery": username_dest, "message_history": []}
		self.privates[id]['message_history'].append({"sender": username_from, "message": message})
		print(self.privates[id])
		self.save_private_realm(username_from, username_dest, realm_id)
		return ok_message('Message sent')
	
	def list_pc_realm(self, sessionid, realm_id, username):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		available_privat_chat = self.get_private_realm(username, realm_id)
		return {'status': 'OK' , 'private_chat' : available_privat_chat}
	
	def send_file_realm(self, sessionid, realm_id, username_from, username_dest, filepath, encoded_file):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)
		if (s_fr==False or s_to==False):
			return error_message('User not found')
		filename = os.path.basename(filepath)
		time_now = time.strftime("%Y%m%d-%H%M%S")
		id = ''.join(sorted([username_from, username_dest])) + "-" + realm_id
		filesum = f"{time_now}_{username_from}_{id}_{filename}"
		if (id not in self.privates):
			self.privates[id] = {"userx": username_from, "usery": username_dest, "message_history": []}
		self.privates[id]['message_history'].append({"sender": username_from, "filename": filesum, "file": encoded_file})
		self.save_private_realm(username_from, username_dest, realm_id)

		#simpan file dalam folder files/<id>/dest_filename dengan nama <tanggal>-<user_from>-<user_to>-<filename>.<ekstensi>
		#misal 2017-04-05-messi-henderson-funny.gif
		filedest = join(dirname(realpath(__file__)), "files/")
		os.makedirs(filedest, exist_ok=True)
		filedest = join(filedest, id)
		os.makedirs(filedest, exist_ok=True)
		filedest = join(filedest, filesum)

		decode_content = base64.decodebytes(encoded_file.encode('utf-8'))
		with open(filedest, "wb") as f:
			f.write(decode_content)

		return ok_message('File sent')
	
	def create_group_realm(self, sessionid, realm_id, user_me, group_name):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		group_id = str(time.time()).split('.')[0] + "-" + realm_id
		if(group_id in self.groups):
			return error_message('Failed to make group')
		self.groups[group_id] = {"nama": group_name, "message_history": [], "members": [user_me]}
		self.save_group(group_id)
		return ok_message('Successfully created group ' + group_name)
	
	def list_group_realm(self, sessionid, realm_id, username):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		if (username not in self.users):
			return error_message('User not found')
		available_groups = {}
		for group in self.groups:
			if ("-" + realm_id in group):
				available_groups[group] = self.groups[group]['nama']
		return {'status': 'OK' , 'groups' : available_groups}

	
	def invite_user_to_group_realm(self, sessionid, realm_id, invitation_from, invited_username, group_id):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		if (invited_username not in self.users):
			return error_message('The invited user does not exist')
		if (group_id not in self.groups or invitation_from not in self.groups[group_id]['members']):
			return error_message('Group not found')
		self.groups[group_id]['members'].append(invited_username)
		self.save_group(group_id)
		return ok_message('Seccessfully invited '+ invited_username+ ' to ' + self.groups[group_id]['nama'])
	
	def send_message_group_realm(self, sessionid, realm_id, username_from, group_id, message):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		if (group_id not in self.groups or username_from not in self.groups[group_id]['members']):
			return error_message('Group not found')
		s_fr = self.get_user(username_from)
		g_to = self.get_group(group_id)
		if (s_fr==False or g_to==False):
			return error_message('Group not found')
		message_log = { 'msg_from': s_fr['nama'], 'msg_to': g_to['nama'], 'msg': message }
		self.groups[group_id]['message_history'].append({"sender": username_from , "message": message})
		print(self.groups[group_id])
		self.save_group(group_id)
		return ok_message('Message sent')
	
	def send_file_group_realm(self, sessionid, realm_id, username_from, group_id, filepath, encoded_file):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		if (group_id not in self.groups or username_from not in self.groups[group_id]['members']):
			return error_message('Group not found')
		s_fr = self.get_user(username_from)
		g_to = self.get_group(group_id)
		if (s_fr==False or g_to==False):
			return error_message('Group not found')
		filename = os.path.basename(filepath)
		time_now = time.strftime("%Y%m%d-%H%M%S")
		filesum = f"{time_now}_{username_from}_{group_id}_{filename}"
		self.groups[group_id]['message_history'].append({"sender": username_from , "filename": filesum, "file": encoded_file})
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

	
	def get_inbox(self,sessionid, user_me, inbox_with):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (inbox_with not in self.users):
			return error_message('User not found')
		id = ''.join(sorted([user_me, inbox_with]))
		if (id not in self.privates):
			return ok_message([])
		inbox = self.privates[id]['message_history']
		return ok_message(inbox)
	
	def get_group_messages(self, sessionid, user_me, group_id):
			if (sessionid not in self.sessions):
				return error_message('Session not found')
			if (group_id not in self.groups or user_me not in self.groups[group_id]['members']):
				return error_message('Group not found')
			group_messages = self.groups[group_id]['message_history']
			return ok_message(group_messages)
	
	def get_inbox_realm(self, sessionid, realm_id, user_me, inbox_with):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		if (inbox_with not in self.users):
			return error_message('User not found')
		id = ''.join(sorted([user_me, inbox_with])) + "-" + realm_id
		if (id not in self.privates):
			return ok_message([])
		inbox = self.privates[id]['message_history']
		return ok_message(inbox)
	
	def get_group_messages_realm(self, sessionid, realm_id, user_me, group_id):
		if (sessionid not in self.sessions):
			return error_message('Session not found')
		if (realm_id not in self.realms):
			return error_message('Realm not found')
		if (group_id not in self.groups or user_me not in self.groups[group_id]['members']):
			return error_message('Group not found')
		group_messages = self.groups[group_id]['message_history']
		return ok_message(group_messages)


if __name__=="__main__":
	j = Chat()
	sesi = j.proses("auth messi surabaya")
	print(sesi)
	#print sesi
	tokenid = sesi['tokenid']

	#testing
	# print(j.leave_group(tokenid, '1686417836'))
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
















