import pygame
import json

from Helpers.tcp_by_size import send_with_size
from UI.UI_helpers.Button import Button
from globals import *
from UI.UI_helpers.massagebox import MassageBox
from Encryption.AES import *

def get_font(size):
    return pygame.font.Font(r'..\Assets/Fonts/ThaleahFat_TTF.ttf', size)

class WaitingRoom:
    def __init__(self, screen, sock, key, ui_queue,players):
        self.ui_queue = ui_queue
        self.screen = screen
        self.sock = sock
        self.key = key
        self.players = players


        self.create_room_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_orangeyellow.png')
        self.refresh_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_magenta.png')
        self.exit_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/Button_back_red.png')
        self.exit_button_image = pygame.transform.flip(self.exit_button_image, True, False)
        self.join_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_orangeyellow.png')
        self.user_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_fx_multiuser_orange.png')

        self.title = "Waiting Room"

        self.to_return = None


        self.background = pygame.image.load(r'../Assets/Pictures/uno_background.jpg')
        self.run()

    def build_button(self):


        exit_button = Button(
            pos=(590 * scale, 35 * scale),
            text_input="",
            font=get_font(30),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.exit_button_image,
            text_pos=(45 * scale, 41 * scale)
        )

        return [ exit_button]



    def run(self):
        pygame.display.set_caption(self.title)


        while True:
            mouse_pos = pygame.mouse.get_pos()


            while self.ui_queue:
                event = self.ui_queue[0]
                if event.get_where() == "room":
                    if event.get_action() == "messagebox":
                        MassageBox(self.screen, event.get_title(), event.get_message())
                        self.ui_queue.remove(event)
                    elif event.get_action() == "new_room":
                        self.ui_queue.remove(event)
                    else:
                        self.ui_queue.remove(event)
                else:
                    break

            self.screen.blit(self.background, (0, 0))

            for player, ids in self.players.items():
                if ids == 1:
                    self.screen.blit(self.user_image,(200,200))



            buttons = self.build_button()
            for button in buttons:
                button.changeColor(mouse_pos)
                button.update(self.screen)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if buttons[-1].checkForInputs(mouse_pos):
                        return


            pygame.display.flip()