from flet import *
import json
import time
import threading
from util.extras import *

class GroupChat(Container):
  def update_messages(self):
    print(self.chat_client.inboxgroup(self.group_id))
    self.messages_containers = []
    self.refresh_delay = 5
    white = '#ffffff'
    print(len(self.messages_json))
    for msg in self.messages_json:
      m = Container(
        bgcolor='#d0d0d0' if msg['sender'] != self.chat_client.username else '#eeee33',
        border_radius=10,
        padding=padding.only(top=10,left=10,right=10,bottom=10),
        width=btn_width,
        content=Text(
          value='{}: {}'.format(msg['sender'], msg['message'][:-3])
        )
      )
      self.messages_containers.append(m);
    
    self.messages_container_main = Column(
      alignment='center',
      horizontal_alignment='center',
    )

    self.messages_container_main.controls = self.messages_containers

    self.error = Row(
      controls=[
        Image(
          src='assets/icons/danger.png',
          # scale=0.8,

        ),
        Text(
          value='',
          color='red',
          font_family='poppins regular'

        )
      ]
    )

    self.user_text_input = Container(
      height=btn_height,
      width=btn_width-60,
      bgcolor='#f0f0f0',
      border_radius=10,
      content=TextField(
        hint_text='Enter message',
        hint_style=TextStyle(
          size=16,
          font_family='Poppins Regular',
          color=input_hint_color,
        ),
        text_style=TextStyle(
          size=16,
          font_family='Poppins Regular',
          color=input_hint_color,
        ),
        border=InputBorder.NONE,
        content_padding=content_padding
      )
    )

    self.user_invite_input = Container(
      height=btn_height,
      width=btn_width-60,
      bgcolor='#f0f0f0',
      border_radius=10,
      content=TextField(
        hint_text='username to invite',
        hint_style=TextStyle(
          size=16,
          font_family='Poppins Regular',
          color=input_hint_color,
        ),
        text_style=TextStyle(
          size=16,
          font_family='Poppins Regular',
          color=input_hint_color,
        ),
        border=InputBorder.NONE,
        content_padding=content_padding
      )
    )

    self.content = Container(
      
        height=base_height,
        width=base_width,
        bgcolor=base_color,
        clip_behavior=ClipBehavior.ANTI_ALIAS,
        expand=True,
        border_radius=br,
        
        content=Column(
          alignment='top',
          horizontal_alignment='center',
          scroll=ScrollMode.AUTO,
          controls=[
            Text(
              value='{}'.format(self.group_name),
              color=white
            ),
            self.messages_container_main,
            Row(
            vertical_alignment='bottom',
            alignment='center',
            controls=[
              Container(
                on_click= self.switch_page,
                data ='open_groups',
                height=30,
                width=30,
                border_radius=10,
                bgcolor='#ffffff',
                content=Icon(
                  icons.LOGOUT_OUTLINED,
                  color='black'
                )
              ),
            self.user_text_input,
            Container(
              on_click= self.switch_page,
              data ='send_message_group ' + str(self.group_id),
              height=30,
              width=30,
              border_radius=10,
              bgcolor='#ffffff',
              content=Icon(
                icons.SEND,
                color='black'
              )
            )
          ] 
        ), Row(
            vertical_alignment='bottom',
            alignment='center',
            controls=[
              Container(
                on_click= self.switch_page,
                data ='leave_group ' + str(self.group_id),
                height=30,
                width=30,
                border_radius=10,
                bgcolor='#ff0000',
                content=Icon(
                  icons.LOGOUT_OUTLINED,
                  color='black'
                )
              ),
            self.user_invite_input,
            Container(
              on_click= self.switch_page,
              data ='invite_user ' + str(self.group_id),
              height=30,
              width=30,
              border_radius=10,
              bgcolor='#00ff00',
              content=Icon(
                icons.SEND,
                color='black'
              )
            )
          ] 
        )
          ]
        )
        
        
      )

  def __init__(self,switch_page,group_id, group_name, chat_client, screen_views=None):
    super().__init__()
    self.offset = transform.Offset(0,0,)
    self.group_id = group_id
    self.group_name = group_name
    self.switch_page = switch_page
    self.expand = True
    self.chat_client = chat_client


    messages = self.chat_client.inboxgroup(self.group_id)['message']
    self.messages_json = json.loads(messages)
    self.update_messages()

    self.message_count = len(self.messages_json)
    def constant_refresh_messages():
      while True:
        time.sleep(self.refresh_delay)
        messages = self.chat_client.inboxgroup(self.group_id)['message']        
        self.messages_json = json.loads(messages)
        if self.message_count != len(self.messages_json):
          self.update_messages()
          screen_views.update()
          self.message_count = len(self.messages_json)
          print('refresh')

    self.refresher = threading.Thread(target=constant_refresh_messages)
    self.refresher.start()
    # while True:
    #   time.sleep(self.refresh_delay)
    #   self.update_messages()
    #   print('refresh')
    
      