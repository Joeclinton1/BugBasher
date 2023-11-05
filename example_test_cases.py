# Importing the unittest module
import unittest
from example_code import Graph

# Defining the test cases for the Graph class
class GraphTest(unittest.TestCase):

    def test_node_addition(self):
        graph = Graph()
        graph.add_node("A")
        self.assertIn("A", graph.adjacency_list)

    def test_edge_addition(self):
        graph = Graph()
        graph.add_edge("A", "B", 5)
        self.assertIn("A", graph.adjacency_list)
        self.assertIn("B", graph.adjacency_list)
        self.assertIn(("B", 5), graph.adjacency_list["A"])

    def test_node_removal(self):
        graph = Graph()
        graph.add_node("A")
        graph.remove_node("A")
        self.assertNotIn("A", graph.adjacency_list)

    def test_edge_removal(self):
        graph = Graph()
        graph.add_edge("A", "B", 5)
        graph.remove_edge("A", "B")
        self.assertNotIn(("B", 5), graph.adjacency_list["A"])

    # def test_display(self):
    #     graph = Graph()
    #     graph.add_edge("A", "B", 1)
    #     try:
    #         graph.display()  # Display does not return anything, just prints to the console
    #     except Exception as e:
    #         self.fail(f"Display method failed with exception {e}")

if __name__ == '__main__':
    unittest.main()