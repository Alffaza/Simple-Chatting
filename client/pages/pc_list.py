from flet import *
from util.extras import *
import json

class PrivateChatList(Container):
  def __init__(self,switch_page,chats):
    super().__init__()
    self.offset = transform.Offset(0,0,)
    self.switch_page = switch_page
    self.expand = True
    white = '#ffffff'

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

    chat_containers = Column(
      alignment='center',
      horizontal_alignment='center',
    )

    chat_buttons = []
    chats = json.loads(chats)
    chats = chats['private_chat']
    # print(chats)
    for chat in chats:
      butt = Container(
        bgcolor='#f0f0f0',
        on_click=switch_page,
        data = 'open_private_chat ' + chat,
        border_radius=10,
        width=btn_width,
        height=btn_height,
        padding=padding.only(top=15,left=10,right=10,),
        content=Text(
          value=chat
        )
      )
      chat_buttons.append(butt)
    
    chat_containers.controls= chat_buttons

    self.create_chat_input = Container(
      height=btn_height,
      width=btn_width-60,
      bgcolor='#f0f0f0',
      border_radius=10,
      content=TextField(
        hint_text='Chat with another user',
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
          alignment='center',
          horizontal_alignment='center',
          controls=[
            Text(
              value='chats!',
              color=white
            ),
            Row(
            vertical_alignment='bottom',
            alignment='center',
            controls=[
            self.create_chat_input,
            Container(
              on_click= self.switch_page,
              data ='create_new_private_chat',
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
        ),
            chat_containers,
            Container(
              on_click= self.switch_page,
              data ='moveto_dashboard',
              height=50,
              width=100,
              border_radius=30,
              bgcolor='#ffffff',
              content=Icon(
                icons.LOGOUT_OUTLINED,
                color='black'
              )
            ),
          ]
        )
        
      )
      