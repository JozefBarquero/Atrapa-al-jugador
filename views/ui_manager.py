import pygame
from config import (COLOR_PANEL, COLOR_PANEL_DARK, COLOR_TEXT, COLOR_TEXT_LIGHT,
                    COLOR_GOLD, COLOR_DANGER, COLOR_SUCCESS,
                    TOP_HUD_HEIGHT, BOTTOM_PANEL_HEIGHT, MODE_MULTI, COLOR_PLAYER, COLOR_PLAYER_2)
from views.widgets import Button

class UIManager:
    def __init__(self):
        self.font_hud = pygame.font.SysFont("trebuchetms", 22, bold=True)
        self.font_hud_label = pygame.font.SysFont("trebuchetms", 14)
        self.font_btn = pygame.font.SysFont("georgia", 18, bold=True)
        self.btn_restart = None
        self.btn_menu = None

    def setup_buttons(self, w, h):
        if self.btn_restart is None or self.btn_restart.rect.y != h - BOTTOM_PANEL_HEIGHT + 25:
            y_panel = h - BOTTOM_PANEL_HEIGHT
            self.btn_restart = Button(20, y_panel + 25, 160, 42, "Reiniciar", self.font_btn)
            self.btn_menu = Button(200, y_panel + 25, 180, 42, "Menú Principal", self.font_btn)

    def handle_events(self, event, pos, w, h):
        self.setup_buttons(w, h)
        self.btn_restart.check_hover(pos)
        self.btn_menu.check_hover(pos)

        if self.btn_restart.handle_event(event, pos):
            return "RESTART"
        if self.btn_menu.handle_event(event, pos):
            return "MENU"
        return None

    def _draw_stat(self, surface, x, y, label, value, color=COLOR_TEXT):
        label_surf = self.font_hud_label.render(label, True, COLOR_TEXT_LIGHT)
        value_surf = self.font_hud.render(str(value), True, color)
        surface.blit(label_surf, (x, y))
        surface.blit(value_surf, (x, y + 18))

    def format_time(self, seconds):
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"

    def draw_hud(self, surface, state):
        w = surface.get_width()
        hud_rect = pygame.Rect(0, 0, w, TOP_HUD_HEIGHT)
        pygame.draw.rect(surface, COLOR_PANEL, hud_rect)
        pygame.draw.line(surface, COLOR_PANEL_DARK, (0, TOP_HUD_HEIGHT), (w, TOP_HUD_HEIGHT), 2)

        if state.mode == MODE_MULTI:
            self._draw_stat(surface, 30, 15, "TIEMPO", self.format_time(state.elapsed_time))
            self._draw_stat(surface, 200, 15, "META", state.goal_node, COLOR_SUCCESS)
            
            p1_color = COLOR_PLAYER if state.turn == "PLAYER1" else COLOR_TEXT_LIGHT
            p2_color = COLOR_PLAYER_2 if state.turn == "PLAYER2" else COLOR_TEXT_LIGHT
            
            self._draw_stat(surface, 380, 15, "JUGADOR 1 (WASD)", state.p1_name, p1_color)
            self._draw_stat(surface, 620, 15, "JUGADOR 2 (FLECHAS)", state.p2_name, p2_color)
            
            turn_color = COLOR_GOLD if state.winner is None else COLOR_DANGER
            self._draw_stat(surface, w - 300, 15, "ESTADO", state.message, turn_color)
        else:
            self._draw_stat(surface, 30, 15, "TIEMPO", self.format_time(state.elapsed_time))
            self._draw_stat(surface, 200, 15, "MOVIMIENTOS", str(state.moves))
            self._draw_stat(surface, 400, 15, "PUNTOS", str(state.get_current_score()), COLOR_GOLD)
            self._draw_stat(surface, 600, 15, "META", state.goal_node, COLOR_SUCCESS)
            self._draw_stat(surface, w - 300, 15, "ESTADO", state.message, COLOR_DANGER if state.winner else COLOR_TEXT)

    def draw_bottom_panel(self, surface):
        w = surface.get_width()
        h = surface.get_height()
        self.setup_buttons(w, h)
        
        y = h - BOTTOM_PANEL_HEIGHT
        panel_rect = pygame.Rect(0, y, w, BOTTOM_PANEL_HEIGHT)
        pygame.draw.rect(surface, COLOR_PANEL, panel_rect)
        pygame.draw.line(surface, COLOR_PANEL_DARK, (0, y), (w, y), 2)
        self.btn_restart.draw(surface)
        self.btn_menu.draw(surface)