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
    def __init__(self, screen, sock, key, ui_queue,players, username):
        self.ui_queue = ui_queue
        self.screen = screen
        self.sock = sock
        self.key = key
        self.players = dict(players)
        self.username = username

        self.host = False

        print("hello")


        self.start_room_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_orangeyellow.png')
        self.refresh_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_magenta.png')
        self.exit_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/Button_back_red.png')
        self.exit_button_image = pygame.transform.flip(self.exit_button_image, True, False)
        self.join_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_orangeyellow.png')
        self.player_img = [
             pygame.image.load(r'../Assets/Pictures/name1.png'),
             pygame.image.load(r'../Assets/Pictures/name2.png'),
             pygame.image.load(r'../Assets/Pictures/name3.png'),
             pygame.image.load(r'../Assets/Pictures/name2.png'),
            ]

        self.player_slots = [(100,200),(300,20),(450,200),(300,300)]

        self.title = "Waiting Room"

        self.to_return = None


        self.background = pygame.image.load(r'../Assets/Pictures/uno_background.jpg')
        self.crown = pygame.image.load(r'../Assets/Pictures/crown.png')

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

    def build_start_button(self):

        start_button = Button(
            pos=(100 * scale, 300 * scale),
            text_input="START",
            font=get_font(30),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.start_room_image,
            text_pos=(45 * scale, 41 * scale)

        )

        return  start_button

    def draw_players(self):
        for username, player_id in self.players.items():
            pos_x ,pos_y = self.player_slots[player_id]

            img = self.player_img[player_id]
            self.screen.blit(img, (pos_x * scale, pos_y * scale))

            name = get_font(30).render(username, True, (255, 255, 255))
            self.screen.blit(name, (pos_x * scale + 70, pos_y * scale + 15))

    def handle_del(self,username):
        try:
            to_send = f"DEL|{username}"
            print("sending:", to_send)
            to_send = to_send.encode('utf-8')
            to_send = pad_massage(to_send)
            encrypted_to_send = encrypt(to_send, self.key)
            send_with_size(self.sock, encrypted_to_send)

        except Exception:
            MassageBox(self.screen, "ERROR", "an unexpected \n error occurred!")

    def run(self):
        pygame.display.set_caption(self.title)
        if len(self.players) == 1:
            self.host = True

        while True:
            mouse_pos = pygame.mouse.get_pos()


            while self.ui_queue:
                event = self.ui_queue[0]
                print(event.get_where()  + " , " + str(type(event.get_where())))
                if event.get_where() == "wait_room":
                    if event.get_action() == "messagebox":
                        MassageBox(self.screen, event.get_title(), event.get_message())
                        self.ui_queue.remove(event)
                    elif event.get_action() == "new_player":
                        new_player = event.get_data()
                        print(new_player)
                        if new_player:
                            for name,pid in new_player.items():
                                self.players[name] = int(pid)
                            print("current players:", self.players)
                        self.ui_queue.remove(event)
                    else:
                        self.ui_queue.remove(event)
                else:
                    break

            self.screen.blit(self.background, (0, 0))
            self.draw_players()
            self.screen.blit(self.crown, (165 * scale, 175 * scale))

            buttons = self.build_button()
            if self.host:
                buttons.insert(0,self.build_start_button())
            for button in buttons:
                button.changeColor(mouse_pos)
                button.update(self.screen)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_del(self.username)
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if buttons[-1].checkForInputs(mouse_pos):

                        self.handle_del(self.username)
                        return


            pygame.display.flip()