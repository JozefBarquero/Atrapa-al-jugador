import pygame
import math
import cairosvg
import io
import os
import random
import webbrowser
from config import (COLOR_BG, COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_GOLD,
                    COLOR_PANEL, COLOR_PANEL_DARK, COLOR_SUCCESS, COLOR_DANGER,
                    COLOR_OVERLAY, COLOR_EDGE, COLOR_NODE, COLOR_PLAYER,
                    COLOR_PLAYER_2, COLOR_COMPUTER, COLOR_GOAL, COLOR_BTN,
                    DIFFICULTIES, MODE_SINGLE, MODE_MULTI,
                    EDITOR_MIN_ROWS, EDITOR_MAX_ROWS, EDITOR_MIN_COLS,
                    EDITOR_MAX_COLS, EDITOR_MIN_ENEMIES, EDITOR_MAX_ENEMIES,
                    ASSETS_DIR, LINK_WIN, LINK_COIN, LINK_GITHUB)
from views.widgets import Button, TextInput, LinkLabel, Spinner
from models.graph import Graph


class MenuScreen:
    def __init__(self):
        self.time = 0.0
        self.title_font = pygame.font.SysFont("georgia", 82, bold=True)
        self.subtitle_font = pygame.font.SysFont("georgia", 24, italic=True)
        self.label_font = pygame.font.SysFont("trebuchetms", 20, bold=True)
        self.credit_title_font = pygame.font.SysFont("trebuchetms", 16, bold=True)
        self.credit_font = pygame.font.SysFont("trebuchetms", 14)
        self.btn_font = pygame.font.SysFont("georgia", 22, bold=True)
        self.custom_font = pygame.font.SysFont("georgia", 17, bold=True)
        self.link_font = pygame.font.SysFont("trebuchetms", 16)
        
        self.modal_title_font = pygame.font.SysFont("georgia", 42, bold=True)
        self.modal_header_font = pygame.font.SysFont("trebuchetms", 20, bold=True)
        self.modal_text_font = pygame.font.SysFont("trebuchetms", 16)
        
        self.mode = MODE_SINGLE
        self.selected_difficulty = "FACIL"
        
        self.btn_mode_single = None
        self.btn_mode_multi = None
        self.diff_buttons = {}
        self.btn_custom = None
        self.btn_play = None
        
        self.sound_img_on = self.load_icon("sound_on.svg")
        self.sound_img_off = self.load_icon("sound_off.svg")
        self.btn_sound = None
        
        self.btn_manual = None
        self.btn_cc = None
        self.btn_github = None
        
        self.link_win = LinkLabel("Won! (Orchestral winning jingle) by spuispuin (CC BY 4.0)", LINK_WIN, self.link_font)
        self.link_coin = LinkLabel("Picked Coin Echo by NenadSimic (CC BY 3.0)", LINK_COIN, self.link_font)
        
        self.active_modal = None
        self.modal_rect = None
        self.close_rect = None
        
        self.focus_group = []
        self.group_index = 0
        self.item_index = 0

    def load_icon(self, filename):
        path = os.path.join(ASSETS_DIR, "icons", filename)
        if os.path.exists(path):
            png_data = cairosvg.svg2png(url=path, output_width=50, output_height=50)
            return pygame.image.load(io.BytesIO(png_data)).convert_alpha()
        return None

    def setup_layout(self, w, h):
        if self.btn_play is not None and self.btn_play.rect.y == int(h * 0.55):
            return
            
        self.btn_mode_single = Button(w // 2 - 250, int(h * 0.30), 220, 50, "1 Jugador", self.btn_font)
        self.btn_mode_multi = Button(w // 2 + 30, int(h * 0.30), 220, 50, "2 Jugadores", self.btn_font)
        self.btn_mode_single.selected = (self.mode == MODE_SINGLE)
        self.btn_mode_multi.selected = (self.mode == MODE_MULTI)
        
        btn_w = 220
        btn_h = 50
        gap = 15
        total_w = btn_w * 4 + gap * 3
        start_x = w // 2 - total_w // 2
        base_y = int(h * 0.45)
        
        self.diff_buttons = {}
        for i, key in enumerate(["FACIL", "MEDIO", "DIFICIL"]):
            data = DIFFICULTIES[key]
            btn = Button(start_x + i * (btn_w + gap), base_y, btn_w, btn_h, data["name"], self.btn_font)
            self.diff_buttons[key] = btn
        self.btn_custom = Button(start_x + 3 * (btn_w + gap), base_y, btn_w, btn_h, "Grafo Personalizado", self.custom_font)
        self.btn_custom.enabled = (self.mode == MODE_SINGLE)
        
        for key, btn in self.diff_buttons.items():
            btn.selected = (self.selected_difficulty == key)
        self.btn_custom.selected = (self.selected_difficulty == "CUSTOM")
        
        self.btn_play = Button(w // 2 - 130, int(h * 0.55), 260, 65, "JUGAR", self.btn_font)
        self.btn_sound = pygame.Rect(w - 80, 20, 50, 50)
        
        footer_y = h - 80
        btn_y = footer_y + 22
        self.btn_manual = Button(w - 420, btn_y, 110, 36, "Manual", self.credit_title_font)
        self.btn_cc = Button(w - 290, btn_y, 110, 36, "Créditos CC", self.credit_title_font)
        self.btn_github = Button(w - 160, btn_y, 110, 36, "GitHub", self.credit_title_font)
        
        self.focus_group = [
            [self.btn_mode_single, self.btn_mode_multi],
            [self.diff_buttons["FACIL"], self.diff_buttons["MEDIO"], self.diff_buttons["DIFICIL"], self.btn_custom],
            [self.btn_play]
        ]
        self.update_focus()

    def setup_modal(self, w, h):
        self.modal_rect = pygame.Rect(w // 2 - 380, h // 2 - 260, 760, 520)
        self.close_rect = pygame.Rect(self.modal_rect.right - 50, self.modal_rect.top + 20, 30, 30)
        self.link_win.set_pos(self.modal_rect.centerx, self.modal_rect.top + 200)
        self.link_coin.set_pos(self.modal_rect.centerx, self.modal_rect.top + 250)

    def update(self, dt):
        self.time += dt

    def update_focus(self):
        if not self.focus_group: return
        for g in self.focus_group:
            for item in g:
                item.focused = False
        self.focus_group[self.group_index][self.item_index].focused = True

    def _move_item(self, direction):
        items = self.focus_group[self.group_index]
        idx = self.item_index
        for _ in range(len(items)):
            idx = (idx + direction) % len(items)
            if items[idx].enabled:
                self.item_index = idx
                break
        self.update_focus()

    def _switch_to_multi(self):
        self.mode = MODE_MULTI
        self.btn_mode_single.selected = False
        self.btn_mode_multi.selected = True
        if self.btn_custom:
            self.btn_custom.enabled = False
            self.btn_custom.selected = False
        if self.selected_difficulty == "CUSTOM":
            self.selected_difficulty = "FACIL"
            if "FACIL" in self.diff_buttons:
                for bb in self.diff_buttons.values():
                    bb.selected = False
                self.diff_buttons["FACIL"].selected = True

    def _switch_to_single(self):
        self.mode = MODE_SINGLE
        self.btn_mode_single.selected = True
        self.btn_mode_multi.selected = False
        if self.btn_custom:
            self.btn_custom.enabled = True

    def _select_difficulty(self, key):
        self.selected_difficulty = key
        for bb in self.diff_buttons.values():
            bb.selected = False
        if key == "CUSTOM":
            self.btn_custom.selected = True
        elif key in self.diff_buttons:
            self.diff_buttons[key].selected = True

    def handle_events(self, event, pos, sound_manager, w, h):
        self.setup_layout(w, h)
        action = None

        if self.active_modal:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.active_modal = None
                return None
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect.collidepoint(pos):
                    self.active_modal = None
                    return None
                if not self.modal_rect.collidepoint(pos):
                    self.active_modal = None
                    return None
                    
                if self.active_modal == "CREDITS":
                    if self.link_win.handle_event(event, pos) or self.link_coin.handle_event(event, pos):
                        return "LINK"
            
            if self.active_modal == "CREDITS":
                self.link_win.check_hover(pos)
                self.link_coin.check_hover(pos)
                
            return action

        self.btn_play.check_hover(pos)
        self.btn_mode_single.check_hover(pos)
        self.btn_mode_multi.check_hover(pos)
        self.btn_manual.check_hover(pos)
        self.btn_cc.check_hover(pos)
        self.btn_github.check_hover(pos)
        self.btn_custom.check_hover(pos)
        for b in self.diff_buttons.values(): b.check_hover(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_sound.collidepoint(pos):
                sound_manager.toggle_mute()
                return "MUTE"

        if self.btn_manual.handle_event(event, pos):
            self.active_modal = "MANUAL"
            self.setup_modal(w, h)
            return "SELECT"
            
        if self.btn_cc.handle_event(event, pos):
            self.active_modal = "CREDITS"
            self.setup_modal(w, h)
            return "SELECT"
            
        if self.btn_github.handle_event(event, pos):
            webbrowser.open(LINK_GITHUB)
            return "LINK"

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.group_index = (self.group_index + 1) % len(self.focus_group)
                self.item_index = 0
                if not self.focus_group[self.group_index][0].enabled:
                    self._move_item(1)
                else:
                    self.update_focus()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.group_index = (self.group_index - 1) % len(self.focus_group)
                self.item_index = 0
                if not self.focus_group[self.group_index][0].enabled:
                    self._move_item(1)
                else:
                    self.update_focus()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if len(self.focus_group[self.group_index]) > 1:
                    self._move_item(1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if len(self.focus_group[self.group_index]) > 1:
                    self._move_item(-1)
            elif event.key == pygame.K_RETURN:
                item = self.focus_group[self.group_index][self.item_index]
                if not item.enabled:
                    return None
                if item == self.btn_play:
                    action = "PLAY"
                elif item == self.btn_mode_single:
                    self._switch_to_single()
                    action = "SELECT"
                elif item == self.btn_mode_multi:
                    self._switch_to_multi()
                    action = "SELECT"
                elif item == self.btn_custom:
                    self._select_difficulty("CUSTOM")
                    action = "SELECT"
                else:
                    for key, b in self.diff_buttons.items():
                        if item == b:
                            self._select_difficulty(key)
                            action = "SELECT"
                            break

        if self.btn_mode_single.handle_event(event, pos):
            self._switch_to_single()
            action = "SELECT"
        elif self.btn_mode_multi.handle_event(event, pos):
            self._switch_to_multi()
            action = "SELECT"

        for key, btn in self.diff_buttons.items():
            if btn.handle_event(event, pos):
                self._select_difficulty(key)
                action = "SELECT"

        if self.btn_custom.enabled and self.btn_custom.handle_event(event, pos):
            self._select_difficulty("CUSTOM")
            action = "SELECT"

        if self.btn_play.handle_event(event, pos):
            return "PLAY"

        return action

    def draw(self, surface, sound_manager):
        w, h = surface.get_width(), surface.get_height()
        self.setup_layout(w, h)
        
        surface.fill(COLOR_BG)
        
        for i in range(10):
            offset = (self.time * 20 + i * 60) % (w + 200) - 100
            pygame.draw.circle(surface, COLOR_PANEL_DARK, (offset, h // 2), 300, 1)
            
        title_y = int(h * 0.10) + math.sin(self.time * 2) * 5
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            glow = self.title_font.render("Atrapa al Jugador", True, COLOR_PANEL_DARK)
            surface.blit(glow, glow.get_rect(center=(w // 2 + dx, title_y + dy)))
            
        title = self.title_font.render("Atrapa al Jugador", True, COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(w // 2, title_y)))
        
        subtitle = self.subtitle_font.render("Escapa de los enemigos y alcanza la meta", True, COLOR_TEXT_LIGHT)
        surface.blit(subtitle, subtitle.get_rect(center=(w // 2, int(h * 0.20))))
        
        lbl_mode = self.label_font.render("MODO DE JUEGO", True, COLOR_TEXT_LIGHT)
        surface.blit(lbl_mode, lbl_mode.get_rect(center=(w // 2, int(h * 0.26))))
        self.btn_mode_single.draw(surface)
        self.btn_mode_multi.draw(surface)
        
        lbl_diff = self.label_font.render("DIFICULTAD", True, COLOR_TEXT_LIGHT)
        surface.blit(lbl_diff, lbl_diff.get_rect(center=(w // 2, int(h * 0.41))))
        for btn in self.diff_buttons.values(): btn.draw(surface)
        self.btn_custom.draw(surface)
        
        self.btn_play.draw(surface)
        
        sound_img = self.sound_img_off if sound_manager.is_muted else self.sound_img_on
        if sound_img:
            surface.blit(sound_img, self.btn_sound)
        else:
            pygame.draw.rect(surface, COLOR_PANEL, self.btn_sound, border_radius=8)
            txt = self.label_font.render("MUTE" if sound_manager.is_muted else "ON", True, COLOR_TEXT)
            surface.blit(txt, txt.get_rect(center=self.btn_sound.center))

        footer_rect = pygame.Rect(0, h - 80, w, 80)
        pygame.draw.rect(surface, COLOR_PANEL_DARK, footer_rect)
        pygame.draw.line(surface, COLOR_PANEL, (0, h - 80), (w, h - 80), 2)
        
        credit_line1 = self.credit_title_font.render("Creadores (Grupo 14) · Programado #3", True, COLOR_TEXT)
        surface.blit(credit_line1, (30, h - 60))
        credit_line2 = self.credit_font.render("Henry Barquero Ordoñez · Fabricio Mendez Zamora", True, COLOR_TEXT_LIGHT)
        surface.blit(credit_line2, (30, h - 40))
        credit_line3 = self.credit_font.render("Prof. Enrique Gómez Jiménez · Universidad Nacional de Costa Rica", True, COLOR_TEXT_LIGHT)
        surface.blit(credit_line3, (30, h - 20))
        
        self.btn_manual.draw(surface)
        self.btn_cc.draw(surface)
        self.btn_github.draw(surface)

        if self.active_modal:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill(COLOR_OVERLAY)
            surface.blit(overlay, (0, 0))
            
            shadow_rect = self.modal_rect.copy()
            shadow_rect.y += 8
            shadow_rect.x += 8
            pygame.draw.rect(surface, (0, 0, 0, 150), shadow_rect, border_radius=15)
            
            pygame.draw.rect(surface, COLOR_PANEL, self.modal_rect, border_radius=15)
            pygame.draw.rect(surface, COLOR_EDGE, self.modal_rect, 2, border_radius=15)
            
            pygame.draw.circle(surface, COLOR_DANGER if self.close_rect.collidepoint(pygame.mouse.get_pos()) else COLOR_PANEL_DARK, self.close_rect.center, 18)
            pygame.draw.line(surface, COLOR_TEXT, (self.close_rect.centerx - 6, self.close_rect.centery - 6), (self.close_rect.centerx + 6, self.close_rect.centery + 6), 2)
            pygame.draw.line(surface, COLOR_TEXT, (self.close_rect.centerx + 6, self.close_rect.centery - 6), (self.close_rect.centerx - 6, self.close_rect.centery + 6), 2)
            
            if self.active_modal == "MANUAL":
                self.draw_manual(surface)
            elif self.active_modal == "CREDITS":
                self.draw_credits(surface)

    def draw_manual(self, surface):
        title = self.modal_title_font.render("Manual de Juego", True, COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(self.modal_rect.centerx, self.modal_rect.top + 50)))
        pygame.draw.line(surface, COLOR_PANEL_DARK, (self.modal_rect.x + 50, self.modal_rect.top + 90), (self.modal_rect.right - 50, self.modal_rect.top + 90), 2)
        
        y = self.modal_rect.top + 120
        lines = [
            ("Objetivo", "Llega a la estrella verde antes de ser atrapado por los enemigos."),
            ("Controles Jugador 1", "Teclas W, A, S, D o Mouse (en modo 1 Jugador)."),
            ("Controles Jugador 2", "Teclas de flecha (solo en modo 2 Jugadores)."),
            ("Movimiento Diagonal", "Mantén presionadas dos teclas a la vez (ej. S + D)."),
            ("Enemigos", "Se mueven por el camino más corto para atraparte."),
            ("Puntuación", "Disminuye con el tiempo y los movimientos. ¡Sé rápido!")
        ]
        
        for title_txt, desc_txt in lines:
            t_surf = self.modal_header_font.render(title_txt, True, COLOR_GOLD)
            surface.blit(t_surf, (self.modal_rect.x + 60, y))
            d_surf = self.modal_text_font.render(desc_txt, True, COLOR_TEXT_LIGHT)
            surface.blit(d_surf, (self.modal_rect.x + 60, y + 25))
            y += 55

    def draw_credits(self, surface):
        title = self.modal_title_font.render("Créditos y Recursos", True, COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(self.modal_rect.centerx, self.modal_rect.top + 50)))
        pygame.draw.line(surface, COLOR_PANEL_DARK, (self.modal_rect.x + 50, self.modal_rect.top + 90), (self.modal_rect.right - 50, self.modal_rect.top + 90), 2)
        
        lbl = self.modal_header_font.render("Efectos de sonido (OpenGameArt.org):", True, COLOR_GOLD)
        surface.blit(lbl, lbl.get_rect(center=(self.modal_rect.centerx, self.modal_rect.top + 140)))
        
        self.link_win.draw(surface)
        self.link_coin.draw(surface)


class NameEntryScreen:
    def __init__(self, w, h):
        self.title_font = pygame.font.SysFont("georgia", 56, bold=True)
        self.label_font = pygame.font.SysFont("trebuchetms", 24)
        self.btn_font = pygame.font.SysFont("georgia", 22, bold=True)

        self.p1_input = TextInput(w // 2 - 150, int(h * 0.35), 300, 50, "Jugador 1")
        self.p2_input = TextInput(w // 2 - 150, int(h * 0.50), 300, 50, "Jugador 2")

        self.btn_start = Button(w // 2 - 220, int(h * 0.65), 200, 60, "Comenzar", self.btn_font)
        self.btn_back = Button(w // 2 + 20, int(h * 0.65), 200, 60, "Volver", self.btn_font)

        self.focus_group = [
            [self.p1_input],
            [self.p2_input],
            [self.btn_start, self.btn_back]
        ]
        self.group_index = 0
        self.item_index = 0
        self.update_focus()

    def resize(self, w, h):
        self.p1_input.rect.topleft = (w // 2 - 150, int(h * 0.35))
        self.p2_input.rect.topleft = (w // 2 - 150, int(h * 0.50))
        self.btn_start.rect.topleft = (w // 2 - 220, int(h * 0.65))
        self.btn_back.rect.topleft = (w // 2 + 20, int(h * 0.65))

    def update_focus(self):
        for g in self.focus_group:
            for item in g:
                if hasattr(item, 'focused'): item.focused = False
                if hasattr(item, 'active'): item.active = False
                    
        item = self.focus_group[self.group_index][self.item_index]
        if hasattr(item, 'focused'): item.focused = True
        if hasattr(item, 'active'): item.active = True

    def handle_events(self, event, pos):
        action = None
        for g in self.focus_group:
            for item in g:
                if hasattr(item, 'check_hover'):
                    item.check_hover(pos)

        current_item = self.focus_group[self.group_index][self.item_index]
        is_typing = isinstance(current_item, TextInput) and current_item.active

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.group_index = (self.group_index + 1) % len(self.focus_group)
                self.item_index = 0
                self.update_focus()
                return action

            if not is_typing:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.group_index = (self.group_index + 1) % len(self.focus_group)
                    self.item_index = 0
                    self.update_focus()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.group_index = (self.group_index - 1) % len(self.focus_group)
                    self.item_index = 0
                    self.update_focus()
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if len(self.focus_group[self.group_index]) > 1:
                        self.item_index = (self.item_index + 1) % len(self.focus_group[self.group_index])
                        self.update_focus()
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if len(self.focus_group[self.group_index]) > 1:
                        self.item_index = (self.item_index - 1) % len(self.focus_group[self.group_index])
                        self.update_focus()
                elif event.key == pygame.K_RETURN:
                    item = self.focus_group[self.group_index][self.item_index]
                    if item == self.btn_start:
                        action = "START"
                    elif item == self.btn_back:
                        action = "BACK"
                    elif isinstance(item, TextInput):
                        if self.group_index < len(self.focus_group) - 1:
                            self.group_index += 1
                            self.item_index = 0
                            self.update_focus()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for gi, g in enumerate(self.focus_group):
                for ii, item in enumerate(g):
                    if item.rect.collidepoint(pos):
                        self.group_index = gi
                        self.item_index = ii
                        self.update_focus()

        for g in self.focus_group:
            for item in g:
                if hasattr(item, 'handle_event'):
                    if item.handle_event(event, pos):
                        if item == self.btn_start: action = "START"
                        elif item == self.btn_back: action = "BACK"

        return action

    def draw(self, surface):
        w, h = surface.get_width(), surface.get_height()
        self.resize(w, h)
        
        surface.fill(COLOR_BG)
        title = self.title_font.render("Ingresa los Nombres", True, COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(w // 2, int(h * 0.20))))
        
        lbl1 = self.label_font.render("Jugador 1 (WASD):", True, COLOR_TEXT_LIGHT)
        surface.blit(lbl1, lbl1.get_rect(center=(w // 2, int(h * 0.30))))
        self.p1_input.draw(surface)

        lbl2 = self.label_font.render("Jugador 2 (Flechas):", True, COLOR_TEXT_LIGHT)
        surface.blit(lbl2, lbl2.get_rect(center=(w // 2, int(h * 0.45))))
        self.p2_input.draw(surface)

        self.btn_start.draw(surface)
        self.btn_back.draw(surface)


class GraphEditorScreen:
    def __init__(self, w, h):
        self.title_font = pygame.font.SysFont("georgia", 40, bold=True)
        self.label_font = pygame.font.SysFont("trebuchetms", 15, bold=True)
        self.spinner_font = pygame.font.SysFont("trebuchetms", 20, bold=True)
        self.tool_font = pygame.font.SysFont("trebuchetms", 16, bold=True)
        self.btn_font = pygame.font.SysFont("georgia", 22, bold=True)
        self.node_font = pygame.font.SysFont("trebuchetms", 16, bold=True)
        self.status_font = pygame.font.SysFont("trebuchetms", 14)
        self.error_font = pygame.font.SysFont("trebuchetms", 15, bold=True)

        self.rows_spinner = None
        self.cols_spinner = None
        self.enemies_spinner = None
        self.btn_tool_player = None
        self.btn_tool_enemy = None
        self.btn_tool_goal = None
        self.btn_tool_clear = None
        self.btn_random = None
        self.btn_clear_all = None
        self.btn_play = None
        self.btn_back = None

        self.selected_tool = "PLAYER"
        self.player_node = None
        self.enemy_nodes = set()
        self.goal_node = None
        self.graph = Graph(rows=3, cols=4, extra_edges=0.0)
        self.hovered_node = None
        self._node_pixels = {}
        self._node_radius = 30
        self.error_message = ""
        self.error_timer = 0.0

    def _max_enemies(self):
        r = self.rows_spinner.value if self.rows_spinner else 3
        c = self.cols_spinner.value if self.cols_spinner else 4
        return max(EDITOR_MIN_ENEMIES, min(EDITOR_MAX_ENEMIES, r * c - 2))

    def setup_layout(self, w, h):
        if self.btn_play is not None and self.btn_play.rect.y == h - 120:
            return

        cur_rows = self.rows_spinner.value if self.rows_spinner else 3
        cur_cols = self.cols_spinner.value if self.cols_spinner else 4
        cur_enemies = self.enemies_spinner.value if self.enemies_spinner else 1

        panel_x = 20
        panel_y = 110

        self.rows_spinner = Spinner(panel_x + 20, panel_y + 20, 240, 40, "Filas (3-5)",
                                    EDITOR_MIN_ROWS, EDITOR_MAX_ROWS, cur_rows,
                                    self.spinner_font, self.label_font)
        self.cols_spinner = Spinner(panel_x + 20, panel_y + 100, 240, 40, "Columnas",
                                    max(EDITOR_MIN_COLS, cur_rows + 1), EDITOR_MAX_COLS, cur_cols,
                                    self.spinner_font, self.label_font)
        max_e = max(EDITOR_MIN_ENEMIES, min(EDITOR_MAX_ENEMIES, cur_rows * cur_cols - 2))
        self.enemies_spinner = Spinner(panel_x + 20, panel_y + 180, 240, 40, "Enemigos",
                                       EDITOR_MIN_ENEMIES, max_e, cur_enemies,
                                       self.spinner_font, self.label_font)

        tool_y = panel_y + 260
        tool_w = 115
        tool_h = 40
        self.btn_tool_player = Button(panel_x + 20, tool_y, tool_w, tool_h, "Jugador", self.tool_font)
        self.btn_tool_enemy = Button(panel_x + 20 + tool_w + 10, tool_y, tool_w, tool_h, "Enemigo", self.tool_font)
        self.btn_tool_goal = Button(panel_x + 20, tool_y + tool_h + 10, tool_w, tool_h, "Meta", self.tool_font)
        self.btn_tool_clear = Button(panel_x + 20 + tool_w + 10, tool_y + tool_h + 10, tool_w, tool_h, "Borrar", self.tool_font)

        action_y = tool_y + tool_h * 2 + 30
        self.btn_random = Button(panel_x + 20, action_y, tool_w, tool_h, "Aleatorio", self.tool_font)
        self.btn_clear_all = Button(panel_x + 20 + tool_w + 10, action_y, tool_w, tool_h, "Limpiar", self.tool_font)

        self.btn_play = Button(panel_x + 20, h - 120, 115, 50, "Jugar", self.btn_font)
        self.btn_back = Button(panel_x + 20 + 115 + 10, h - 120, 115, 50, "Volver", self.btn_font)

    def _graph_rect(self, w, h):
        return pygame.Rect(320, 90, w - 340, h - 140)

    def _compute_node_pixels(self, rect):
        positions = {}
        rows = self.rows_spinner.value if self.rows_spinner else 3
        cols = self.cols_spinner.value if self.cols_spinner else 4
        pad_x, pad_y = 60, 60
        usable_w = rect.width - pad_x * 2
        usable_h = rect.height - pad_y * 2
        for nid, (r, c) in self.graph.positions.items():
            x = rect.x + pad_x + (usable_w * c / (cols - 1) if cols > 1 else usable_w / 2)
            y = rect.y + pad_y + (usable_h * r / (rows - 1) if rows > 1 else usable_h / 2)
            positions[nid] = pygame.Vector2(x, y)

        if cols > 1 and rows > 1:
            max_by_x = usable_w / (cols - 1) / 2 - 4
            max_by_y = usable_h / (rows - 1) / 2 - 4
        else:
            max_by_x = usable_w / 4
            max_by_y = usable_h / 4
        self._node_radius = int(max(10, min(max_by_x, max_by_y, 32)))
        return positions

    def _get_node_at(self, pos, node_pixels):
        for nid, p in node_pixels.items():
            if (pygame.Vector2(p) - pygame.Vector2(pos)).length() <= self._node_radius + 3:
                return nid
        return None

    def _rebuild(self):
        r = self.rows_spinner.value
        c = self.cols_spinner.value
        self.graph = Graph(rows=r, cols=c, extra_edges=0.0)
        self.player_node = None
        self.enemy_nodes = set()
        self.goal_node = None
        self.hovered_node = None
        max_e = max(EDITOR_MIN_ENEMIES, min(EDITOR_MAX_ENEMIES, r * c - 2))
        self.enemies_spinner.set_bounds(EDITOR_MIN_ENEMIES, max_e)

    def _apply_tool(self, node):
        if node is None:
            return
        if self.selected_tool == "PLAYER":
            if node in self.enemy_nodes or node == self.goal_node:
                return
            self.player_node = node
        elif self.selected_tool == "ENEMY":
            if node == self.player_node or node == self.goal_node:
                return
            if node in self.enemy_nodes:
                self.enemy_nodes.discard(node)
            elif len(self.enemy_nodes) < self.enemies_spinner.value:
                self.enemy_nodes.add(node)
        elif self.selected_tool == "GOAL":
            if node == self.player_node or node in self.enemy_nodes:
                return
            self.goal_node = node
        elif self.selected_tool == "CLEAR":
            if node == self.player_node:
                self.player_node = None
            self.enemy_nodes.discard(node)
            if node == self.goal_node:
                self.goal_node = None

    def _randomize(self):
        nodes = list(self.graph.all_nodes())
        if len(nodes) < 3:
            return
        n_enemies = min(self.enemies_spinner.value, len(nodes) - 2)
        sample = random.sample(nodes, 2 + n_enemies)
        self.player_node = sample[0]
        self.goal_node = sample[1]
        self.enemy_nodes = set(sample[2:])

    def _clear_all(self):
        self.player_node = None
        self.enemy_nodes = set()
        self.goal_node = None

    def _set_error(self, msg):
        self.error_message = msg
        self.error_timer = 2.5

    def _validate(self):
        if self.player_node is None:
            self._set_error("Marca el nodo del jugador")
            return False
        if self.goal_node is None:
            self._set_error("Marca el nodo meta")
            return False
        target = self.enemies_spinner.value
        if len(self.enemy_nodes) != target:
            if len(self.enemy_nodes) < target:
                self._set_error(f"Faltan {target - len(self.enemy_nodes)} enemigo(s)")
            else:
                self._set_error(f"Sobran {len(self.enemy_nodes) - target} enemigo(s)")
            return False
        return True

    def get_config(self):
        return {
            "rows": self.rows_spinner.value,
            "cols": self.cols_spinner.value,
            "player": self.player_node,
            "enemies": list(self.enemy_nodes),
            "goal": self.goal_node,
        }

    def update(self, dt):
        if self.error_timer > 0:
            self.error_timer -= dt
            if self.error_timer <= 0:
                self.error_message = ""

    def handle_events(self, event, pos, w, h):
        self.setup_layout(w, h)
        graph_rect = self._graph_rect(w, h)
        node_pixels = self._compute_node_pixels(graph_rect)
        self._node_pixels = node_pixels
        action = None

        for btn in (self.btn_tool_player, self.btn_tool_enemy, self.btn_tool_goal,
                    self.btn_tool_clear, self.btn_random, self.btn_clear_all,
                    self.btn_play, self.btn_back):
            btn.check_hover(pos)

        self.rows_spinner.check_hover(pos)
        self.cols_spinner.check_hover(pos)
        self.enemies_spinner.check_hover(pos)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "BACK"

        r_change = self.rows_spinner.handle_event(event, pos)
        if r_change == "CHANGED":
            min_cols = max(EDITOR_MIN_COLS, self.rows_spinner.value + 1)
            self.cols_spinner.set_bounds(min_cols, EDITOR_MAX_COLS)
            self._rebuild()

        c_change = self.cols_spinner.handle_event(event, pos)
        if c_change == "CHANGED":
            max_rows = min(EDITOR_MAX_ROWS, self.cols_spinner.value - 1)
            self.rows_spinner.set_bounds(EDITOR_MIN_ROWS, max_rows)
            self._rebuild()

        e_change = self.enemies_spinner.handle_event(event, pos)
        if e_change == "CHANGED":
            while len(self.enemy_nodes) > self.enemies_spinner.value:
                self.enemy_nodes.pop()

        if self.btn_tool_player.handle_event(event, pos):
            self.selected_tool = "PLAYER"
        elif self.btn_tool_enemy.handle_event(event, pos):
            self.selected_tool = "ENEMY"
        elif self.btn_tool_goal.handle_event(event, pos):
            self.selected_tool = "GOAL"
        elif self.btn_tool_clear.handle_event(event, pos):
            self.selected_tool = "CLEAR"

        if self.btn_random.handle_event(event, pos):
            self._randomize()
        elif self.btn_clear_all.handle_event(event, pos):
            self._clear_all()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if graph_rect.collidepoint(pos):
                node = self._get_node_at(pos, node_pixels)
                if node is not None:
                    self._apply_tool(node)

        if self.btn_play.handle_event(event, pos):
            if self._validate():
                return "PLAY"

        if self.btn_back.handle_event(event, pos):
            return "BACK"

        return action

    def draw(self, surface):
        w, h = surface.get_width(), surface.get_height()
        self.setup_layout(w, h)

        surface.fill(COLOR_BG)

        title = self.title_font.render("Editor de Grafo Personalizado", True, COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(w // 2, 45)))

        panel_rect = pygame.Rect(10, 90, 300, h - 140)
        pygame.draw.rect(surface, COLOR_PANEL, panel_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_EDGE, panel_rect, 2, border_radius=12)

        self.rows_spinner.draw(surface)
        self.cols_spinner.draw(surface)
        self.enemies_spinner.draw(surface)

        lbl_tool = self.label_font.render("HERRAMIENTA", True, COLOR_TEXT_LIGHT)
        surface.blit(lbl_tool, (30, self.btn_tool_player.rect.y - 22))

        self.btn_tool_player.selected = (self.selected_tool == "PLAYER")
        self.btn_tool_enemy.selected = (self.selected_tool == "ENEMY")
        self.btn_tool_goal.selected = (self.selected_tool == "GOAL")
        self.btn_tool_clear.selected = (self.selected_tool == "CLEAR")
        self.btn_tool_player.draw(surface)
        self.btn_tool_enemy.draw(surface)
        self.btn_tool_goal.draw(surface)
        self.btn_tool_clear.draw(surface)

        self.btn_random.draw(surface)
        self.btn_clear_all.draw(surface)

        status_y = self.btn_random.rect.y + 60
        player_txt = self.player_node if self.player_node else "—"
        goal_txt = self.goal_node if self.goal_node else "—"
        st1 = self.status_font.render(f"Jugador: {player_txt}", True, COLOR_PLAYER)
        st2 = self.status_font.render(f"Enemigos: {len(self.enemy_nodes)}/{self.enemies_spinner.value}", True, COLOR_COMPUTER)
        st3 = self.status_font.render(f"Meta: {goal_txt}", True, COLOR_GOAL)
        surface.blit(st1, (30, status_y))
        surface.blit(st2, (30, status_y + 22))
        surface.blit(st3, (30, status_y + 44))

        if self.error_message and self.error_timer > 0:
            err = self.error_font.render(self.error_message, True, COLOR_DANGER)
            surface.blit(err, (30, status_y + 76))

        self.btn_play.draw(surface)
        self.btn_back.draw(surface)

        graph_rect = self._graph_rect(w, h)
        pygame.draw.rect(surface, COLOR_PANEL, graph_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_EDGE, graph_rect, 2, border_radius=12)

        node_pixels = self._compute_node_pixels(graph_rect)
        self._node_pixels = node_pixels
        self.hovered_node = self._get_node_at(pygame.mouse.get_pos(), node_pixels) if graph_rect.collidepoint(pygame.mouse.get_pos()) else None

        self._draw_graph(surface, node_pixels)

    def _draw_graph(self, surface, node_pixels):
        drawn = set()
        for node, neighbors in self.graph.adjacency_list.items():
            for nb in neighbors:
                edge = tuple(sorted([node, nb]))
                if edge in drawn:
                    continue
                p1, p2 = node_pixels[node], node_pixels[nb]
                pygame.draw.line(surface, COLOR_EDGE, p1, p2, 4)
                drawn.add(edge)

        r = self._node_radius
        for nid, pos in node_pixels.items():
            pygame.draw.circle(surface, COLOR_NODE, pos, r)
            if nid == self.player_node:
                pygame.draw.circle(surface, COLOR_PLAYER, pos, max(4, r - 4))
            elif nid in self.enemy_nodes:
                pygame.draw.circle(surface, COLOR_COMPUTER, pos, max(4, r - 4))
            elif nid == self.goal_node:
                pygame.draw.circle(surface, COLOR_GOAL, pos, max(4, r - 4))
            pygame.draw.circle(surface, COLOR_EDGE, pos, r, 2)

            if nid == self.player_node or nid in self.enemy_nodes or nid == self.goal_node:
                txt_color = (30, 30, 40)
            else:
                txt_color = (180, 190, 200)
            txt = self.node_font.render(nid, True, txt_color)
            surface.blit(txt, txt.get_rect(center=pos))

            if nid == self.hovered_node:
                pygame.draw.circle(surface, COLOR_GOLD, pos, r + 4, 2)


class GameOverScreen:
    def __init__(self, state, w, h):
        self.stats = state.get_stats()
        self.title_font = pygame.font.SysFont("georgia", 64, bold=True)
        self.label_font = pygame.font.SysFont("trebuchetms", 22)
        self.value_font = pygame.font.SysFont("trebuchetms", 30, bold=True)
        self.btn_font = pygame.font.SysFont("georgia", 22, bold=True)
        
        self.panel_rect = pygame.Rect(w // 2 - 350, h // 2 - 300, 700, 600)
        self.btn_retry = Button(self.panel_rect.centerx - 220, self.panel_rect.bottom - 100, 200, 60, "Reintentar", self.btn_font)
        self.btn_menu = Button(self.panel_rect.centerx + 20, self.panel_rect.bottom - 100, 200, 60, "Menú Principal", self.btn_font)
        
        self.focus_group = [[self.btn_retry, self.btn_menu]]
        self.group_index = 0
        self.item_index = 0
        self.update_focus()

    def resize(self, w, h):
        self.panel_rect = pygame.Rect(w // 2 - 350, h // 2 - 300, 700, 600)
        self.btn_retry.rect.topleft = (self.panel_rect.centerx - 220, self.panel_rect.bottom - 100)
        self.btn_menu.rect.topleft = (self.panel_rect.centerx + 20, self.panel_rect.bottom - 100)

    def update_focus(self):
        for g in self.focus_group:
            for item in g: item.focused = False
        self.focus_group[self.group_index][self.item_index].focused = True

    def handle_events(self, event, pos, w, h):
        self.resize(w, h)
        self.btn_retry.check_hover(pos)
        self.btn_menu.check_hover(pos)
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.item_index = (self.item_index + 1) % len(self.focus_group[self.group_index])
                self.update_focus()
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.item_index = (self.item_index - 1) % len(self.focus_group[self.group_index])
                self.update_focus()
            elif event.key == pygame.K_RETURN:
                item = self.focus_group[self.group_index][self.item_index]
                if item == self.btn_retry: return "RETRY"
                elif item == self.btn_menu: return "MENU"

        if self.btn_retry.handle_event(event, pos):
            return "RETRY"
        if self.btn_menu.handle_event(event, pos):
            return "MENU"
        return None

    def format_time(self, seconds):
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"

    def draw(self, surface):
        w, h = surface.get_width(), surface.get_height()
        self.resize(w, h)
        
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        surface.blit(overlay, (0, 0))
        
        pygame.draw.rect(surface, COLOR_PANEL, self.panel_rect, border_radius=20)
        pygame.draw.rect(surface, COLOR_TEXT, self.panel_rect, 3, border_radius=20)
        
        win = self.stats["ganador"] in ("PLAYER", "PLAYER1")
        if self.stats["mode"] == MODE_SINGLE:
            title_text = "¡VICTORIA!" if win else "DERROTA"
            sub_text = "Llegaste a la meta" if win else "Fuiste atrapado por los enemigos"
        else:
            winner_name = self.stats["p1_name"] if win else self.stats["p2_name"]
            title_text = "¡FIN DEL JUEGO!"
            sub_text = f"Ganador: {winner_name}"
            
        title_color = COLOR_SUCCESS if win else COLOR_DANGER
        title = self.title_font.render(title_text, True, title_color)
        surface.blit(title, title.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 100)))
        
        sub = self.label_font.render(sub_text, True, COLOR_TEXT_LIGHT)
        surface.blit(sub, sub.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 170)))
        
        y = self.panel_rect.top + 250
        stats_to_show = [("Tiempo", self.format_time(self.stats["tiempo"]), COLOR_TEXT)]
        if self.stats["mode"] == MODE_SINGLE:
            stats_to_show.extend([
                ("Movimientos", str(self.stats["movimientos"]), COLOR_TEXT),
                ("Puntos", str(self.stats["puntos"]), COLOR_GOLD),
            ])
        else:
            stats_to_show.append(("Movimientos Totales", str(self.stats["movimientos"]), COLOR_TEXT))
            
        for label, value, color in stats_to_show:
            lbl = self.label_font.render(label, True, COLOR_TEXT_LIGHT)
            val = self.value_font.render(value, True, color)
            surface.blit(lbl, lbl.get_rect(center=(self.panel_rect.centerx - 150, y)))
            surface.blit(val, val.get_rect(center=(self.panel_rect.centerx + 150, y)))
            pygame.draw.line(surface, COLOR_PANEL_DARK, (self.panel_rect.centerx - 260, y + 30), (self.panel_rect.centerx + 260, y + 30), 1)
            y += 70
            
        self.btn_retry.draw(surface)
        self.btn_menu.draw(surface)