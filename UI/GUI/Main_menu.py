import pygame
from UI.UI_helpers.Button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1200, 720))
BG = pygame.image.load(r'..\..\Assets\Pictures\menu_bg.jpg')
BG = pygame.transform.scale(BG, (1200, 720))

def get_font(size):
    font = pygame.font.Font('..\..\Assets/Fonts/ThaleahFat_TTF.ttf', size)
    return font

def main_menu():
    pygame.display.set_caption('Main Menu')
    pygame.mixer.init()
    pygame.mixer.music.load(r'..\..\Assets/Music/main_menu_music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)

    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOOSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render('MENU', True, "yellow")
        MENU_RECT = MENU_TEXT.get_rect(center=(640,100))

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        pygame.display.update()
main_menu()