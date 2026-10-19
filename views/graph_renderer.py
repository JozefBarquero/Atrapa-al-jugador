import pygame
import cairosvg
import io
import os
import math
from config import (ASSETS_DIR, COLOR_EDGE, COLOR_SHADOW, NODE_RADIUS,
                    EDGE_WIDTH, ANIMATION_SPEED, MODE_MULTI, COLOR_GOLD)

class GraphRenderer:
    def __init__(self, graph, board_rect):
        self.graph = graph
        self.board_rect = board_rect
        self.images = self.load_images()
        self.node_font = pygame.font.SysFont("trebuchetms", 22, bold=True)
        self.node_pixels = self._compute_node_positions()
        self.visual_positions = {}
        self.target_positions = {}
        self.goal_pulse = 0.0

    def update_rect(self, new_rect):
        self.board_rect = new_rect
        self.node_pixels = self._compute_node_positions()

    def load_svg(self, filename):
        path = os.path.join(ASSETS_DIR, "nodes", filename)
        png_data = cairosvg.svg2png(url=path, output_width=NODE_RADIUS*2, output_height=NODE_RADIUS*2)
        return pygame.image.load(io.BytesIO(png_data)).convert_alpha()

    def load_images(self):
        return {
            "node": self.load_svg("node.svg"),
            "player": self.load_svg("player.svg"),
            "player2": self.load_svg("player2.svg"),
            "computer": self.load_svg("computer.svg"),
            "goal": self.load_svg("goal.svg")
        }

    def _compute_node_positions(self):
        positions = {}
        rows, cols = self.graph.rows, self.graph.cols
        pad_x, pad_y = 80, 80
        usable_w = self.board_rect.width - pad_x * 2
        usable_h = self.board_rect.height - pad_y * 2
        for nid, (r, c) in self.graph.positions.items():
            x = self.board_rect.x + pad_x + (usable_w * c / (cols - 1) if cols > 1 else usable_w / 2)
            y = self.board_rect.y + pad_y + (usable_h * r / (rows - 1) if rows > 1 else usable_h / 2)
            positions[nid] = pygame.Vector2(x, y)
        return positions

    def sync_with_state(self, state):
        self.target_positions["player"] = self.node_pixels[state.player_pos].copy()
        if state.mode == MODE_MULTI:
            if "player2" not in self.visual_positions:
                self.visual_positions["player2"] = self.node_pixels[state.player2_pos].copy()
            self.target_positions["player2"] = self.node_pixels[state.player2_pos].copy()
        else:
            for i, pos in enumerate(state.computer_positions):
                self.target_positions[f"enemy_{i}"] = self.node_pixels[pos].copy()
                
        for key, target in self.target_positions.items():
            if key not in self.visual_positions:
                self.visual_positions[key] = pygame.Vector2(target)

    def update(self, dt):
        for key, target in self.target_positions.items():
            current = self.visual_positions.get(key, pygame.Vector2(target))
            diff = pygame.Vector2(target) - current
            if diff.length() > 1:
                current += diff * min(1.0, ANIMATION_SPEED * dt)
            self.visual_positions[key] = current
        self.goal_pulse += dt * 3.5

    def draw_board(self, surface, state):
        drawn = set()
        for node, neighbors in self.graph.adjacency_list.items():
            for neighbor in neighbors:
                edge = tuple(sorted([node, neighbor]))
                if edge in drawn:
                    continue
                p1, p2 = self.node_pixels[node], self.node_pixels[neighbor]
                pygame.draw.line(surface, COLOR_SHADOW, (p1.x, p1.y + 4), (p2.x, p2.y + 4), EDGE_WIDTH)
                pygame.draw.line(surface, COLOR_EDGE, p1, p2, EDGE_WIDTH)
                drawn.add(edge)

        pulse = 1.0 + 0.08 * math.sin(self.goal_pulse)
        for node, pos in self.node_pixels.items():
            surface.blit(self.images["node"], self.images["node"].get_rect(center=pos))
            
            node_txt = self.node_font.render(node, True, (80, 95, 115))
            surface.blit(node_txt, node_txt.get_rect(center=pos))
            
            if node == state.goal_node:
                size = int(NODE_RADIUS * 2 * pulse)
                img = pygame.transform.smoothscale(self.images["goal"], (size, size))
                surface.blit(img, img.get_rect(center=pos))

        if state.mode == MODE_MULTI:
            player2_visual = self.visual_positions.get("player2", self.node_pixels[state.player2_pos])
            surface.blit(self.images["player2"], self.images["player2"].get_rect(center=player2_visual))
        else:
            for i, pos in enumerate(state.computer_positions):
                key = f"enemy_{i}"
                visual = self.visual_positions.get(key, self.node_pixels[pos])
                surface.blit(self.images["computer"], self.images["computer"].get_rect(center=visual))

        player_visual = self.visual_positions.get("player", self.node_pixels[state.player_pos])
        surface.blit(self.images["player"], self.images["player"].get_rect(center=player_visual))

        if not state.winner:
            turn_pulse_radius = NODE_RADIUS + 8 + math.sin(self.goal_pulse * 1.5) * 4
            if state.turn in ("PLAYER", "PLAYER1"):
                pos = self.visual_positions.get("player", self.node_pixels[state.player_pos])
                pygame.draw.circle(surface, COLOR_GOLD, pos, int(turn_pulse_radius), 3)
            elif state.turn == "PLAYER2":
                pos = self.visual_positions.get("player2", self.node_pixels[state.player2_pos])
                pygame.draw.circle(surface, COLOR_GOLD, pos, int(turn_pulse_radius), 3)
            elif state.turn == "COMPUTER":
                for i, c_pos in enumerate(state.computer_positions):
                    pos = self.visual_positions.get(f"enemy_{i}", self.node_pixels[c_pos])
                    pygame.draw.circle(surface, COLOR_GOLD, pos, int(turn_pulse_radius), 3)

    def get_clicked_node(self, pos):
        for node, node_pos in self.node_pixels.items():
            if (pygame.Vector2(node_pos) - pygame.Vector2(pos)).length() <= NODE_RADIUS:
                return node
        return None