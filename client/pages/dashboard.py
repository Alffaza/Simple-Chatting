from flet import *
from util.extras import *

class DashboardPage(Container):
  def __init__(self,switch_page,username):
    super().__init__()
    self.offset = transform.Offset(0,0,)
    self.username = username
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
              value='Welcome {}!'.format(username),
              color=white
            ),
            self.user_search_input,
            Container(
              on_click=self.switch_page,
              data = 'open_private_chat',
              height=btn_height,
              width=btn_width,
              bgcolor=base_green,
              border_radius=10,
              alignment=alignment.center,
              content=Text(
              value='Find user',
              font_family='Poppins Medium',
              size=18,
              )
            ),
            Container(
              on_click=self.switch_page,
              data = 'open_groups',
              height=btn_height,
              width=btn_width,
              bgcolor=base_green,
              border_radius=10,
              alignment=alignment.center,
              content=Text(
              value='Check groups',
              font_family='Poppins Medium',
              size=18,
              )
            ),
            Container(
              on_click= self.switch_page,
              data ='logout',
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
      