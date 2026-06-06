import pygame
import globals
from globals import scale

cards = {
    ("RED", 1): (0, 0),
    ("RED", 2): (0, 1),
    ("RED", 3): (0, 2),
    ("RED", 4): (0, 3),
    ("RED", 5): (0, 4),
    ("RED", 6): (0, 5),
    ("RED", 7): (0, 6),
    ("RED", 8): (0, 7),
    ("RED", 9): (0, 8),

    ("YELLOW", 1): (1, 0),
    ("YELLOW", 2): (1, 1),
    ("YELLOW", 3): (1, 2),
    ("YELLOW", 4): (1, 3),
    ("YELLOW", 5): (1, 4),
    ("YELLOW", 6): (1, 5),
    ("YELLOW", 7): (1, 6),
    ("YELLOW", 8): (1, 7),
    ("YELLOW", 9): (1, 8),

    ("GREEN", 1): (2, 0),
    ("GREEN", 2): (2, 1),
    ("GREEN", 3): (2, 2),
    ("GREEN", 4): (2, 3),
    ("GREEN", 5): (2, 4),
    ("GREEN", 6): (2, 5),
    ("GREEN", 7): (2, 6),
    ("GREEN", 8): (2, 7),
    ("GREEN", 9): (2, 8),

    ("BLUE", 1): (3, 0),
    ("BLUE", 2): (3, 1),
    ("BLUE", 3): (3, 2),
    ("BLUE", 4): (3, 3),
    ("BLUE", 5): (3, 4),
    ("BLUE", 6): (3, 5),
    ("BLUE", 7): (3, 6),
    ("BLUE", 8): (3, 7),
    ("BLUE", 9): (3, 8),

    ("RED", "SKIP"): (4, 0),
    ("YELLOW", "SKIP"): (4, 1),
    ("GREEN", "SKIP"): (4, 2),
    ("BLUE", "SKIP"): (4, 3),

    ("RED", "DRAW_TWO"): (4, 4),
    ("YELLOW", "DRAW_TWO"): (4, 5),
    ("GREEN", "DRAW_TWO"): (4, 6),
    ("BLUE", "DRAW_TWO"): (4, 7),

    ("RED", "REVERSE"): (4, 8),
    ("YELLOW", "REVERSE"): (5, 0),
    ("GREEN", "REVERSE"): (5, 1),
    ("BLUE", "REVERSE"): (5, 2),

    ("WILD", "DRAW_FOUR"): (5, 3),
    ("WILD","CHANGE"): (5, 4)
}

plain_cards = {
    ("RED", -1): (0,0),
    ("GREEN", -1): (0,1),
    ("YELLOW", -1): (0,2),
    ("BLUE", -1): (0,3),
}

def get_card(card):
    pic = pygame.image.load(r'../Assets/Pictures/uno_cards.jpg')
    row,col = 0,0
    if card in cards.keys():
        row,col = cards[card]
    else:
        if card in plain_cards.keys():
            pic = pygame.image.load(r'../Assets/Pictures/plain_cards.jpg')
            row,col = plain_cards[card]

    x_pos = col * 33
    y_pos = row * 50

    rect = pygame.Rect(x_pos,y_pos,33,50)
    card = pygame.Surface((33 ,50),pygame.SRCALPHA)
    card.blit(pic,(0,0),rect)
    return card
