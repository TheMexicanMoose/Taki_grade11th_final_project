__author__ = "Noam"

import pygame

from Helpers.tcp_by_size import send_with_size
from UI.GUI.Game.Playing_room import PlayingRoom
from UI.UI_helpers.Button import Button
from globals import *
from UI.UI_helpers.massagebox import MassageBox
from Encryption.AES import *

def get_font(size):
    return pygame.font.Font(r'..\Assets/Fonts/ThaleahFat_TTF.ttf', size)

class RoomsList:
    def __init__(self, screen, sock, key, ui_queue,username):
        self.ui_queue = ui_queue
        self.screen = screen
        self.sock = sock
        self.key = key
        self.username = username

        self.dropdown = pygame.image.load('..\Assets\Pictures\dropdown.PNG')
        self.dropdown = pygame.transform.scale(self.dropdown, (1000, 782))
        self.dropdown_rect = self.dropdown.get_rect()

        self.final_center = (320 * scale, 160 * scale)
        self.dropdown_rect.center = (320 * scale, 160 * scale)
        self.overlay = pygame.Surface((SIZE_WIDTH * scale, SIZE_HEIGHT * scale), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        self.title = "login/sign-up"

        self.create_room_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_orangeyellow.png')
        self.refresh_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_magenta.png')
        self.exit_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/Button_back_red.png')
        self.exit_button_image = pygame.transform.flip(self.exit_button_image, True, False)
        self.join_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_orangeyellow.png')

        self.animation_speed = 12
        self.animating = True
        self.dropdown_rect.centery = -self.dropdown_rect.height // 2

        self.to_return = None
        self.rooms = {}
        self.room_button_height = 50 * scale
        self.room_button_gap = 10 * scale

        self.background_snapshot = self.screen.copy()
        self.run()

    def build_button(self):
        base_y = self.dropdown_rect.centery

        create_button = Button(
            pos=(210 * scale, base_y - 50 * scale),
            text_input="CREATE",
            font=get_font(50),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.create_room_image
        )

        refresh_button = Button(
            pos=(400 * scale, base_y - 50 * scale),
            text_input="REFRESH",
            font=get_font(50),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.refresh_button_image
        )

        exit_button = Button(
            pos=(590 * scale, 35 * scale),
            text_input="",
            font=get_font(30),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.exit_button_image,
            text_pos=(45 * scale, 41 * scale)
        )

        return [create_button, refresh_button, exit_button]

    def build_room_buttons(self):
        buttons = []
        area_top = self.dropdown_rect.centery + 20 * scale
        area_left = 210 * scale

        for i, (room_name, current_count) in enumerate(self.rooms.items()):
            btn_y = area_top + i * (self.room_button_height + self.room_button_gap)
            label = f"{room_name}   {current_count}/{4}"

            btn = Button(
                pos=(area_left, btn_y),
                text_input=label,
                font=get_font(30),
                base_color="#d7fcd4",
                hovering_color="white",
                image=self.join_button_image
            )
            buttons.append((btn, room_name))

        return buttons

    def handle_join(self, room_name,username):
        to_send = f"JOIN|{room_name}|{username}"
        print("sending:", to_send)
        to_send = to_send.encode('utf-8')
        to_send = pad_massage(to_send)
        encrypted_to_send = encrypt(to_send, self.key)
        send_with_size(self.sock, encrypted_to_send)


    def handle_room_creation(self,username):
        try:
            to_send = f"CRR|{username}|"
            print("sending:", to_send)
            to_send = to_send.encode('utf-8')
            to_send = pad_massage(to_send)
            encrypted_to_send = encrypt(to_send, self.key)
            send_with_size(self.sock, encrypted_to_send)

        except Exception:
            MassageBox(self.screen, "ERROR", "an unexpected \n error occurred!")

    def handle_refresh(self):
        try:
            to_send = f"ROOMS|"
            print("sending:", to_send)
            to_send = to_send.encode('utf-8')
            to_send = pad_massage(to_send)
            encrypted_to_send = encrypt(to_send, self.key)
            send_with_size(self.sock, encrypted_to_send)

        except Exception:
            MassageBox(self.screen, "ERROR", "an unexpected \n error occurred!")

    def run(self):
        pygame.display.set_caption(self.title)
        self.handle_refresh()

        while True:
            mouse_pos = pygame.mouse.get_pos()

            if self.animating:
                target_y = self.final_center[1]
                if self.dropdown_rect.centery < target_y:
                    self.dropdown_rect.centery += self.animation_speed
                    if self.dropdown_rect.centery >= target_y:
                        self.dropdown_rect.centery = target_y
                        self.animating = False

            while self.ui_queue:
                print("hi")
                event = self.ui_queue[0]
                if event.get_where() == "room":
                    if event.get_action() == "messagebox":
                        MassageBox(self.screen, event.get_title(), event.get_message())
                        self.ui_queue.remove(event)
                    elif event.get_action() == "new_room":
                        self.rooms = event.get_data()
                        self.ui_queue.remove(event)
                    elif event.get_action() == "join_room":
                        self.ui_queue.remove(event)
                        PlayingRoom(self.screen, self.sock, self.key, self.ui_queue, event.get_data(), self.username)
                    else:
                        self.ui_queue.remove(event)

                else:
                    break

            self.screen.blit(self.background_snapshot, (0, 0))
            self.screen.blit(self.overlay, (0, 0))
            self.screen.blit(self.dropdown, self.dropdown_rect)

            rooms_text = get_font(50).render('ROOMS', True, "red")
            rooms_rect = rooms_text.get_rect(
                center=(self.dropdown_rect.centerx - 10, self.dropdown_rect.centery - 100 * scale)
            )
            self.screen.blit(rooms_text, rooms_rect)

            top_buttons = self.build_button()
            for button in top_buttons:
                button.changeColor(mouse_pos)
                button.update(self.screen)

            room_buttons = self.build_room_buttons()
            for btn, _ in room_buttons:
                btn.changeColor(mouse_pos)
                btn.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.animating:
                        if top_buttons[1].checkForInputs(mouse_pos):
                            self.handle_refresh()
                        elif top_buttons[0].checkForInputs(mouse_pos):
                            self.handle_room_creation(self.username)
                        elif top_buttons[-1].checkForInputs(mouse_pos):
                            self.to_return = None
                            return

                        for btn, room_name in room_buttons:
                            if btn.checkForInputs(mouse_pos):
                                self.handle_join(room_name,self.username)

            pygame.display.flip()