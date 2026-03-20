import pygame
from UI.UI_helpers.Button import Button
from globals import *

def get_font(size):
    return pygame.font.Font(r'..\..\Assets/Fonts/ThaleahFat_TTF.ttf', size)

class DropDown:
    def __init__(self,screen):
        self.screen = screen

        self.dropdown = pygame.image.load('..\..\Assets\Pictures\dropdown.PNG')
        self.dropdown = pygame.transform.scale(self.dropdown,(638,782))
        self.dropdown_rect = self.dropdown.get_rect()

        self.final_center = (129 * scale, 160 * scale)
        self.dropdown_rect.center = (129 * scale, 160 * scale)
        #self.dropdown_rect.center = (129 * scale,160*scale)
        self.overlay = pygame.Surface((SIZE_WIDTH * scale, SIZE_HEIGHT * scale), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        self.title = "login/sign-up"

        self.login_button_image = pygame.image.load(r'..\..\Assets\Pictures\button_plain_orangeyellow.png')
        self.sighup_button_image = pygame.image.load(r'..\..\Assets\Pictures\button_plain_magenta.png')

        self.exit_button_image = pygame.image.load(r'../../Assets/Pictures/Button_back_red.png')
        self.exit_button_image = pygame.transform.flip(self.exit_button_image, True, False)

        self.animation_speed = 12
        self.animating = True
        self.dropdown_rect.centery = -self.dropdown_rect.height // 2

        self.background_snapshot = self.screen.copy()
        self.run()
    def build_button(self):
        base_y = self.dropdown_rect.centery

        login_button = Button(
            pos=(120 * scale,base_y + 0 * scale),
            text_input="LOGIN",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.login_button_image
        )

        sighup_button = Button(
            pos=(120 * scale, base_y + 70 * scale),
            text_input="SIGH UP",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="white",
            image=self.sighup_button_image
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

        return [login_button,sighup_button,exit_button]
    def run(self):
        pygame.display.set_caption(self.title)
        while True:
            mouse_pos = pygame.mouse.get_pos()

            if self.animating:
                target_y = self.final_center[1]
                if self.dropdown_rect.centery < target_y:
                    self.dropdown_rect.centery += self.animation_speed
                    if self.dropdown_rect.centery >= target_y:
                        self.dropdown_rect.centery = target_y
                        self.animating = False

            self.screen.blit(self.background_snapshot, (0, 0))
            self.screen.blit(self.overlay, (0, 0))
            self.screen.blit(self.dropdown, self.dropdown_rect)

            for button in self.build_button():
                button.changeColor(mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.animating and self.build_button()[2].checkForInputs(mouse_pos):
                        return

            pygame.display.flip()




