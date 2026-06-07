import time

import pygame

from Helpers.tcp_by_size import send_with_size
from UI.UI_helpers.Button import Button
from globals import *
from UI.UI_helpers.massagebox import MassageBox
from Encryption.AES import *
from UI.UI_helpers.card_selector import *

def get_font(size):
    return pygame.font.Font(r'..\Assets/Fonts/ThaleahFat_TTF.ttf', size)

class PlayingRoom:
    def __init__(self, screen, sock, key, ui_queue,players, username):
        self.ui_queue = ui_queue
        self.screen = screen
        self.sock = sock
        self.key = key
        self.players = dict(players)
        for player,pid in self.players.items():
            self.players[player] = pid + 1
        last_player = next(reversed(self.players))
        self.players[last_player] = 0
        self.username = username

        self.game_start = False

        self.cards = []

        self.card_count = {}

        self.is_turn = False


        self.host = False
        self.change = False

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
        self.card_img = pygame.image.load(r'../Assets/Pictures/uno_card.png')
        self.card_norm_img = pygame.transform.scale(self.card_img, (self.card_img.get_width() * scale, self.card_img.get_height() * scale))

        self.player_slots = [(280,320),(25,150),(300,20),(450,200)]

        self.player_cards = [(50,50),(150,45),(425,20)]

        self.title = "Waiting Room"

        self.to_return = None


        self.background = pygame.image.load(r'../Assets/Pictures/uno_background.jpg')
        self.crown = pygame.image.load(r'../Assets/Pictures/crown.png')
        self.current_card = None

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
            text_pos=(100 * scale, 300 * scale)

        )

        return  start_button

    def build_add_card(self):
        get_card_button = Button(
            pos=(750, 270),
            text_input="",
            font=get_font(30),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.card_norm_img,
            text_pos=(150 * scale, 300 * scale)
        )

        return [get_card_button]

    def draw_players(self):
        for username, player_id in self.players.items():
            pos_x ,pos_y = self.player_slots[player_id]

            img = self.player_img[player_id]
            self.screen.blit(img, (pos_x * scale, pos_y * scale))

            name = get_font(30).render(username, True, (255, 255, 255))
            self.screen.blit(name, (pos_x * scale + 70, pos_y * scale + 15))

    def build_color_buttons(self):
        red_img = pygame.Surface((100, 100))
        red_img.fill((255, 0, 0))

        blue_img = pygame.Surface((100, 100))
        blue_img.fill((0, 0, 255))

        green_img = pygame.Surface((100, 100))
        green_img.fill((0, 255, 0))

        yellow_img = pygame.Surface((100, 100))
        yellow_img.fill((255, 255, 0))

        red_button = Button(
            pos=(250, 300),
            text_input="",
            font=get_font(30),
            base_color="white",
            hovering_color="white",
            image=red_img
        )

        blue_button = Button(
            pos=(400, 300),
            text_input="",
            font=get_font(30),
            base_color="white",
            hovering_color="white",
            image=blue_img
        )

        green_button = Button(
            pos=(250, 450),
            text_input="",
            font=get_font(30),
            base_color="white",
            hovering_color="white",
            image=green_img
        )

        yellow_button = Button(
            pos=(400, 450),
            text_input="",
            font=get_font(30),
            base_color="white",
            hovering_color="white",
            image=yellow_img
        )

        return [red_button,blue_button,green_button,yellow_button]


    def draw_player_cards(self):
        for i,(player,pid) in enumerate(self.players.items()):
            if pid == 0:
                continue

            count = 0

            card_w = 33
            card_h = 49
            pad = 8

            orientation = pid *90
            img = pygame.transform.rotate(self.card_img,orientation)
            hand_x = self.player_cards[pid][0] * scale
            hand_y = self.player_cards[pid][1] * scale
            hand_w = 250
            hand_h = 75

            for name in self.card_count.keys():
                if player == name:
                    count = self.card_count[name]


            if count == 1:
                spacing = 0
            else:
                if pid % 2 == 0:
                    spacing = (hand_w - card_w) / (count - 1) + pad
                else:
                    spacing = (hand_h - card_h) / (count - 1) + pad

            for j in range(1,count+1):
             if pid % 2 == 0:
                 x = hand_x + j * spacing
                 y = hand_y + (hand_h - card_h) / 2
                 self.screen.blit(img, (x, y))
             else:
                y = hand_y + j * spacing
                x = hand_x + (hand_h - card_h) / 2
                self.screen.blit(img, (x, y))



    def build_cards(self):

        if not self.cards:
            return None

        card_w = 33 * scale
        card_h = 49 * scale
        pad = 8

        hand_x = 220 * scale
        hand_y = 280 *scale
        hand_w = 250 * scale
        hand_h = 75 * scale

        card_buttons = {}


        num_cards = len(self.cards)

        if num_cards == 1:
            spacing = 0
        else:
            spacing = (hand_w - card_w) / (num_cards - 1) + pad

        for i,card in enumerate(self.cards):
            x = hand_x + i * spacing
            y = hand_y + (hand_h - card_h) / 2
            surface = get_card(card)
            if surface:
                img_surface = pygame.transform.scale(surface, (int(card_w), int(card_h)))
                btn = Button(
                    pos=(x,y),
                    text_input= "",
                    font=get_font(30),
                    base_color="#d7fcd4",
                    hovering_color="white",
                    image=img_surface,
                    text_pos=(100 * scale, 300 * scale)
                )
                card_buttons[btn] = card
        return card_buttons


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

    def handle_start(self):
        try:
            to_send = f"STR"
            print("sending:", to_send)
            to_send = to_send.encode('utf-8')
            to_send = pad_massage(to_send)
            encrypted_to_send = encrypt(to_send, self.key)
            send_with_size(self.sock, encrypted_to_send)
        except Exception:
            MassageBox(self.screen, "ERROR", "an unexpected \n error occurred!")

    def handle_add(self):
        try:
            to_send = f"ADD"
            print("sending:", to_send)
            to_send = to_send.encode('utf-8')
            to_send = pad_massage(to_send)
            encrypted_to_send = encrypt(to_send, self.key)
            send_with_size(self.sock, encrypted_to_send)
        except Exception:
            MassageBox(self.screen, "ERROR", "an unexpected \n error occurred!")

    def handle_play(self,card):
        try:
            to_send = f"PLAY|{card}"
            print("sending:", to_send)
            to_send = to_send.encode('utf-8')
            to_send = pad_massage(to_send)
            encrypted_to_send = encrypt(to_send, self.key)
            send_with_size(self.sock, encrypted_to_send)
            self.cards.remove(card)

        except Exception:
            MassageBox(self.screen, "ERROR", "an unexpected \n error occurred!")

    def handle_change(self,color):
        try:
            to_send = f"CHAN|{color}"
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
                if event.get_where() == "play_room":
                    print("im_in")
                    if event.get_action() == "messagebox":
                        MassageBox(self.screen, event.get_title(), event.get_message())
                        self.ui_queue.remove(event)

                    elif event.get_action() == "new_player":
                        print("new player")
                        new_player = event.get_data()
                        print(new_player)
                        if new_player:
                            for name,pid in new_player.items():
                                self.players[name] = int(pid)
                            print("current players:", self.players)
                        self.ui_queue.remove(event)

                    elif event.get_action() == "del_player":
                        del_player = event.get_data()
                        if del_player:
                            for name,pid in self.players.items():
                                if name == del_player:
                                    self.players.pop(name)
                                    break
                        self.ui_queue.remove(event)

                    elif event.get_action() == "start":
                        self.game_start = True
                        self.ui_queue.remove(event)

                    elif event.get_action() == "cards":
                        self.cards = event.get_data()
                        self.ui_queue.remove(event)

                    elif event.get_action() == "curr_card":
                        self.current_card = event.get_data()
                        self.ui_queue.remove(event)

                    elif event.get_action() == "stop":
                        self.is_turn = False
                        self.ui_queue.remove(event)

                    elif event.get_action() == "turn":
                        print("turn")
                        self.is_turn = True
                        self.ui_queue.remove(event)

                    elif event.get_action() == "count":
                        self.card_count = event.get_data()
                        self.ui_queue.remove(event)

                    elif event.get_action() == "change":
                        self.change = True
                        self.ui_queue.remove(event)

                    elif event.get_action() == "win":
                        win_text = get_font(300).render(f'{event.get_data()} WON!!', True, "yellow")
                        win_rect = win_text.get_rect(center=(320 * scale, 150 * scale))
                        self.screen.blit(win_text, win_rect)

                        time.sleep(2)

                        self.game_start = False
                        self.ui_queue.remove(event)

                    else:
                        self.ui_queue.remove(event)
                else:
                    break

            self.screen.blit(self.background, (0, 0))
            self.draw_players()
            if self.host:
                self.screen.blit(self.crown, (380 * scale, 320 * scale))
            else:
                self.screen.blit(self.crown, (95 * scale, 125 * scale))

            if self.current_card is not None:
                card_w = 33 * scale
                card_h = 49 * scale
                surface = get_card(self.current_card)
                img_surface = pygame.transform.scale(surface, (int(card_w), int(card_h)))

                self.screen.blit(img_surface, (620, 250))

                self.draw_player_cards()


            buttons = self.build_button()
            if not self.game_start:
                if self.host:
                    buttons.insert(0, self.build_start_button())
            for button in buttons:
                button.changeColor(mouse_pos)
                button.update(self.screen)

            if self.game_start:
                card_buttons = self.build_cards()
                if card_buttons is not None:
                    for card in card_buttons.keys():
                        card.changeColor(mouse_pos)
                        card.update(self.screen)

                card_pile = self.build_add_card()
                if card_pile is not None:
                    for card in card_pile:
                        card.changeColor(mouse_pos)
                        card.update(self.screen)

                if self.change:
                    color_buttons = self.build_color_buttons()
                    for color_button in color_buttons:
                        color_button.changeColor(mouse_pos)
                        color_button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_del(self.username)
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_start:
                        if self.host:
                            if buttons[0].checkForInputs(mouse_pos):
                                self.handle_start()
                    if buttons[-1].checkForInputs(mouse_pos):
                        self.handle_del(self.username)
                        return
                    if self.game_start and self.is_turn and not self.change:
                        for button, card in card_buttons.items():
                            if button.checkForInputs(mouse_pos):
                                self.handle_play(card)

                        if card_pile[0].checkForInputs(mouse_pos):
                            self.handle_add()

                    if self.game_start and self.is_turn and self.change:
                        if color_buttons[0].checkForInputs(mouse_pos):
                            self.handle_change("red")
                            self.change = False
                        elif color_buttons[1].checkForInputs(mouse_pos):
                            self.handle_change("blue")
                            self.change = False
                        elif color_buttons[2].checkForInputs(mouse_pos):
                            self.handle_change("green")
                            self.change = False
                        elif color_buttons[3].checkForInputs(mouse_pos):
                            self.handle_change("yellow")
                            self.change = False




            pygame.display.flip()