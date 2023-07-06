import base64
import socket
import os
import json
import sys

TARGET_IP = "127.0.0.1"
TARGET_PORT = 1111

# TARGET_IP = "0.tcp.ap.ngrok.io"
# TARGET_PORT = 15808

print('using ' + TARGET_IP + str(TARGET_PORT))

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""

    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            elif (command=='listpc'):
                return self.listpc()
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)
            elif (command=='sendfile'):
                usernameto = j[1].strip()
                filepath = j[2].strip()
                return self.sendfile(usernameto,filepath)
            elif (command=='creategroup'):
                groupname = j[1].strip()
                return self.creategroup(groupname)
            elif (command=='listgroup'):
                return self.listgroup()
            elif (command=='invitegroup'):
                group_id = j[1].strip()
                username = j[2].strip()
                return self.invitegroup(group_id,username)
            elif (command=='sendgroup'):
                group_id = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessagegroup(group_id,message)
            elif (command=='sendfilegroup'):
                group_id = j[1].strip()
                filepath = j[2].strip()
                return self.sendfilegroup(group_id,filepath)
            elif (command=='leavegroup'):
                group_id = j[1].strip()
                return self.leavegroup(group_id)
            elif (command=='register'):
                return self.register(j[1].strip(), j[2].strip(), j[3].strip(), j[4].strip())
            elif (command=='addrealm'):
                realm_id = j[1].strip()
                realm_address = j[2].strip()
                realm_port = j[3].strip()
                return self.add_realm(realm_id, realm_address, realm_port)
            elif (command=='listrealm'):
                return self.listrealm()
            elif (command=='listpcrealm'):
                realm_id = j[1].strip()
                return self.listpc_realm(realm_id)
            elif (command == 'sendpcrealm'):
                realm_id = j[1].strip()
                usernameto = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}".format(message, w)
                return self.send_realm_message(realm_id, usernameto, message)
            elif (command=='sendpcfilerealm'):
                realm_id = j[1].strip()
                usernameto = j[2].strip()
                filepath = j[3].strip()
                return self.send_file_realm(realm_id, usernameto,filepath)
            elif (command=='creategrouprealm'):
                realm_id = j[1].strip()
                groupname = j[2].strip()
                return self.create_group_realm(realm_id, groupname)
            elif (command=='invitegrouprealm'):
                realm_id = j[1].strip()
                group_id = j[2].strip()
                username = j[3].strip()
                return self.invite_group_realm(realm_id, group_id, username)
            elif (command=='listgrouprealm'):
                realm_id = j[1].strip()
                return self.listgroup_realm(realm_id)
            elif (command=='sendgrouprealm'):
                realm_id = j[1].strip()
                group_id = j[2].strip()
                message=""
                for w in j[3:]:
                    message="{} {}" . format(message,w)
                return self.send_group_realm_message(realm_id, group_id, message)
            elif (command=='sendgroupfilerealm'):
                realm_id = j[1].strip()
                group_id = j[2].strip()
                filepath = j[3].strip()
                return self.send_group_file_realm(realm_id, group_id, filepath)
            elif (command=='leavegrouprealm'):
                realm_id = j[1].strip()
                group_id = j[2].strip()
                return self.leave_group_realm(realm_id, group_id)
            elif (command=='inbox'):
                inbox_with = j[1].strip()
                return self.inbox(inbox_with)
            elif (command=='inboxgroup'):
                group_id = j[1].strip()
                return self.inboxgroup(group_id)
            elif (command == 'inboxrealm'):
                realm_id = j[1].strip()
                inbox_with = j[2].strip()
                return self.inbox_realm(realm_id, inbox_with)
            elif (command == 'inboxgrouprealm'):
                realm_id = j[1].strip()
                group_id = j[2].strip()
                return self.inboxgroup_realm(realm_id, group_id)
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
        
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}
        
    # COMMANDS
    def login(self,username,password):
        string="auth {} {} \r\n" . format(username, password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username, self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
        
    def register(self, username, real_name, password, country):
        string = "register {} {} {} {}\r\n" . format(username, real_name, password, country)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "successfully created account {}" . format(username)
        else:
            return "Error, {}" . format(result['message'])
        
    def listpc(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="listpc {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result!=[]:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])

    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        if (message[0] == " "):
            message = message[1:]
        string="send {} {} {} \r\n" . format(self.tokenid, usernameto, message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])

    #create function sendfile from specific path
    def sendfile(self,usernameto="xxx",filepath="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        
        #check if file exists
        print(filepath)
        if not os.path.isfile(filepath):
            return "Error, file not found"
        
        # Decode bytes to string
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode('utf-8')
        string="sendfile {} {} {} {} \r\n" . format(self.tokenid, usernameto, filepath, encoded_content)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "file sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
        
    def creategroup(self,groupname="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="creategroup {} {} \r\n" . format(self.tokenid, groupname)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group {} created" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
    
    def listgroup(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="listgroup {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result!=[]:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
    def invitegroup(self,group_id="xxx",username="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="invitegroup {} {} {} \r\n" . format(self.tokenid,group_id,username)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "user {} invited to group {}" . format(username,group_id)
        else:
            return "Error, {}" . format(result['message'])

    def sendmessagegroup(self,group_id="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgroup {} {} {} \r\n" . format(self.tokenid, group_id, message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(group_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def sendfilegroup(self,group_id="xxx",filepath="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        
        #check if file exists
        if not os.path.isfile(filepath):
            return "Error, file not found"
        
        # Decode bytes to string
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode('utf-8')
        string="sendfilegroup {} {} {} {} \r\n" . format(self.tokenid, group_id, filepath, encoded_content)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "file sent to group {}" . format(group_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def leavegroup(self,group_id="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="leavegroup {} {} \r\n" . format(self.tokenid, group_id)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group {} left" . format(group_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def add_realm(self, realm_id, realm_address, realm_port):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="addrealm {} {} {} {} \r\n" . format(self.tokenid, realm_id, realm_address, realm_port)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "realm {} added" . format(realm_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def listrealm(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="listrealm {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result!=[]:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
    def listpc_realm(self, realm_id):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="listpcrealm {} {} \r\n" . format(self.tokenid, realm_id)
        result = self.sendstring(string)
        if result!=[]:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
    def send_realm_message(self, realm_id, usernameto="xxx", message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        if (message[0] == " "):
            message = message[1:]
        string="sendpcrealm {} {} {} {} \r\n" . format(self.tokenid, realm_id, usernameto, message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
        
    def send_file_realm(self, realm_id, usernameto="xxx", filepath="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        
        #check if file exists
        if not os.path.isfile(filepath):
            return "Error, file not found"
        
        # Decode bytes to string
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode('utf-8')
        string="sendpcfilerealm {} {} {} {} {} \r\n" . format(self.tokenid, realm_id, usernameto, filepath, encoded_content)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "file sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
        
    def create_group_realm(self, realm_id, groupname="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="creategrouprealm {} {} {} \r\n" . format(self.tokenid, realm_id, groupname)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group {} created" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
        
    def invite_group_realm(self, realm_id, group_id="xxx", username="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="invitegrouprealm {} {} {} {} \r\n" . format(self.tokenid, realm_id, group_id, username)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "user {} invited to group {}" . format(username, group_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def listgroup_realm(self, realm_id):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="listgrouprealm {} {} \r\n" . format(self.tokenid, realm_id)
        result = self.sendstring(string)
        if result!=[]:
            return "{}" . format(json.dumps(result))
        else:
            return "Error, {}" . format(result['message'])
        
    def send_group_realm_message(self, realm_id, group_id="xxx", message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgrouprealm {} {} {} {} \r\n" . format(self.tokenid, realm_id, group_id, message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(group_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def send_group_file_realm(self, realm_id, group_id="xxx", filepath="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        
        #check if file exists
        if not os.path.isfile(filepath):
            return "Error, file not found"
        
        # Decode bytes to string
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode('utf-8')
        string="sendgroupfilerealm {} {} {} {} {} \r\n" . format(self.tokenid, realm_id, group_id, filepath, encoded_content)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "file sent to group {}" . format(group_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def leave_group_realm(self, realm_id, group_id="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="leavegrouprealm {} {} {} \r\n" . format(self.tokenid, realm_id, group_id)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "group {} left" . format(group_id)
        else:
            return "Error, {}" . format(result['message'])
        
    def inbox(self, inbox_with="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} {} \r\n" . format(self.tokenid, inbox_with)
        result = self.sendstring(string)
        if result['status']=='OK':
            if result['message'] == []:
                return "{}" . format(json.dumps("No message"))
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])
    
    def inboxgroup(self,group_id="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxgroup {} {} \r\n" . format(self.tokenid, group_id)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])
        
    def inbox_realm(self, realmid, inbox_with="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxrealm {} {} {} \r\n" . format(self.tokenid, realmid, inbox_with)
        result = self.sendstring(string)
        if result['status']=='OK':
            if result['message'] == []:
                return "{}" . format(json.dumps("No message"))
            return "{}" . format(json.dumps(result['message']))
        
    def inboxgroup_realm(self, realmid, group_id="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxgrouprealm {} {} {} \r\n" . format(self.tokenid, realmid, group_id)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])

if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))

