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
