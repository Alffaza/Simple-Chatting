from flet import *
from util.extras import *


class MainPage(Container):
  def __init__(self,switch_page):

    super().__init__()
    self.offset = transform.Offset(0,0,)
    self.switch_page = switch_page
    self.error_msg = ''
    self.error = Row(
      controls=[
        Image(
          src='assets/icons/danger.png',
          # scale=0.8,

        ),
        Text(
          value=self.error_msg,
          color='red',
          font_family='poppins regular'

        )
      ]
    )
    
    self.expand = True

    self.title_text = Container(
      content=Text(
        value= 'Chatting with Kelompok 1',
        color='#ffffff',
        style=TextStyle(
          size=32,
          font_family='Poppins Regular',
          color='#ffffff'
        ),
      )
    )

    self.username_input = Container(
      height=btn_height,
      bgcolor='white',
      border_radius=10,
      content=TextField(
        on_focus=self.field_in_focus,
        hint_text='Username',
        hint_style=TextStyle(
          size=16,
          font_family='Poppins Regular',
          color=input_hint_color
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

    self.password_input = Container(
      height=btn_height,
      bgcolor='white',
      border_radius=10,
      content=TextField(
        on_focus=self.field_in_focus,
        hint_text='Password',
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

    self.main_content = Column(
      controls=[
        self.title_text,
        self.username_input,
        self.password_input,
        Container(height=0),
        Container(
          on_click=self.switch_page,
          data = 'process_login',
          height=btn_height,
          width=btn_width,
          bgcolor=base_green,
          border_radius=10,
          alignment=alignment.center,
          content=Text(
            value='Continue',
            font_family='Poppins Medium',
            size=18,
          )
        ),
        Container(
          on_click=self.switch_page,
          data = 'register_clicked',
          height=btn_height/2,
          width=btn_width/2,
          bgcolor=base_green,
          border_radius=10,
          alignment=alignment.center,
          content=Text(
            value='Register',
            font_family='Poppins Medium',
            size=9,
          )
        ),
      ]
    )
                  
    self.content = Container(
        # padding=padding.symmetric(horizontal=8,vertical=20),
        height=base_height,
        width=base_width,
        bgcolor=base_color,
        clip_behavior=ClipBehavior.ANTI_ALIAS,
        expand=True,
        border_radius=br,
        content=Stack(
          controls=[
            Container(
              height=base_height,
              width=base_width,
              left=60,
              top=-200,
              content=Image(
                src='assets/images/2.png',
                scale=0.9,
              )
            ),
            
            Container(
              height=base_height,
              width=base_width,
              # bgcolor='red'
              padding=padding.only(top=30,left=10,right=10,),
              content=Column(
                controls=[
                  Container(height=160),
                  Container(
                    margin=margin.only(left=20),
                    content=Text(
                      value='Hi!',
                      font_family='Poppins Bold',
                      size=30,
                    ),
                  ),
                  Container(height=2),
                  Container(
                    padding=20,
                    bgcolor='#cc2d2b2c',
                    border_radius=10,
                    content=self.main_content,
                  ),
                ]
              )

            )
           
          ]
        )
        
      )
    
  def field_in_focus(self,e):

    y = self.error in self.main_content.controls
    if y == True:
      self.main_content.controls.remove(self.error)

      self.username_input.bgcolor = 'white'
      self.username_input.border = None
      self.main_content.update()