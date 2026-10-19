import random

class Graph:
    def __init__(self, rows=3, cols=3, extra_edges=0.2, seed=None):
        self.rows = rows
        self.cols = cols
        self.adjacency_list = {}
        self.positions = {}
        if seed is not None:
            random.seed(seed)
        self._generate(extra_edges)

    def _node_id(self, r, c):
        idx = r * self.cols + c
        if idx < 26:
            return chr(ord('A') + idx)
        return f"N{idx}"

    def _add_edge(self, n1, n2):
        if n2 not in self.adjacency_list[n1]:
            self.adjacency_list[n1].append(n2)
        if n1 not in self.adjacency_list[n2]:
            self.adjacency_list[n2].append(n1)

    def _generate(self, extra_edges):
        for r in range(self.rows):
            for c in range(self.cols):
                nid = self._node_id(r, c)
                self.adjacency_list[nid] = []
                self.positions[nid] = (r, c)

        for r in range(self.rows):
            for c in range(self.cols):
                nid = self._node_id(r, c)
                if c + 1 < self.cols:
                    self._add_edge(nid, self._node_id(r, c + 1))
                if r + 1 < self.rows:
                    self._add_edge(nid, self._node_id(r + 1, c))

        attempts = int(self.rows * self.cols * extra_edges * 2)
        for _ in range(attempts):
            r1 = random.randint(0, self.rows - 1)
            c1 = random.randint(0, self.cols - 1)
            r2 = random.randint(0, self.rows - 1)
            c2 = random.randint(0, self.cols - 1)
            if (r1, c1) == (r2, c2):
                continue
            if abs(r1 - r2) + abs(c1 - c2) == 2:
                n1 = self._node_id(r1, c1)
                n2 = self._node_id(r2, c2)
                if n2 not in self.adjacency_list[n1]:
                    self._add_edge(n1, n2)

    def get_neighbors(self, node):
        return self.adjacency_list.get(node, [])

    def all_nodes(self):
        return list(self.adjacency_list.keys())
