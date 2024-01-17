class Graph:
    def __init__(self):
        self.adjacency_list = {}

    def add_node(self, node):
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []

    def add_edge(self, src, dest, weight=1):
        if src not in self.adjacency_list:
            self.add_node(src)
        if dest not in self.adjacency_list:
            self.add_node(dest)
        self.adjacency_list[src].append((dest, weight))

    def remove_edge(self, src, dest):
        self.adjacency_list[src] = [(n, w) for n, w in self.adjacency_list[src] if n != dest]

    def remove_node(self, node):
        if node in self.adjacency_list:
            del self.adjacency_list[node]
            for src in self.adjacency_list:
                self.adjacency_list[src] = [(n, w) for n, w in self.adjacency_list[src] if n != node]
