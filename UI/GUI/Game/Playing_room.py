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

        self.is_turn = False


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

        self.player_slots = [(280,320),(25,150),(300,20),(450,200)]

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

    def draw_players(self):
        for username, player_id in self.players.items():
            pos_x ,pos_y = self.player_slots[player_id]

            img = self.player_img[player_id]
            self.screen.blit(img, (pos_x * scale, pos_y * scale))

            name = get_font(30).render(username, True, (255, 255, 255))
            self.screen.blit(name, (pos_x * scale + 70, pos_y * scale + 15))


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
                    if self.game_start:
                        for button,card in card_buttons.items():
                            if self.is_turn:
                                if button.checkForInputs(mouse_pos):
                                    self.handle_play(card)



            pygame.display.flip()