class Graph:
    def __init__(self, directed=False):
        self.graph = {}
        self.directed = directed
    
    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = []
    
    def add_edge(self, src, dest):
        if src not in self.graph:
            self.add_vertex(src)
        if dest not in self.graph:
            self.add_vertex(dest)
        self.graph[src].append(dest)
        if not self.directed:
            self.graph[dest].append(src)
    
    def remove_edge(self, src, dest):
        if src in self.graph:
            if dest in self.graph[src]:
                self.graph[src].remove(dest)
        if not self.directed:
            if dest in self.graph and src in self.graph[dest]:
                self.graph[dest].remove(src)
    
    def remove_vertex(self, vertex):
        if vertex in self.graph:
            # Remove any edges from other vertices to this one
            for adj in list(self.graph):
                if vertex in self.graph[adj]:
                    self.graph[adj].remove(vertex)
            # Remove the vertex entry
            del self.graph[vertex]
    
    def get_adjacent_vertices(self, vertex):
        if vertex in self.graph:
            return self.graph[vertex]
        else:
            return []
    
    def __str__(self):
        return str(self.graph)

# Example usage:
g = Graph(directed=True)
g.add_vertex('A')
g.add_vertex('B')
g.add_edge('A', 'B')
g.add_edge('A', 'C')
print(g)