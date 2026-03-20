import pygame
import random
from UI.UI_helpers.gif_load import load_gif
from UI.UI_helpers.Button import Button

pygame.init()

SIZE_WIDTH, SIZE_HEIGHT = 640, 360
scale = 2

SCREEN = pygame.display.set_mode((SIZE_WIDTH * scale, SIZE_HEIGHT * scale))
clock = pygame.time.Clock()
frames, durations = load_gif(r'..\..\Assets\Pictures\water.gif')

scaled_up = (SIZE_WIDTH * scale, SIZE_HEIGHT * scale)
frames = [pygame.transform.scale(f, scaled_up) for f in frames]



def get_font(size):
    font = pygame.font.Font('..\..\Assets/Fonts/ThaleahFat_TTF.ttf', size)
    return font

def main_menu():
    pygame.display.set_caption('Main Menu')
    pygame.mixer.init()
    pygame.mixer.music.load(r'..\..\Assets/Music/main_menu_music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)

    bird_sound = pygame.mixer.Sound(r'..\..\Assets/Music/bird sound.mp3')
    bird_timer = random.randint(10000, 20000)

    current_frame = 0
    elapsed = 0
    bird_elapsed = 0

    while True:
        dt = clock.tick(60)
        elapsed += dt
        bird_elapsed += dt

        if bird_elapsed >= bird_timer:
            bird_sound.play()
            bird_elapsed = 0
            bird_timer = random.randint(10000, 20000)

        if elapsed >= durations[current_frame]:
            elapsed = 0
            current_frame = (current_frame + 1) % len(frames)

        SCREEN.fill((0, 0, 0))
        SCREEN.blit(frames[current_frame], (0, 0))

        MENU_MOOSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render('MAIN MENU', True, "yellow")
        MENU_RECT = MENU_TEXT.get_rect(center=(320 * scale,50 * scale))

        play_button_image = pygame.image.load(r'..\..\Assets\Pictures\button_plain_green.png')
        options_button_image = pygame.image.load(r'..\..\Assets\Pictures\button_plain_magenta.png')
        quit_button_image = pygame.image.load(r'..\..\Assets\Pictures\button_plain_orangeyellow.png')

        PLAY_BUTTON = Button(image=play_button_image,
                             pos=(320 * scale,125 * scale),
                             text_input="PLAY",
                             font=get_font(75),
                             base_color="#d7fcd4",
                             hovering_color="white",
                        )

        OPTIONS_BUTTON = Button(image=options_button_image,
                                pos=(320 * scale,190 * scale),
                                text_input="OPTIONS",
                                font=get_font(75),
                                base_color="#d7fcd4",
                                hovering_color="white",
                        )

        QUIT_BUTTON = Button(image=quit_button_image,
                             pos=(320 * scale,255 * scale),
                             text_input="QUIT",
                             font=get_font(75),
                             base_color="#d7fcd4",
                             hovering_color="white",
                    )




        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON,QUIT_BUTTON]:
            button.changeColor(MENU_MOOSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        pygame.display.flip()
main_menu()