import pygame
from PIL import Image


def load_gif(path):
    gif = Image.open(path)
    Scenes = []
    duration = []

    try:
        while True:
            frame = gif.copy().convert("RGBA")
            pygame_frame = pygame.image.frombytes(frame.tobytes(), frame.size, "RGBA")
            Scenes.append(pygame_frame)
            duration.append(gif.info.get("duration", 100))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    return Scenes, duration