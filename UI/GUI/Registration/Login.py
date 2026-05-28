import pygame
from UI.UI_helpers.Button import Button
from UI.UI_helpers.Text_Input import TextInput
from UI.UI_helpers.massagebox import MassageBox
from UI.GUI.Email_new_pass import EmailNewPass
from Encryption.AES import *
from globals import *
from Helpers.tcp_by_size import *

#get the custom font
def get_font(size):
    return pygame.font.Font(r'..\Assets/Fonts/ThaleahFat_TTF.ttf', size)

#get an arial font
def get_arial_font(size):
    return pygame.font.SysFont("Arial", size)

#the login page
class Login:
    def __init__(self, screen, background,sock,key,ui_queue):
        self.ui_queue = ui_queue
        self.screen = screen
        self.background = background
        self.sock = sock
        self.key = key

        #load the login box
        self.box = pygame.image.load(r'..\Assets\Pictures\box.PNG')
        self.box_rect = self.box.get_rect()
        self.box_rect.center = (320 * scale, 190 * scale)

        #fills the background with transparent black
        self.overlay = pygame.Surface((SIZE_WIDTH * scale, SIZE_HEIGHT * scale), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        self.title = "login"

        self.input_box = pygame.image.load(r'..\Assets\Pictures\input_box.PNG')


        #the user's inputs
        self.username = ""
        self.password = ""

        #in what box the user in
        self.username_active = False
        self.password_active = False

        #loads the images
        self.login_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_orangeyellow.png')
        self.forgot_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_green.png')
        self.exit_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/Button_back_red.png')
        self.exit_button_image = pygame.transform.flip(self.exit_button_image, True, False)

        self.text_inputs = self.build_text_area()

        self.to_return = None

        self.run()

    #build the input areas
    def build_text_area(self):
        USERNAME = TextInput(pos=(320 * scale, 100 * scale),
                             color="white",
                             font=get_arial_font(30),
                             width=200,
                             image=self.input_box,
                             padding=20)

        PASSWORD = TextInput(pos=(320 * scale, 140 * scale),
                             color="white",
                             font=get_arial_font(30),
                             width=200,
                             image=self.input_box,
                             padding=20,
                             hide=True)

        return [USERNAME, PASSWORD]

    #build the button
    def build_buttons(self):
        login_button = Button(pos=(320 * scale, 200 * scale),
                              text_input="LOGIN",
                              font=get_font(75),
                              base_color="#d7fcd4",
                              hovering_color="white",
                              image=self.login_button_image
        )

        forgot_button = Button(pos=(320 * scale, 260 * scale),
                               text_input="FORGOT PASSWORD?",
                               font=get_font(35),
                               base_color="#d7fcd4",
                               hovering_color="white",
                               image=self.forgot_button_image)

        exit_button = Button(
            pos=(590 * scale, 35 * scale),
            text_input="",
            font=get_font(30),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.exit_button_image,
            text_pos=(45 * scale, 41 * scale)
        )

        return [login_button, forgot_button, exit_button]

    #handle what to send to the server to log in
    def handel_login(self,username,password,sock):
        try:
            to_send = f"LGN|{username}|{password}"
            print("sending:",to_send)
            to_send = to_send.encode('utf-8')
            to_send = pad_massage(to_send)
            encrypted_to_send = encrypt(to_send, self.key)
            send_with_size(sock, encrypted_to_send)
        except Exception:
            MassageBox(self.screen,"ERROR","an unexpected \n error occurred!")


    def run(self):
        pygame.display.set_caption(self.title)
        while True:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.overlay, (0, 0))
            self.screen.blit(self.box, self.box_rect)

            while not len(self.ui_queue) == 0:
                event = self.ui_queue[0]
                if event.get_where() == "login":
                    if event.get_action() == "messagebox":
                        MassageBox(self.screen, event.get_title(), event.get_message())
                    elif event.get_action() == "logged":
                        self.to_return = event.get_message()
                        self.ui_queue.remove(event)
                        self.screen.blit(self.background, (0, 0))
                        pygame.display.flip()
                        return
                    elif event.get_action() == "":
                        pass


            username_text = get_font(20).render('USERNAME:', True, "red")
            username_rect = username_text.get_rect(center=(255 * scale, 100 * scale))
            self.screen.blit(username_text, username_rect)

            password_text = get_font(20).render('PASSWORD:', True, "red")
            password_rect = password_text.get_rect(center=(255 * scale, 140 * scale))
            self.screen.blit(password_text, password_rect)


            for input_text in self.text_inputs:
                input_text.update(self.screen)

            for button in self.build_buttons():
                button.changeColor(mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.text_inputs[0].checkForInputs(mouse_pos):
                        self.username_active = True
                        self.password_active = False

                        self.password = self.text_inputs[1].get_input()

                        self.text_inputs[0].set_active(True)
                        self.text_inputs[1].set_active(False)
                    elif self.text_inputs[1].checkForInputs(mouse_pos):
                        self.password_active = True
                        self.username_active = False

                        self.username= self.text_inputs[0].get_input()

                        self.text_inputs[1].set_active(True)
                        self.text_inputs[0].set_active(False)

                    elif self.build_buttons()[0].checkForInputs(mouse_pos):
                        self.username = self.text_inputs[0].get_input()
                        self.password = self.text_inputs[1].get_input()

                        if self.username == "":
                            MassageBox(self.screen,"ERROR","pls Enter \n username")
                        elif self.password == "":
                            MassageBox(self.screen,"ERROR","pls Enter \n password")
                        else:
                            self.handel_login(self.username, self.password, self.sock)
                    elif self.build_buttons()[1].checkForInputs(mouse_pos):
                        self.to_return = EmailNewPass(self.screen, self.background,self.sock,self.key,self.ui_queue).to_return
                        return
                    elif self.build_buttons()[2].checkForInputs(mouse_pos):
                        return
                    else:
                        self.username_active = False
                        self.password_active = False

                        self.username = self.text_inputs[0].get_input()
                        self.password = self.text_inputs[1].get_input()

                        self.text_inputs[0].set_active(False)
                        self.text_inputs[1].set_active(False)

                if event.type == pygame.KEYDOWN:
                    if self.username_active:

                        if event.key == pygame.K_BACKSPACE:
                            self.text_inputs[0].removeText()
                        elif event.key == pygame.K_RETURN:
                            self.username_active = False
                            self.username = self.text_inputs[0].get_input()
                        elif event.key == pygame.K_LEFT:
                            self.text_inputs[0].scroll_left()
                        elif event.key == pygame.K_RIGHT:
                            self.text_inputs[0].scroll_right()
                        else:
                            self.text_inputs[0].addText(event.unicode)

                    elif self.password_active:

                        if event.key == pygame.K_BACKSPACE:
                            self.text_inputs[1].removeText()
                        elif event.key == pygame.K_RETURN:
                            self.password_active = False
                            self.password = self.text_inputs[1].get_input()
                        elif event.key == pygame.K_LEFT:
                            self.text_inputs[1].scroll_left()
                        elif event.key == pygame.K_RIGHT:
                            self.text_inputs[1].scroll_right()
                        else:
                            self.text_inputs[1].addText(event.unicode)

            pygame.display.flip()