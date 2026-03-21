import pygame

class TextInput:
    def __init__(self, pos, color, font, width, image=None, padding=10,hide=False):
        self.hide = hide
        self.is_active = False
        self.width = width
        self.padding = padding
        self._last_tick = 0
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.color = color
        self.font = font
        self.user_input = ''
        self.user_text = self.font.render(self.user_input, True, self.color)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos)) if self.image else None
        self.scroll_offset = 0
        self._update_text_rect()
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 500

    def _update_text_rect(self):
        if self.image:
            self.user_text_rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        else:
            text_height = self.user_text.get_height()
            width = self.width
            height = text_height + self.padding * 2
            self.user_text_rect = pygame.Rect(0, 0, width, height)
            self.user_text_rect.midleft = (self.x_pos, self.y_pos)

    def _clamp_scroll(self):
        available_width = self.user_text_rect.width - self.padding * 2
        text_width = self.user_text.get_width()
        max_scroll = max(0, text_width - available_width)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def scroll_right(self, amount=10):
        self.scroll_offset += amount
        self._clamp_scroll()

    def scroll_left(self, amount=10):
        self.scroll_offset -= amount
        self._clamp_scroll()

    def update(self, screen):
        if self.image:
            screen.blit(self.image, self.user_text_rect)
        else:
            pygame.draw.rect(screen, self.color, self.user_text_rect, 2)
        available_width = self.user_text_rect.width - self.padding * 2
        text_width = self.user_text.get_width()
        if self.hide:
            hidden_surface = self.font.render("*" * len(self.user_input), True, self.color)
            text_width = hidden_surface.get_width()
            if text_width > available_width:
                clip_rect = pygame.Rect(self.scroll_offset, 0, available_width, hidden_surface.get_height())
                visible_text = hidden_surface.subsurface(clip_rect)
            else:
                visible_text = hidden_surface
        else:
            if text_width > available_width:
                clip_rect = pygame.Rect(self.scroll_offset, 0, available_width, self.user_text.get_height())
                visible_text = self.user_text.subsurface(clip_rect)
            else:
                visible_text = self.user_text
        text_surface_rect = visible_text.get_rect(
            midleft=(self.user_text_rect.left + self.padding, self.user_text_rect.centery))
        screen.set_clip(self.user_text_rect)
        screen.blit(visible_text, text_surface_rect)
        screen.set_clip(None)
        if self.is_active:
            self.cursor_timer += pygame.time.get_ticks() - self._last_tick
            self._last_tick = pygame.time.get_ticks()
            if self.cursor_timer >= self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            if self.cursor_visible:
                cursor_x = text_surface_rect.right + 2
                cursor_top = self.user_text_rect.top + self.padding // 2
                cursor_bottom = self.user_text_rect.bottom - self.padding // 2
                pygame.draw.line(screen, self.color, (cursor_x, cursor_top), (cursor_x, cursor_bottom), 2)

    def checkForInputs(self, position):
        if self.user_text_rect.collidepoint(position):
            self.is_active = True
            self.cursor_visible = True
            self.cursor_timer = 0
            return True
        self.is_active = False
        return False

    def addText(self, text):
        self.user_input += text
        self.user_text = self.font.render(self.user_input, True, self.color)
        available_width = self.user_text_rect.width - self.padding * 2
        if self.hide:
            hidden_surface = self.font.render("*" * len(self.user_input), True, self.color)
            self.scroll_offset = max(0, hidden_surface.get_width() - available_width)
        else:
            self.scroll_offset = max(0, self.user_text.get_width() - available_width)

    def removeText(self):
        self.user_input = self.user_input[:-1]
        self.user_text = self.font.render(self.user_input, True, self.color)
        if self.hide:
            hidden_surface = self.font.render("*" * len(self.user_input), True, self.color)
            available_width = self.user_text_rect.width - self.padding * 2
            max_scroll = max(0, hidden_surface.get_width() - available_width)
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        else:
            self._clamp_scroll()

    def get_input(self):
        self.is_active = False
        return self.user_input