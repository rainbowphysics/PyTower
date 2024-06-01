# https://www.geeksforgeeks.org/python-program-for-topological-sorting/
# https://kannappanchidambaram.medium.com/unlocking-topological-sorting-in-python-a-quick-guide-bf939e30e24d

from collections import defaultdict, deque
from typing import Generic, TypeVar

T = TypeVar('T')

#Class to represent a graph
class DAG:
    def __init__(self,vertices: int):
        self.graph = defaultdict[int, list[int]](list[int]) #dictionary containing adjacency List
        self.V = vertices #No. of vertices

    # function to add an edge to graph
    def add_edge(self,u: int,v: int):
        self.graph[u].append(v)

    # A recursive function used by topologicalSort
    def topological_sort_util(self,v: int,visited: list[bool],stack: list[int]):

        # Mark the current node as visited.
        visited[v] = True

        # Recur for all the vertices adjacent to this vertex
        for i in self.graph[v]:
            if visited[i] == False:
                self.topological_sort_util(i,visited,stack)

        # Push current vertex to stack which stores result
        stack.insert(0,v)

    # The function to do Topological Sort. It uses recursive
    # topologicalSortUtil()
    def topological_sort(self):
        # Mark all the vertices as not visited
        visited = [False]*self.V
        stack = list[int]()

        # Call the recursive helper function to store Topological
        # Sort starting from all vertices one by one
        for i in range(self.V):
            if visited[i] == False:
                self.topological_sort_util(i,visited,stack)

        # Print contents of stack
        return stack