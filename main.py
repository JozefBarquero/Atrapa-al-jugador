import pygame
import sys
from config import (WIDTH, HEIGHT, FPS, COLOR_BG, TOP_HUD_HEIGHT,
                    BOTTOM_PANEL_HEIGHT, SCREEN_MENU, SCREEN_PLAYING,
                    SCREEN_GAMEOVER, SCREEN_NAME_ENTRY, SCREEN_GRAPH_EDITOR,
                    DIFFICULTIES, MODE_SINGLE, MODE_MULTI)
from models.graph import Graph
from models.game_state import GameState
from utils.asset_generator import generate_assets
from utils.sound_manager import SoundManager
from views.graph_renderer import GraphRenderer
from views.ui_manager import UIManager
from views.screens import MenuScreen, GameOverScreen, NameEntryScreen, GraphEditorScreen

class App:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Atrapa al Jugador")
        self.clock = pygame.time.Clock()
        self.running = True

        generate_assets()
        self.sound_manager = SoundManager()
        self.sound_manager.set_music_mode("menu")

        self.screen_state = SCREEN_MENU
        self.menu = MenuScreen()
        self.name_entry_screen = None
        self.graph_editor = None
        self.current_difficulty = "FACIL"
        self.difficulty_data = DIFFICULTIES["FACIL"]

        self.game = None
        self.ui = UIManager()
        self.game_over_screen = None
        self.computer_timer = 0
        self.end_delay = 0

        self.pending_p1_move = None
        self.pending_p1_timer = 0.0
        self.pending_p2_move = None
        self.pending_p2_timer = 0.0

    def get_board_rect(self):
        w = self.screen.get_width()
        h = self.screen.get_height()
        return pygame.Rect(40, TOP_HUD_HEIGHT + 30, w - 80, h - TOP_HUD_HEIGHT - BOTTOM_PANEL_HEIGHT - 60)

    def start_game(self, difficulty_key, mode, p1_name, p2_name, custom_config=None):
        if custom_config:
            graph = Graph(rows=custom_config["rows"], cols=custom_config["cols"], extra_edges=0.0)
            enemies = len(custom_config["enemies"])
        else:
            cfg = DIFFICULTIES[difficulty_key]
            graph = Graph(rows=cfg["rows"], cols=cfg["cols"], extra_edges=0.2)
            enemies = cfg["enemies"]

        if not p1_name.strip(): p1_name = "Jugador 1"
        if not p2_name.strip(): p2_name = "Jugador 2"

        state = GameState(graph, enemies, mode, p1_name, p2_name, custom_config=custom_config)

        self.game = {
            "graph": graph,
            "state": state,
            "renderer": GraphRenderer(graph, self.get_board_rect()),
            "difficulty": difficulty_key,
            "custom_config": custom_config,
        }
        self.game["renderer"].sync_with_state(state)
        self.ui = UIManager()
        self.screen_state = SCREEN_PLAYING
        self.sound_manager.set_music_mode("game")
        self.sound_manager.unduck_music()
        self.computer_timer = 0
        self.end_delay = 0
        
        self.pending_p1_move = None
        self.pending_p1_timer = 0.0
        self.pending_p2_move = None
        self.pending_p2_timer = 0.0

    def _restart_current_game(self):
        config = self.game.get("custom_config") if self.game else None
        self.start_game(self.game["difficulty"], self.game["state"].mode,
                        self.game["state"].p1_name, self.game["state"].p2_name,
                        custom_config=config)

    def handle_events(self):
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            elif event.type == pygame.WINDOWRESTORED:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                if self.screen_state == SCREEN_PLAYING and self.game:
                    self.game["renderer"].update_rect(self.get_board_rect())
                    self.game["renderer"].sync_with_state(self.game["state"])
                elif self.screen_state == SCREEN_GAMEOVER and self.game_over_screen:
                    self.game_over_screen.resize(self.screen.get_width(), self.screen.get_height())
                elif self.screen_state == SCREEN_NAME_ENTRY and self.name_entry_screen:
                    self.name_entry_screen.resize(self.screen.get_width(), self.screen.get_height())
                continue
            elif event.type == pygame.VIDEORESIZE:
                if event.w > 0 and event.h > 0:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    if self.screen_state == SCREEN_PLAYING and self.game:
                        self.game["renderer"].update_rect(self.get_board_rect())
                        self.game["renderer"].sync_with_state(self.game["state"])
                    elif self.screen_state == SCREEN_GAMEOVER and self.game_over_screen:
                        self.game_over_screen.resize(self.screen.get_width(), self.screen.get_height())
                    elif self.screen_state == SCREEN_NAME_ENTRY and self.name_entry_screen:
                        self.name_entry_screen.resize(self.screen.get_width(), self.screen.get_height())
                continue

            if self.screen_state == SCREEN_MENU:
                action = self.menu.handle_events(event, pos, self.sound_manager, self.screen.get_width(), self.screen.get_height())
                if action == "SELECT":
                    self.sound_manager.play("select")
                elif action == "PLAY":
                    self.sound_manager.play("select")
                    if self.menu.selected_difficulty == "CUSTOM" and self.menu.mode == MODE_SINGLE:
                        self.graph_editor = GraphEditorScreen(self.screen.get_width(), self.screen.get_height())
                        self.screen_state = SCREEN_GRAPH_EDITOR
                    elif self.menu.mode == MODE_MULTI:
                        self.screen_state = SCREEN_NAME_ENTRY
                        self.name_entry_screen = NameEntryScreen(self.screen.get_width(), self.screen.get_height())
                    else:
                        self.start_game(self.menu.selected_difficulty, MODE_SINGLE, "Jugador 1", "")

            elif self.screen_state == SCREEN_NAME_ENTRY:
                action = self.name_entry_screen.handle_events(event, pos)
                if action == "START":
                    self.sound_manager.play("select")
                    self.start_game(self.menu.selected_difficulty, MODE_MULTI, 
                                    self.name_entry_screen.p1_input.text, 
                                    self.name_entry_screen.p2_input.text)
                elif action == "BACK":
                    self.sound_manager.play("select")
                    self.screen_state = SCREEN_MENU

            elif self.screen_state == SCREEN_GRAPH_EDITOR:
                action = self.graph_editor.handle_events(event, pos, self.screen.get_width(), self.screen.get_height())
                if action == "PLAY":
                    self.sound_manager.play("select")
                    config = self.graph_editor.get_config()
                    self.start_game("CUSTOM", MODE_SINGLE, "Jugador 1", "", custom_config=config)
                elif action == "BACK":
                    self.sound_manager.play("select")
                    self.screen_state = SCREEN_MENU

            elif self.screen_state == SCREEN_PLAYING:
                action = self.ui.handle_events(event, pos, self.screen.get_width(), self.screen.get_height())
                state = self.game["state"]
                
                if action == "RESTART":
                    self._restart_current_game()
                elif action == "MENU":
                    self.sound_manager.set_music_mode("menu")
                    self.sound_manager.unduck_music()
                    self.screen_state = SCREEN_MENU

                if self.screen_state == SCREEN_PLAYING and not state.winner:
                    if state.mode == MODE_SINGLE and state.turn == "PLAYER":
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            clicked = self.game["renderer"].get_clicked_node(pos)
                            if clicked:
                                self.pending_p1_move = None
                                if state.move_player(clicked):
                                    self.sound_manager.play("move")
                                    self.game["renderer"].sync_with_state(state)
                        elif event.type == pygame.KEYDOWN:
                            dr, dc = 0, 0
                            if event.key in (pygame.K_w, pygame.K_UP): dr = -1
                            if event.key in (pygame.K_s, pygame.K_DOWN): dr = 1
                            if event.key in (pygame.K_a, pygame.K_LEFT): dc = -1
                            if event.key in (pygame.K_d, pygame.K_RIGHT): dc = 1
                            
                            if dr != 0 or dc != 0:
                                if self.pending_p1_move is None:
                                    self.pending_p1_move = [dr, dc]
                                else:
                                    self.pending_p1_move[0] += dr
                                    self.pending_p1_move[1] += dc
                                self.pending_p1_timer = 0.12

                    elif state.mode == MODE_MULTI:
                        if event.type == pygame.KEYDOWN:
                            if state.turn == "PLAYER1":
                                dr, dc = 0, 0
                                if event.key == pygame.K_w: dr = -1
                                if event.key == pygame.K_s: dr = 1
                                if event.key == pygame.K_a: dc = -1
                                if event.key == pygame.K_d: dc = 1
                                if dr != 0 or dc != 0:
                                    if self.pending_p1_move is None:
                                        self.pending_p1_move = [dr, dc]
                                    else:
                                        self.pending_p1_move[0] += dr
                                        self.pending_p1_move[1] += dc
                                    self.pending_p1_timer = 0.12
                            elif state.turn == "PLAYER2":
                                dr, dc = 0, 0
                                if event.key == pygame.K_UP: dr = -1
                                if event.key == pygame.K_DOWN: dr = 1
                                if event.key == pygame.K_LEFT: dc = -1
                                if event.key == pygame.K_RIGHT: dc = 1
                                if dr != 0 or dc != 0:
                                    if self.pending_p2_move is None:
                                        self.pending_p2_move = [dr, dc]
                                    else:
                                        self.pending_p2_move[0] += dr
                                        self.pending_p2_move[1] += dc
                                    self.pending_p2_timer = 0.12

            elif self.screen_state == SCREEN_GAMEOVER:
                action = self.game_over_screen.handle_events(event, pos, self.screen.get_width(), self.screen.get_height())
                if action == "RETRY":
                    self.sound_manager.unduck_music()
                    self._restart_current_game()
                elif action == "MENU":
                    self.sound_manager.set_music_mode("menu")
                    self.sound_manager.unduck_music()
                    self.screen_state = SCREEN_MENU

    def update(self, dt):
        self.sound_manager.update(dt)

        if self.screen_state == SCREEN_MENU:
            self.menu.update(dt)
        elif self.screen_state == SCREEN_GRAPH_EDITOR:
            self.graph_editor.update(dt)
        elif self.screen_state == SCREEN_PLAYING:
            state = self.game["state"]
            renderer = self.game["renderer"]
            state.update_time()
            renderer.update(dt)

            if not state.winner:
                if state.mode == MODE_SINGLE and state.turn == "PLAYER":
                    if self.pending_p1_move is not None:
                        self.pending_p1_timer -= dt
                        if self.pending_p1_timer <= 0:
                            dr = max(-1, min(1, self.pending_p1_move[0]))
                            dc = max(-1, min(1, self.pending_p1_move[1]))
                            if dr != 0 or dc != 0:
                                target = state.get_neighbor_in_direction(dr, dc, state.player_pos)
                                if target and state.move_player(target):
                                    self.sound_manager.play("move")
                                    self.game["renderer"].sync_with_state(state)
                            self.pending_p1_move = None
                            
                elif state.mode == MODE_MULTI:
                    if state.turn == "PLAYER1" and self.pending_p1_move is not None:
                        self.pending_p1_timer -= dt
                        if self.pending_p1_timer <= 0:
                            dr = max(-1, min(1, self.pending_p1_move[0]))
                            dc = max(-1, min(1, self.pending_p1_move[1]))
                            if dr != 0 or dc != 0:
                                target = state.get_neighbor_in_direction(dr, dc, state.player_pos)
                                if target and state.move_player(target):
                                    self.sound_manager.play("move")
                                    self.game["renderer"].sync_with_state(state)
                            self.pending_p1_move = None
                            
                    elif state.turn == "PLAYER2" and self.pending_p2_move is not None:
                        self.pending_p2_timer -= dt
                        if self.pending_p2_timer <= 0:
                            dr = max(-1, min(1, self.pending_p2_move[0]))
                            dc = max(-1, min(1, self.pending_p2_move[1]))
                            if dr != 0 or dc != 0:
                                target = state.get_neighbor_in_direction(dr, dc, state.player2_pos)
                                if target and state.move_player(target):
                                    self.sound_manager.play("move")
                                    self.game["renderer"].sync_with_state(state)
                            self.pending_p2_move = None

            if not state.winner and state.mode == MODE_SINGLE and state.turn == "COMPUTER":
                now = pygame.time.get_ticks()
                if now - self.computer_timer > 500:
                    state.move_computers()
                    renderer.sync_with_state(state)
                    self.computer_timer = now

            if state.winner:
                self.pending_p1_move = None
                self.pending_p2_move = None
                if self.end_delay == 0:
                    self.end_delay = 1.2
                    self.sound_manager.duck_music()
                    if state.winner in ("PLAYER", "PLAYER1"):
                        self.sound_manager.play("win")
                    else:
                        self.sound_manager.play("lose")
                        
                self.end_delay -= dt
                if self.end_delay <= 0:
                    self.game_over_screen = GameOverScreen(state, self.screen.get_width(), self.screen.get_height())
                    self.screen_state = SCREEN_GAMEOVER

    def draw(self):
        self.screen.fill(COLOR_BG)
        if self.screen_state == SCREEN_MENU:
            self.menu.draw(self.screen, self.sound_manager)

        elif self.screen_state == SCREEN_NAME_ENTRY:
            self.name_entry_screen.draw(self.screen)

        elif self.screen_state == SCREEN_GRAPH_EDITOR:
            self.graph_editor.draw(self.screen)

        elif self.screen_state == SCREEN_PLAYING:
            self.ui.draw_hud(self.screen, self.game["state"])
            self.game["renderer"].draw_board(self.screen, self.game["state"])
            self.ui.draw_bottom_panel(self.screen)

        elif self.screen_state == SCREEN_GAMEOVER:
            self.game["renderer"].draw_board(self.screen, self.game["state"])
            self.game_over_screen.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.run()