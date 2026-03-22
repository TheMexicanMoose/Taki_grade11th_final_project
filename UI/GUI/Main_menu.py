import pygame
import random
import os
from UI.UI_helpers.gif_load import load_gif
from UI.UI_helpers.Button import Button
from UI.UI_helpers.massagebox import MassageBox
from UI.GUI.Login_Sign_Up_Dropdown import DropDown
from globals import *

pygame.init()

def get_font(size):
    return pygame.font.Font(r'..\Assets/Fonts/ThaleahFat_TTF.ttf', size)


class MainMenu:
    def __init__(self,screen,sock,key,ui_queue):
        self.ui_queue = ui_queue
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.frames, self.durations = load_gif(r'..\Assets\Pictures\water.gif')
        scaled_up = (SIZE_WIDTH * scale, SIZE_HEIGHT * scale)
        self.frames = [pygame.transform.scale(f, scaled_up) for f in self.frames]
        self.sock = sock
        self.key = key

        pygame.mixer.init()
        pygame.mixer.music.load(r'..\Assets/Music/main_menu_music.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)

        self.files = [f for f in os.listdir("../Assets/Music/Animals") if f.endswith('.mp3')]
        random_song = random.choice(self.files)
        self.animal_sound = pygame.mixer.Sound(f'../Assets/Music/Animals/{random_song}')
        self.animal_sound.set_volume(0.5)
        self.animal_timer = random.randint(5000, 10000)

        self.play_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_green.png')
        self.options_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_magenta.png')
        self.quit_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_plain_orangeyellow.png')
        self.user_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/button_fx_multiuser_orange.png')

        self.current_frame = 0
        self.elapsed = 0
        self.animal_elapsed = 0

        self.run()


    def build_buttons(self):
        user_button = Button(
            pos=(45 * scale, 45 * scale),
            text_input="LOGIN/SIGH UP",
            font=get_font(30),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.user_button_image,
            text_pos=(45 * scale, 41 * scale)
        )
        play_button = Button(
            pos=(320 * scale, 125 * scale),
            text_input="PLAY",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.play_button_image
        )
        options_button = Button(
            pos=(320 * scale, 190 * scale),
            text_input="OPTIONS",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.options_button_image
        )
        quit_button = Button(
            pos=(320 * scale, 255 * scale),
            text_input="QUIT",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.quit_button_image
        )
        return [play_button, options_button, quit_button, user_button]

    def run(self):
        while True:
            pygame.display.set_caption('Main Menu')

            dt = self.clock.tick(60)
            self.elapsed += dt
            self.animal_elapsed += dt

            while not self.ui_queue.empty():
                event = self.ui_queue.get()
                if event["where"] == "main":
                    if event["action"] == "messagebox":
                        MassageBox(self.screen, event["title"], event["message"])

            if self.animal_elapsed >= self.animal_timer:
                self.animal_sound.play()
                random_song = random.choice(self.files)
                self.animal_sound = pygame.mixer.Sound(f'../Assets/Music/Animals/{random_song}')
                self.animal_elapsed = 0
                self.animal_timer = random.randint(10000, 20000)

            if self.elapsed >= self.durations[self.current_frame]:
                self.elapsed = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.frames[self.current_frame], (0, 0))

            mouse_pos = pygame.mouse.get_pos()

            menu_text = get_font(100).render('MAIN MENU', True, "yellow")
            menu_rect = menu_text.get_rect(center=(320 * scale, 50 * scale))
            self.screen.blit(menu_text, menu_rect)

            for button in self.build_buttons():
                button.changeColor(mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.build_buttons()[0].checkForInputs(mouse_pos):
                        if is_logged_in:
                            pass
                        else:
                            MassageBox(self.screen,"Error","pls sigh in \n to play")
                    elif self.build_buttons()[2].checkForInputs(mouse_pos):
                        pygame.quit()
                    elif self.build_buttons()[3].checkForInputs(mouse_pos):
                        DropDown(screen=self.screen,sock=self.sock,key=self.key,ui_queue=self.ui_queue)



            pygame.display.flip()

