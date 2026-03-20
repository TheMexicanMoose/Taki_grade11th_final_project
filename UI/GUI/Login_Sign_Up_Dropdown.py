import pygame
from UI.UI_helpers.Button import Button
from globals import *

def get_font(size):
    return pygame.font.Font(r'..\..\Assets/Fonts/ThaleahFat_TTF.ttf', size)

class DropDown:
    def __init__(self,screen):
        self.screen = screen

        self.dropdown = pygame.image.load('..\..\Assets\Pictures\dropdown.PNG')
        self.dropdown_rect = self.dropdown.get_rect()
        self.dropdown_rect.center = ((SIZE_WIDTH * scale) // 2, (SIZE_HEIGHT * scale) // 2)
        self.overlay = pygame.Surface((SIZE_WIDTH * scale, SIZE_HEIGHT * scale), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        self.title = "login/sign-up"

        self.background_snapshot = self.screen.copy()
    def build_button(self):
        pass
    def run(self):
        pygame.display.set_caption(self.title)
        while True:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(self.background_snapshot, (0, 0))
            self.screen.blit(self.overlay, (0, 0))
            self.screen.blit(self.dropdown, self.dropdown_rect)

            pygame.display.flip()




