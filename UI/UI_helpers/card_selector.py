import pygame

cards = {
    "red_1": (0, 0), "red_2": (0, 1), "red_3": (0, 2),
    "red_4": (0, 3), "red_5": (0, 4), "red_6": (0, 5),
    "red_7": (0, 6), "red_8": (0, 7), "red_9": (0, 8),
    "yellow_1": (1, 0), "yellow_2": (1, 1), "yellow_3": (1, 2),
    "yellow_4": (1, 3), "yellow_5": (1, 4), "yellow_6": (1, 5),
    "yellow_7": (1, 6), "yellow_8": (1, 7), "yellow_9": (1, 8),
    "green_1": (2, 0), "green_2": (2, 1), "green_3": (2, 2),
    "green_4": (2, 3), "green_5": (2, 4), "green_6": (2, 5),
    "green_7": (2, 6), "green_8": (2, 7), "green_9": (2, 8),
    "blue_1": (3, 0), "blue_2": (3, 1), "blue_3": (3, 2),
    "blue_4": (3, 3), "blue_5": (3, 4), "blue_6": (3, 5),
    "blue_7": (3, 6), "blue_8": (3, 7), "blue_9": (3, 8),
    "red_skip": (4, 0), "yellow_skip": (4, 1),
    "green_skip": (4, 2), "blue_skip": (4, 3),
    "red_draw2": (4, 4), "yellow_draw2": (4, 5),
    "green_draw2": (4, 6), "blue_draw2": (4, 7),
    "red_reverse": (4, 8),
    "yellow_reverse": (5, 0), "green_reverse": (5, 1),
    "wild_draw4": (5, 2),
    "wild": (5, 4)

}

def get_card(card_name):
    pic = pygame.image.load(r'../Assets/Pictures/uno_cards.jpg')
    row,col = 0,0
    if card_name in cards.keys():
        row,col = cards[card_name]
    else:
        return None

    x_pos = col * 76
    y_pos = row * 115

    rect = pygame.Rect(x_pos,y_pos,76,115)
    card = pygame.Surface((76,115),pygame.SRCALPHA)
    card.blit(pic,(0,0),rect)
    return card
