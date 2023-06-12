from flet import *
import pickle
from util.extras import *
from pages.mainpage import MainPage
from pages.login import LoginPage
from pages.signup import SignupPage
from pages.dashboard import DashboardPage
from pages.group_list import GroupChatList
from pages.group_chat import GroupChat
# from pages.private_chat import 
from service.chat_cli import ChatClient
import sys
import asyncio


if (len(sys.argv) > 1):
    TARGET_IP = '0.tcp.ap.ngrok.io'
    TARGET_PORT = int(sys.argv[1])
else:
    TARGET_IP = "127.0.0.1"
    TARGET_PORT = 1111

async def save_token(token):
  try:
    with open("token.pkl", "wb") as f:
      pickle.dump(token, f)
    return 'Saved'
  except:
    return None 



async def load_token():
  try:
    with open("token.pkl", "rb") as f:
      stored_token = pickle.load(f)
    return stored_token
  except:
    return None



class WindowDrag(UserControl):
  def __init__(self):
    super().__init__()
    # self.color = color
  def build(self):
    return Container(content=WindowDragArea(height=10,content=Container(bgcolor='white')))


class App(UserControl):
  def __init__(self,pg:Page):
    super().__init__()

    pg.window_title_bar_hidden = True
    pg.window_frameless = True
    pg.window_title_bar_buttons_hidden = True
    pg.bgcolor = colors.TRANSPARENT
    pg.window_bgcolor = colors.TRANSPARENT
    pg.fonts = {
    "SF Pro Bold":"fonts/SFProText-Bold.ttf",
    "SF Pro Heavy":"fonts/SFProText-Heavy.ttf",
    "SF Pro HeavyItalic":"fonts/SFProText-HeavyItalic.ttf",
    "SF Pro Light":"fonts/SFProText-Light.ttf",
    "SF Pro Medium":"fonts/SFProText-Medium.ttf",
    "SF Pro Regular":"fonts/SFProText-Regular.ttf",
    "SF Pro Semibold":"fonts/SFProText-Semibold.ttf",
    "SF Pro SemiboldItalic":"fonts/SFProText-SemiboldItalic.ttf",
    
    
    "Poppins ThinItalic":"fonts/poppins/Poppins-ThinItalic.ttf",
    "Poppins Thin":"fonts/poppins/Poppins-Thin.ttf",
    "Poppins Semibold":"fonts/poppins/Poppins-Semibold.ttf",
    "Poppins SemiboldItalic":"fonts/poppins/Poppins-SemiboldItalic.ttf",
    "Poppins Regular":"fonts/poppins/Poppins-Regular.ttf",
    "Poppins MediumItalic":"fonts/poppins/Poppins-MediumItalic.ttf",
    "Poppins Medium":"fonts/poppins/Poppins-Medium.ttf",
    "Poppins LightItalic":"fonts/poppins/Poppins-LightItalic.ttf",
    "Poppins Light":"fonts/poppins/Poppins-Light.ttf",
    "Poppins Italic":"fonts/poppins/Poppins-Italic.ttf",
    "Poppins ExtraLightItalic":"fonts/poppins/Poppins-ExtraLightItalic.ttf",
    "Poppins ExtraLight":"fonts/poppins/Poppins-ExtraLight.ttf",
    "Poppins ExtraBold":"fonts/poppins/Poppins-ExtraBold.ttf",
    "Poppins ExtraBoldItalic":"fonts/poppins/Poppins-ExtraBoldItalic.ttf",
    "Poppins BoldItalic":"fonts/poppins/Poppins-BoldItalic.ttf",
    "Poppins Bold":"fonts/poppins/Poppins-Bold.ttf",
    "Poppins BlackItalic":"fonts/poppins/Poppins-BlackItalic.ttf",
    "Poppins Black":"fonts/poppins/Poppins-Black.ttf",
  }
    pg.window_width = base_width
    pg.window_height = base_height



    self.pg  = pg
    self.pg.spacing = 0
    self.delay = 0.1
    self.chat_client = ChatClient(TARGET_IP, TARGET_PORT)
    self.anim = animation.Animation(300,AnimationCurve.EASE_IN_OUT_CUBIC)

    self.main_page = MainPage(self.switch_page)
    
    self.screen_views = Stack(
        expand=True,
        controls=[
         # self.main_page if not auth else DashboardPage(self.switch_page, auth["username"]),
          self.main_page
        ]
      )

    self.init_helper()

  def switch_page(self,e):
    if e.control.data == 'register':
      name = self.signup.name_box.value
      password = self.signup.password_box.value
      country = self.signup.country_box.value

      response = self.chat_client.register(name,name, password,country)

      if response['status'] == 'OK':
        self.screen_views.controls.clear()
        self.screen_views.controls.append(DashboardPage(self.switch_page,name))
        self.screen_views.update()
      else:
        self.signup.error = Row(
          controls=[
            Image(
              src='assets/icons/danger.png',
            ),
            Text(
              value=response['message'],
              color='red',
              font_family='poppins regular'

            )
          ]
        )
        self.signup.main_content.controls.insert(1,self.main_page.error)

        self.signup.update()
      return
    elif e.control.data == 'moveto_dashboard':
      id = self.chat_client.tokenid
      self._name = self.chat_client.username
      self._username = self.chat_client.username
      self.screen_views.controls.clear()
      self.dashboard = DashboardPage(self.switch_page,username=self._username)
      self.screen_views.controls.append(self.dashboard)
      self.screen_views.update()

    elif e.control.data == 'open_groups':
      response = self.chat_client.listgroup()
      if response['status'] == 'OK':
        self.grouplist = GroupChatList(self.switch_page,response['message'])
        self.screen_views.controls.append(self.grouplist)
        self.screen_views.update()
        if self.groupchat != None and self.groupchat.refresher != None:
          self.groupchat.refresher.join()

    elif e.control.data.split(' ')[0] == 'open_group_chat':
      group_id = e.control.data.split(' ')[1]
      group_name = e.control.data.split(' ')[2]
      response = self.chat_client.inboxgroup(group_id)
      if response['status'] == 'OK':
        self.groupchat = GroupChat(self.switch_page, group_id,group_name, self.chat_client, self.screen_views)
        self.screen_views.controls.append(self.groupchat)
        self.screen_views.update()
      else:
        print('error')

    elif e.control.data.split(' ')[0] == 'send_message_group':
      group_id = e.control.data.split(' ')[1]
      sent_message = self.groupchat.user_text_input.content.value
      response = self.chat_client.sendmessagegroup(group_id, sent_message)
      if response['status'] == 'OK':
        self.groupchat.update_messages()
        self.screen_views.update()
      else:
        print('error')

    elif e.control.data.split(' ')[0] == 'leave_group':
      group_id = e.control.data.split(' ')[1]
      response = self.chat_client.leavegroup(group_id)
      if response['status'] == 'OK':
        response = self.chat_client.listgroup()
        if response['status'] == 'OK':
          self.grouplist = GroupChatList(self.switch_page,response['message'])
          self.screen_views.controls.append(self.grouplist)
          self.screen_views.update()
          if self.groupchat != None and self.groupchat.refresher != None:
            self.groupchat.refresher.join()
      else:
        print('error')
    
    elif e.control.data == 'create_group':
      group_name = self.grouplist.create_group_input.content.value
      response = self.chat_client.creategroup(group_name)
      if response['status'] == 'OK':
        response = self.chat_client.listgroup()
        if response['status'] == 'OK':
          self.grouplist = GroupChatList(self.switch_page,response['message'])
          self.screen_views.controls.append(self.grouplist)
          self.screen_views.update()
          if self.groupchat != None and self.groupchat.refresher != None:
            self.groupchat.refresher.join()
      else:
        print('error')

    elif e.control.data.split(' ')[0] == 'invite_user':
      group_id = e.control.data.split(' ')[1]
      invited_username = self.groupchat.user_invite_input.content.value
      response = self.chat_client.invitegroup(group_id,invited_username)
      if response['status'] == 'OK':
        print(response['message'])
      else:
        print('error')

    elif e.control.data == 'process_login':
      username = self.main_page.username_input.content.value
      password = self.main_page.password_input.content.value

      response = self.chat_client.login(username, password)
      if response['status'] == 'OK':
        id = self.chat_client.tokenid
        self._name = self.chat_client.username
        self._username = self.chat_client.username
        self.screen_views.controls.clear()
        self.dashboard = DashboardPage(self.switch_page,username=self._username)
        self.screen_views.controls.append(self.dashboard)
        self.screen_views.update()
      else:
        self.main_page.username_input.bgcolor = input_error_bg
        self.main_page.username_input.border = border.all(width=2,color=input_error_outline)
        self.main_page.error = Row(
          controls=[
            Image(
              src='assets/icons/danger.png',
            ),
            Text(
              value=response['message'],
              color='red',
              font_family='poppins regular'

            )
          ]
        )
        self.main_page.main_content.controls.insert(1,self.main_page.error)

        self.main_page.update()
        # self.main_page.username_input.update()

    elif e.control.data == 'register_clicked':
      self.signup = SignupPage(switch_page=self.switch_page)
      self.screen_views.controls.append(self.signup)
      self.screen_views.update()
        
      
    elif e.control.data == 'main_page':
      self.screen_views.controls.clear()
      self.screen_views.controls.append(self.main_page)
      self.screen_views.update()
      
    elif e.control.data == 'login_clicked':
      password = self.login_page.pwd_input.content.value
      username = self.login_page.username


      if true:
        self.screen_views.controls.clear()
        self.screen_views.controls.append(DashboardPage(self.switch_page,username))
        self.screen_views.update()

      else:
        self.login_page.login_box.controls.insert(4,self.login_page.error)  
        self.login_page.pwd_input.bgcolor = input_error_bg
        self.login_page.pwd_input.border=border.all(width=2, color=input_error_outline)
        self.login_page.pwd_input.update()
        self.login_page.login_box.update()

    elif e.control.data == 'logout':
      try:
        os.remove('token.pkl')  
      except:
        pass
      self.screen_views.controls.clear()
      self.screen_views.controls.append(self.main_page)
      self.screen_views.update()      

  def init_helper(self):
    self.pg.add(
      WindowDrag(),
      self.screen_views 
    )


app(target=App,assets_dir='assets')