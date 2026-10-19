import random
import time
from config import BASE_SCORE, SCORE_PER_MOVE, SCORE_PER_SECOND, MODE_SINGLE, MODE_MULTI
from logic.bfs import find_shortest_path, bfs_distance

class GameState:
    def __init__(self, graph, num_enemies=1, mode=MODE_SINGLE, p1_name="Jugador 1", p2_name="Jugador 2", custom_config=None):
        self.graph = graph
        self.num_enemies = num_enemies
        self.mode = mode
        self.p1_name = p1_name
        self.p2_name = p2_name
        self.custom_config = custom_config
        self.reset()

    def reset(self):
        nodes = self.graph.all_nodes()
        self.goal_node = None
        self.computer_positions = []
        self.player2_pos = None
        self.winner = None
        self.moves = 0
        self.start_time = None
        self.elapsed_time = 0.0
        self.score = BASE_SCORE

        if self.custom_config:
            self.player_pos = self.custom_config["player"]
            self.computer_positions = list(self.custom_config["enemies"])
            self.goal_node = self.custom_config["goal"]
            self.turn = "PLAYER"
            self.message = "Tu turno"
            return

        self.player_pos = nodes[0]

        if self.mode == MODE_SINGLE:
            self.turn = "PLAYER"
            self.message = "Tu turno"
            self._setup_single_player(nodes)
        else:
            self.turn = "PLAYER1"
            self.message = f"Turno de {self.p1_name}"
            self._setup_multiplayer(nodes)

    def _setup_single_player(self, nodes):
        if self.num_enemies == 1:
            enemy_node = nodes[-1]
            if enemy_node == self.player_pos and len(nodes) > 1:
                enemy_node = nodes[-2]
            self.computer_positions = [enemy_node]
            candidates = [n for n in nodes if n != self.player_pos and n not in self.computer_positions]
            safe_candidates = [n for n in candidates
                               if bfs_distance(self.graph, self.player_pos, n) >= 2
                               and bfs_distance(self.graph, enemy_node, n) >= 2]
            if safe_candidates:
                self.goal_node = random.choice(safe_candidates)
            elif candidates:
                self.goal_node = random.choice(candidates)
            else:
                self.goal_node = nodes[-1]
            return

        max_attempts = 200
        for _ in range(max_attempts):
            candidates = [n for n in nodes if n != self.player_pos and bfs_distance(self.graph, self.player_pos, n) >= 2]
            if len(candidates) < self.num_enemies:
                candidates = [n for n in nodes if n != self.player_pos]
            enemies = random.sample(candidates, min(self.num_enemies, len(candidates)))

            goal_candidates = [n for n in nodes if n != self.player_pos and n not in enemies and bfs_distance(self.graph, self.player_pos, n) >= 2]
            if not goal_candidates:
                goal_candidates = [n for n in nodes if n != self.player_pos and n not in enemies]
            if not goal_candidates:
                continue
            goal = random.choice(goal_candidates)

            safe_move_exists = False
            for neighbor in self.graph.get_neighbors(self.player_pos):
                if neighbor in enemies:
                    continue
                if all(bfs_distance(self.graph, neighbor, e) >= 2 for e in enemies):
                    safe_move_exists = True
                    break
            if safe_move_exists:
                self.computer_positions = enemies
                self.goal_node = goal
                break
        else:
            enemies = random.sample([n for n in nodes if n != self.player_pos], min(self.num_enemies, len(nodes)-1))
            self.computer_positions = enemies
            goal_candidates = [n for n in nodes if n != self.player_pos and n not in enemies]
            self.goal_node = random.choice(goal_candidates) if goal_candidates else nodes[-1]

    def _setup_multiplayer(self, nodes):
        self.player2_pos = nodes[-1]
        candidates = [n for n in nodes if n not in (self.player_pos, self.player2_pos) and bfs_distance(self.graph, self.player_pos, n) >= 2 and bfs_distance(self.graph, self.player2_pos, n) >= 2]
        if not candidates:
            candidates = [n for n in nodes if n not in (self.player_pos, self.player2_pos)]
        self.goal_node = random.choice(candidates) if candidates else nodes[len(nodes)//2]

    def get_neighbor_in_direction(self, dr, dc, pos):
        if pos not in self.graph.positions:
            return None
        
        current_r, current_c = self.graph.positions[pos]
        best_neighbor = None
        min_dist = float('inf')
        
        for neighbor in self.graph.get_neighbors(pos):
            nr, nc = self.graph.positions[neighbor]
            
            valid_r = (dr == 0) or (dr == -1 and nr < current_r) or (dr == 1 and nr > current_r)
            valid_c = (dc == 0) or (dc == -1 and nc < current_c) or (dc == 1 and nc > current_c)
            
            if valid_r and valid_c:
                dist = abs(nr - (current_r + dr)) + abs(nc - (current_c + dc))
                if dist < min_dist:
                    min_dist = dist
                    best_neighbor = neighbor
                    
        return best_neighbor

    def _start_timer_if_needed(self):
        if self.start_time is None and self.winner is None:
            self.start_time = time.time()

    def update_time(self):
        if self.start_time is not None and self.winner is None:
            self.elapsed_time = time.time() - self.start_time

    def get_current_score(self):
        if self.winner in ("PLAYER", "PLAYER1"):
            return self.score
        if self.winner in ("COMPUTER", "PLAYER2"):
            return 0
        time_penalty = int(self.elapsed_time * SCORE_PER_SECOND)
        move_penalty = self.moves * SCORE_PER_MOVE
        return max(0, BASE_SCORE - time_penalty - move_penalty)

    def move_player(self, target_node):
        if self.winner:
            return False

        if self.mode == MODE_SINGLE:
            if self.turn != "PLAYER" or target_node not in self.graph.get_neighbors(self.player_pos):
                return False
            self._start_timer_if_needed()
            self.player_pos = target_node
            self.moves += 1
            self.update_time()
            if self.check_win_conditions():
                return True
            self.turn = "COMPUTER"
            self.message = "Enemigos pensando..."
            return True
        else:
            if self.turn == "PLAYER1":
                if target_node not in self.graph.get_neighbors(self.player_pos):
                    return False
                self._start_timer_if_needed()
                self.player_pos = target_node
            elif self.turn == "PLAYER2":
                if target_node not in self.graph.get_neighbors(self.player2_pos):
                    return False
                self._start_timer_if_needed()
                self.player2_pos = target_node
            else:
                return False

            self.moves += 1
            self.update_time()
            if self.check_win_conditions():
                return True
            self.turn = "PLAYER2" if self.turn == "PLAYER1" else "PLAYER1"
            self.message = f"Turno de {self.p2_name if self.turn == 'PLAYER2' else self.p1_name}"
            return True

    def move_computers(self):
        if self.turn != "COMPUTER" or self.winner:
            return False
        occupied = set(self.computer_positions)
        new_positions = []
        for pos in self.computer_positions:
            occupied.discard(pos)
            path = find_shortest_path(self.graph, pos, self.player_pos)
            if len(path) > 1:
                next_node = path[1]
                if next_node == self.player_pos:
                    new_positions.append(next_node)
                    occupied.add(next_node)
                elif next_node not in occupied:
                    new_positions.append(next_node)
                    occupied.add(next_node)
                else:
                    new_positions.append(pos)
                    occupied.add(pos)
            else:
                new_positions.append(pos)
                occupied.add(pos)
        self.computer_positions = new_positions
        self.update_time()
        if self.check_win_conditions():
            self.turn = "PLAYER"
            return True
        self.turn = "PLAYER"
        self.message = "Tu turno"
        return True

    def check_win_conditions(self):
        if self.mode == MODE_SINGLE:
            if self.player_pos in self.computer_positions:
                self.winner = "COMPUTER"
                self.message = "¡Has sido atrapado!"
                self.score = 0
                return True
            if self.player_pos == self.goal_node:
                self.winner = "PLAYER"
                self.message = "¡Has llegado a la meta!"
                self.score = self.get_current_score()
                return True
        else:
            if self.player2_pos == self.player_pos:
                self.winner = "PLAYER2"
                self.message = f"¡{self.p2_name} ha atrapado a {self.p1_name}!"
                return True
            if self.player_pos == self.goal_node:
                self.winner = "PLAYER1"
                self.message = f"¡{self.p1_name} llegó a la meta!"
                self.score = self.get_current_score()
                return True
        return False

    def get_stats(self):
        return {
            "tiempo": self.elapsed_time,
            "movimientos": self.moves,
            "puntos": self.score if self.winner in ("PLAYER", "PLAYER1") else 0,
            "ganador": self.winner,
            "mode": self.mode,
            "p1_name": self.p1_name,
            "p2_name": self.p2_name
        }