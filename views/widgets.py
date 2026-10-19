import pygame
import webbrowser
from config import (COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_ACTIVE, COLOR_BTN_SELECTED,
                    COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_SHADOW, COLOR_PANEL_DARK,
                    COLOR_INPUT_BG, COLOR_INPUT_ACTIVE, COLOR_GOLD)

class Button:
    def __init__(self, x, y, w, h, text, font, base_color=COLOR_BTN):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.is_hovered = False
        self.is_pressed = False
        self.selected = False
        self.focused = False
        self.enabled = True

    def draw(self, surface):
        if not self.enabled:
            color = COLOR_PANEL_DARK
        elif self.selected:
            color = COLOR_BTN_SELECTED
        elif self.is_pressed:
            color = COLOR_BTN_ACTIVE
        elif self.is_hovered:
            color = COLOR_BTN_HOVER
        else:
            color = self.base_color

        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, COLOR_SHADOW, shadow_rect, border_radius=10)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        if self.focused:
            pygame.draw.rect(surface, COLOR_GOLD, self.rect, 3, border_radius=10)
        elif self.is_hovered and self.enabled:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)

        text_color = COLOR_TEXT if self.enabled else (150, 140, 130)
        text_surf = self.font.render(self.text, True, text_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def check_hover(self, pos):
        if self.enabled:
            self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event, pos):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            if was_pressed and self.rect.collidepoint(pos):
                return True
        return False

class TextInput:
    def __init__(self, x, y, w, h, text='', max_len=12):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False
        self.focused = False
        self.max_len = max_len
        self.font = pygame.font.SysFont("trebuchetms", 22)
        self.enabled = True

    def handle_event(self, event, pos):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.active = True
                return True
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < self.max_len:
                if event.unicode.isprintable():
                    self.text += event.unicode
        return False

    def draw(self, surface):
        color = COLOR_INPUT_ACTIVE if self.active else COLOR_INPUT_BG
        if not self.enabled:
            color = COLOR_PANEL_DARK
            
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        border_color = COLOR_TEXT if self.active else COLOR_BTN
        pygame.draw.rect(surface, border_color, self.rect, 2 if self.active else 1, border_radius=8)
        if self.focused:
            pygame.draw.rect(surface, COLOR_GOLD, self.rect, 3, border_radius=8)
        
        txt = self.font.render(self.text, True, COLOR_TEXT if self.enabled else (150, 140, 130))
        surface.blit(txt, (self.rect.x + 15, self.rect.y + self.rect.height//2 - txt.get_height()//2))

class LinkLabel:
    def __init__(self, text, url, font):
        self.text = text
        self.url = url
        self.font = font
        self.color = (100, 180, 250)
        self.hover_color = (150, 220, 255)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.is_hovered = False

    def set_pos(self, x, y):
        surf = self.font.render(self.text, True, self.color)
        self.rect = surf.get_rect(center=(x, y))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                webbrowser.open(self.url)
                return True
        return False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        surf = self.font.render(self.text, True, color)
        surface.blit(surf, self.rect)
        if self.is_hovered:
            pygame.draw.line(surface, color, (self.rect.left, self.rect.bottom), (self.rect.right, self.rect.bottom), 1)

class Spinner:
    def __init__(self, x, y, w, h, label, min_val, max_val, value, font, label_font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.font = font
        self.label_font = label_font if label_font else font
        self.btn_w = h
        self.btn_minus = pygame.Rect(x, y, self.btn_w, h)
        self.btn_plus = pygame.Rect(x + w - self.btn_w, y, self.btn_w, h)
        self.value_rect = pygame.Rect(x + self.btn_w, y, w - self.btn_w * 2, h)
        self.enabled = True
        self.hover_minus = False
        self.hover_plus = False

    def set_bounds(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val
        self.value = max(min_val, min(max_val, self.value))

    def handle_event(self, event, pos):
        if not self.enabled:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_minus.collidepoint(pos) and self.value > self.min_val:
                self.value -= 1
                return "CHANGED"
            if self.btn_plus.collidepoint(pos) and self.value < self.max_val:
                self.value += 1
                return "CHANGED"
        return None

    def check_hover(self, pos):
        self.hover_minus = self.btn_minus.collidepoint(pos) and self.value > self.min_val
        self.hover_plus = self.btn_plus.collidepoint(pos) and self.value < self.max_val

    def draw(self, surface):
        lbl = self.label_font.render(self.label, True, COLOR_TEXT_LIGHT)
        surface.blit(lbl, (self.rect.x, self.rect.y - 22))

        m_color = COLOR_BTN_HOVER if self.hover_minus else (COLOR_BTN if self.value > self.min_val else COLOR_PANEL_DARK)
        p_color = COLOR_BTN_HOVER if self.hover_plus else (COLOR_BTN if self.value < self.max_val else COLOR_PANEL_DARK)
        pygame.draw.rect(surface, m_color, self.btn_minus, border_radius=6)
        pygame.draw.rect(surface, p_color, self.btn_plus, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_DARK, self.value_rect)
        pygame.draw.rect(surface, COLOR_BTN, self.rect, 1, border_radius=6)

        minus_txt = self.font.render("-", True, COLOR_TEXT)
        surface.blit(minus_txt, minus_txt.get_rect(center=self.btn_minus.center))
        plus_txt = self.font.render("+", True, COLOR_TEXT)
        surface.blit(plus_txt, plus_txt.get_rect(center=self.btn_plus.center))
        val_txt = self.font.render(str(self.value), True, COLOR_TEXT)
        surface.blit(val_txt, val_txt.get_rect(center=self.value_rect.center))