import base64
import socket
import os
import json
import sys

class ChatClient:
    def __init__(self, target_ip='127.0.0.1', target_port=1111):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (target_ip,target_port)
        self.sock.connect(self.server_address)
        self.tokenid=""
        print('using ' + target_ip + ':' +str(target_port))

    def is_success(self, message):
        return {'status':'OK', 'message': message}
    def is_fail(self, message):
        return {'status':'ERROR', 'message': message}
        
    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
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
            elif (command=='sendg'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessagegroup(group_id,message)
            elif (command=='sendgfile'):
                group_id = j[1].strip()
                filepath = j[2].strip()
                return self.sendfilegroup(group_id,filepath)
            elif (command=='leavegroup'):
                group_id = j[1].strip()
                return self.leavegroup(group_id)
            elif (command=='register'):
                return self.register(j[1].strip(), j[2].strip(), j[3].strip(), j[4].strip())
            elif (command=='inbox'):
                return self.inbox()
            elif (command=='inboxgroup'):
                group_id = j[1].strip()
                return self.inboxgroup(group_id)
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
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.username = username
            self.tokenid=result['tokenid']
            return self.is_success( "username {} logged in, token {} " .format(username,self.tokenid))
        else:
            return self.is_fail("Error {}". format(result['message']))
        
    def register(self, username, real_name, password, country):
        string = "register {} {} {} {}\r\n" . format(username, real_name, password, country)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success( "successfully created account {}" . format(username))
        else:
            return self.is_fail( "Error, {}" . format(result['message']))
        
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("message sent to {}" . format(usernameto))
        else:
            return self.is_fail("Error, {}" . format(result['message']))

    #create function sendfile from specific path
    def sendfile(self,usernameto="xxx",filepath="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        
        #check if file exists
        if not os.path.isfile(filepath):
            return "Error, file not found"
        
        # Decode bytes to string
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode('utf-8')
        string="sendfile {} {} {} {} \r\n" . format(self.tokenid,usernameto,filepath,encoded_content)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("file sent to {}" . format(usernameto))
        else:
            return self.is_fail("Error, {}" . format(result['message']))

    def creategroup(self, group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="creategroup {} {} \r\n" . format(self.tokenid, group_name)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("{}" . format(result['message']))
        else:
            return self.is_fail("Error, {}" . format(result['message']))

    def listgroup(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="listgroup {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("{}" . format(json.dumps(result['groups'])))
        else:
            return self.is_fail("Error, {}" . format(result['message']))
        
    def invitegroup(self,group_id="xxx",username="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="invitegroup {} {} {} \r\n" . format(self.tokenid,group_id,username)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("user {} invited to group {}" . format(username,group_id))
        else:
            return self.is_fail("Error, {}" . format(result['message']))

    def sendmessagegroup(self,group_id="xxx",message="xxx"):
        if (self.tokenid==""):
            return self.is_fail("Error, not authorized")
        string="sendgroup {} {} {} \r\n" . format(self.tokenid,group_id,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("message sent to {}" . format(group_id))
        else:
            return self.is_fail("Error, {}" . format(result['message']))
        
    def sendfilegroup(self,group_id="xxx",filepath="xxx"):
        if (self.tokenid==""):
            return self.is_fail("Error, not authorized")
        
        #check if file exists
        if not os.path.isfile(filepath):
            return self.is_fail("Error, file not found")
        
        # Decode bytes to string
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode('utf-8')
        string="sendgfile {} {} {} {} \r\n" . format(self.tokenid,group_id,filepath,encoded_content)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("file sent to {}" . format(group_id))
        else:
            return self.is_fail("Error, {}" . format(result['message']))
        
    def leavegroup(self,group_id="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="leavegroup {} {} \r\n" . format(self.tokenid,group_id)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("group {} left" . format(group_id))
        else:
            return self.is_fail("Error, {}" . format(result['message']))
        
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("{}" . format(json.dumps(result['messages'])))
        else:
            return self.is_fail("Error, {}" . format(result['message']))
    
    def inboxgroup(self,group_id="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inboxgroup {} {} \r\n" . format(self.tokenid,group_id)
        result = self.sendstring(string)
        if result['status']=='OK':
            return self.is_success("{}" . format(json.dumps(result['message'])))
        else:
            return self.is_fail("Error, {}" . format(result['message']))


if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))

