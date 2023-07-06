# Simple-Chatting

Final project for net programming class using python and flet

## COMMANDS

### login
this command can access without authentication
```
auth {username} {password}
```
- username can't same with other user

### register
this command can access without authentication
```
register {username} {real_name} {password} {country}
```
- real_name can't contain space


### my private chat list
this command only can access after authentication
```
listpc
```
this command return list of private chat from other user

### send message to another user
this command only can access after authentication
```
send {recipient username} {message}
```
- recipient user must already registered


### send file to another user
this command only can access after authentication
```
sendfile {recipient username} {file path}
```
- recipient user must already registered
- file path must be absolute path


### create group
this command only can access after authentication
```
creategroup {group name}
```
- group name can be same with other group name

### my group list
this command only can access after authentication
```
listgroup
```
this command return list of group id and its group name


### invite user to group
this command only can access after authentication
```
invitegroup {group id} {username}
```
- group id must already created, you can check it with listgroup command
- username must already registered


### send message to group
this command only can access after authentication
```
sendg {group id} {message}
```
- group id must already created, you can check it with listgroup command


### check my inbox from specific user
this command only can access after authentication
```
inbox {username}
```
- username must already registered
- if username not in private chat list, it will return "No message"

### check my inbox from specific group
this command only can access after authentication
```
inboxgroup {group id}
```
- group id must already created, you can check it with listgroup command


## COMMANDS AT REALMS BEETWEEN
this command only can access after authentication

### add realm
```
addrealm {realm name} {realm address} {realm port}
```
- realm name can't contain space
- realm name can't same with other realm name


### list realm
```
listrealm
```

### send private message to another user at another realm
```
sendpcrealm {realm name} {recipient username} {message}
```
- realm name must already added, you can check it with listrealm command

### get list of private chat from another user at another realm
```
listpcrealm {realm name}
```
- realm name must already added, you can check it with listrealm command

### send file to another user at another realm
```
sendfilerealm {realm name} {recipient username} {file path}
```
- realm name must already added, you can check it with listrealm command

### create group at another realm
```
creategrouprealm {realm name} {group name}
```
- realm name must already added, you can check it with listrealm command

### list group at another realm
```
listgrouprealm {realm name}
```
- realm name must already added, you can check it with listrealm command

### invite user to group at another realm
```
invitegrouprealm {realm name} {group id} {username}
```
- realm name must already added, you can check it with listrealm command
- group id must already created, you can check it with listgrouprealm command

### send message to group at another realm
```
sendgrouprealm {realm name} {group id} {message}
```
- realm name must already added, you can check it with listrealm command
- group id must already created, you can check it with listgrouprealm command

### send file to group at another realm
```
sendgroupfilerealm {realm name} {group id} {file path}
```
- realm name must already added, you can check it with listrealm command
- group id must already created, you can check it with listgrouprealm command

### check my inbox from specific user at another realm
```
inboxrealm {realm name} {username}
```
- realm name must already added, you can check it with listrealm command
- username must already contact you, you can check it with listpcrealm command

### check my inbox from specific group at another realm
```
inboxgrouprealm {realm name} {group id}
```
- realm name must already added, you can check it with listrealm command
- group id must already created and you are member of that group, you can check it with listgrouprealm command