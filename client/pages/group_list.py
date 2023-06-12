from flet import *
from util.extras import *
import json

class GroupChatList(Container):
  def __init__(self,switch_page,group_list):
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

    group_containers = Column(
      alignment='center',
      horizontal_alignment='center',
    )

    group_buttons = []
    
    group_list = json.loads(group_list)
    # print(group_list)
    for group in group_list:
      butt = Container(
        bgcolor='#f0f0f0',
        on_click=switch_page,
        data = 'open_group_chat ' + str(group) + ' ' + group_list[group],
        border_radius=10,
        width=btn_width,
        height=btn_height,
        padding=padding.only(top=15,left=10,right=10,),
        content=Text(
          value=group_list[group]
        )
      )
      group_buttons.append(butt)
    
    group_containers.controls= group_buttons

    self.user_search_input = Container(
      height=btn_height,
      bgcolor='#f0f0f0',
      border_radius=10,
      content=TextField(
        hint_text='Search username to message',
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
              value='GROUPS!',
              color=white
            ),
            group_containers,
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
            )
          ]
        )
        
      )
      