__author__ = "Noam"

import pygame
from UI.UI_helpers.Button import Button
from UI.UI_helpers.Text_Input import TextInput
from UI.UI_helpers.massagebox import MassageBox
from globals import *


def get_font(size):
    return pygame.font.Font(r'..\Assets/Fonts/ThaleahFat_TTF.ttf', size)

def get_arial_font(size):
    return pygame.font.SysFont("Arial", size)

class Options:
    def __init__(self, screen,sock,key,ui_queue):
        self.ui_queue = ui_queue
        self.screen = screen
        self.sock = sock
        self.key = key

        self.box = pygame.image.load(r'..\Assets\Pictures\box.PNG')
        self.box_rect = self.box.get_rect()
        self.box_rect.center = (320 * scale, 190 * scale)

        self.overlay = pygame.Surface((SIZE_WIDTH * scale, SIZE_HEIGHT * scale), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        self.title = "options"

        self.input_box = pygame.image.load(r'..\Assets\Pictures\input_box.PNG')



        self.options = "5"

        self.options_active = False

        self.exit_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/Button_back_red.png')
        self.exit_button_image = pygame.transform.flip(self.exit_button_image, True, False)

        self.text_inputs = self.build_text_area()

        self.to_return = None

        self.background_snapshot = self.screen.copy()
        self.run()

    def build_text_area(self):
        OPTION = TextInput(pos=(320 * scale, 100 * scale),
                             color="white",
                             font=get_arial_font(30),
                             width=200,
                             image=self.input_box,
                             padding=20)



        return [OPTION]

    #build the button
    def build_buttons(self):

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
        global volume
        pygame.display.set_caption(self.title)
        while True:
            mouse_pos = pygame.mouse.get_pos()

            pygame.mixer.music.set_volume(volume)

            self.screen.blit(self.background_snapshot, (0, 0))
            self.screen.blit(self.overlay, (0, 0))
            self.screen.blit(self.box, self.box_rect)

            while not len(self.ui_queue) == 0:
                event = self.ui_queue[0]
                if event.get_where() == "options":
                    if event.get_action() == "messagebox":
                        MassageBox(self.screen, event.get_title(), event.get_message())
                        self.ui_queue.remove(event)
                    elif event.get_action() == "":
                        self.ui_queue.remove(event)


            username_text = get_font(20).render('VOLUME:', True, "red")
            username_rect = username_text.get_rect(center=(255 * scale, 100 * scale))
            self.screen.blit(username_text, username_rect)

            credits_lines = [
                "GAME CREATOR:",
                "  noam gilboa",
                "",
                "MUSIC:",
                "  randow wii music",
                "",
                "ASSETS:",
                "  unity assets store",
                "  random assets from the internet"
                "",
                "",
                "CODE:",
                "  noam gilboa",
                "",
                "EVERYTHING:",
                "  noam gilboa",
                "",
                "THANKS FOR PLAYING!!"
            ]

            start_y = 130 * scale
            line_height = 10 * scale

            for i, line in enumerate(credits_lines):
                text = get_font(20).render(line, True, "red")
                rect = text.get_rect(center=(320 * scale, start_y + i * line_height))
                self.screen.blit(text, rect)



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
                        self.options_active = True

                        self.text_inputs[0].set_active(True)
                    elif self.build_buttons()[0].checkForInputs(mouse_pos):
                        return
                    else:
                        self.options_active = False

                        self.text_inputs[0].set_active(False)

                        self.options = self.text_inputs[0].get_input()
                        volume = int(self.options) / 10
                        if volume < 0:
                            volume = 0
                        elif volume > 1:
                            volume = 1

                if event.type == pygame.KEYDOWN:
                    if self.options_active:

                        if event.key == pygame.K_BACKSPACE:
                            self.text_inputs[0].removeText()
                        elif event.key == pygame.K_RETURN:
                            self.options_active = False
                            self.options = self.text_inputs[0].get_input()
                            volume = int(self.options) / 10
                            if volume < 0:
                                volume = 0
                            elif volume > 1:
                                volume = 1
                        elif event.key == pygame.K_LEFT:
                            self.text_inputs[0].scroll_left()
                        elif event.key == pygame.K_RIGHT:
                            self.text_inputs[0].scroll_right()
                        else:
                            self.text_inputs[0].addText(event.unicode)



            pygame.display.flip()