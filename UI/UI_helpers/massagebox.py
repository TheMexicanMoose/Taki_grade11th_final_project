
import pygame
from globals import *
from UI.UI_helpers.Button import Button

#gets the custom font
def get_font(size):
    return pygame.font.Font(r'..\Assets/Fonts/ThaleahFat_TTF.ttf', size)

# a custom MassageBox class
class MassageBox:
    def __init__(self,screen,title,message,image=None):
        self.screen = screen
        self.title = title
        self.message = message
        if image is None:
            self.image = pygame.image.load(r'..\Assets\Pictures\popup.png')
        else:
            self.image = image
        self.messagebox = self.image
        self.messagebox_rect = self.messagebox.get_rect()
        self.messagebox_rect.center = ((SIZE_WIDTH * scale) // 2, (SIZE_HEIGHT * scale) // 2)
        self.overlay = pygame.Surface((SIZE_WIDTH * scale, SIZE_HEIGHT * scale), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))

        self.exit_button_image = pygame.image.load(r'../Assets/Pictures/Buttons/Button_back_red.png')
        self.exit_button_image = pygame.transform.flip(self.exit_button_image, True, False)

        self.background_snapshot = self.screen.copy()
        self.run()

    #build the exit button
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

        return [exit_button]

    #runs the massageBox
    def run(self):
        pygame.display.set_caption(self.title)
        while True:
            #update the mouse position every frame
            mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(self.background_snapshot,(0,0))
            self.screen.blit(self.overlay, (0,0))
            self.screen.blit(self.messagebox,self.messagebox_rect)

            title_text = get_font(60).render(self.title.upper(), True, "#d7fcd4")
            title_rect = title_text.get_rect(center=(324 * scale, 137 * scale))
            self.screen.blit(title_text, title_rect)

            message_text = get_font(40).render(self.message.upper(), True, "red")
            message_rect = message_text.get_rect(center=(324 * scale, 180 * scale))
            self.screen.blit(message_text, message_rect)

            #chack for inputs in the buttons
            for button in self.build_buttons():
                button.changeColor(mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                #chack if it should quit
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #chack if pressed button
                    if self.build_buttons()[0].checkForInputs(mouse_pos):
                        return

            pygame.display.flip()
