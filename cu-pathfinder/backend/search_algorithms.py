"""
CU PathFinder - Search Algorithms Implementation
===============================================

This module implements BFS, DFS, UCS, and A* search algorithms with detailed tracing.
Each algorithm returns the path, cost, and exploration trace for analysis.

Author: AI Assistant
Date: September 19, 2025
"""

import heapq
from collections import deque
from typing import List, Tuple, Dict, Optional, Set
from campus_graph import CampusGraph

class SearchResult:
    """Container for search algorithm results."""
    
    def __init__(self, path: List[str], cost: int, nodes_explored: List[str], 
                 exploration_order: List[str], algorithm: str, success: bool = True):
        self.path = path
        self.cost = cost
        self.nodes_explored = nodes_explored
        self.exploration_order = exploration_order
        self.algorithm = algorithm
        self.success = success
        self.num_nodes_explored = len(set(nodes_explored))
    
    def __str__(self):
        if not self.success:
            return f"{self.algorithm}: No path found"
        
        path_str = " → ".join(self.path)
        return (f"{self.algorithm} Results:\n"
                f"Path: {path_str}\n"
                f"Total Distance: {self.cost}m\n"
                f"Nodes Explored: {self.num_nodes_explored}\n"
                f"Exploration Order: {' → '.join(self.exploration_order[:10])}..."
                f"{'...' if len(self.exploration_order) > 10 else ''}")

class SearchAlgorithms:
    """Implementation of various search algorithms for campus pathfinding."""
    
    def __init__(self, campus_graph: CampusGraph):
        """
        Initialize with campus graph.
        
        Args:
            campus_graph: CampusGraph instance
        """
        self.graph = campus_graph
        self.trace_enabled = True
    
    def breadth_first_search(self, start: str, goal: str) -> SearchResult:
        """
        Breadth-First Search implementation.
        
        Args:
            start: Starting node name
            goal: Goal node name
            
        Returns:
            SearchResult with path and exploration details
        """
        if not self.graph.is_valid_node(start) or not self.graph.is_valid_node(goal):
            return SearchResult([], 0, [], [], "BFS", False)
        
        if start == goal:
            return SearchResult([start], 0, [start], [start], "BFS")
        
        # Initialize BFS data structures
        queue = deque([(start, [start], 0)])  # (node, path, cost)
        visited = set()
        exploration_order = []
        nodes_explored = []
        
        while queue:
            current_node, path, cost = queue.popleft()
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            exploration_order.append(current_node)
            nodes_explored.append(current_node)
            
            if self.trace_enabled:
                print(f"BFS: Exploring {current_node}, Queue size: {len(queue)}")
            
            if current_node == goal:
                total_cost = self.graph.get_path_distance(path)
                return SearchResult(path, total_cost, nodes_explored, 
                                  exploration_order, "BFS")
            
            # Add neighbors to queue
            for neighbor, edge_cost in self.graph.get_neighbors(current_node).items():
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    new_cost = cost + edge_cost
                    queue.append((neighbor, new_path, new_cost))
        
        return SearchResult([], 0, nodes_explored, exploration_order, "BFS", False)
    
    def depth_first_search(self, start: str, goal: str) -> SearchResult:
        """
        Depth-First Search implementation.
        
        Args:
            start: Starting node name
            goal: Goal node name
            
        Returns:
            SearchResult with path and exploration details
        """
        if not self.graph.is_valid_node(start) or not self.graph.is_valid_node(goal):
            return SearchResult([], 0, [], [], "DFS", False)
        
        if start == goal:
            return SearchResult([start], 0, [start], [start], "DFS")
        
        # Initialize DFS data structures
        stack = [(start, [start], 0)]  # (node, path, cost)
        visited = set()
        exploration_order = []
        nodes_explored = []
        
        while stack:
            current_node, path, cost = stack.pop()
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            exploration_order.append(current_node)
            nodes_explored.append(current_node)
            
            if self.trace_enabled:
                print(f"DFS: Exploring {current_node}, Stack size: {len(stack)}")
            
            if current_node == goal:
                total_cost = self.graph.get_path_distance(path)
                return SearchResult(path, total_cost, nodes_explored, 
                                  exploration_order, "DFS")
            
            # Add neighbors to stack (reverse order for consistent exploration)
            neighbors = list(self.graph.get_neighbors(current_node).items())
            neighbors.reverse()  # For consistent ordering
            
            for neighbor, edge_cost in neighbors:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    new_cost = cost + edge_cost
                    stack.append((neighbor, new_path, new_cost))
        
        return SearchResult([], 0, nodes_explored, exploration_order, "DFS", False)
    
    def uniform_cost_search(self, start: str, goal: str) -> SearchResult:
        """
        Uniform Cost Search (Dijkstra's) implementation.
        
        Args:
            start: Starting node name
            goal: Goal node name
            
        Returns:
            SearchResult with optimal path and exploration details
        """
        if not self.graph.is_valid_node(start) or not self.graph.is_valid_node(goal):
            return SearchResult([], 0, [], [], "UCS", False)
        
        if start == goal:
            return SearchResult([start], 0, [start], [start], "UCS")
        
        # Initialize UCS data structures
        priority_queue = [(0, start, [start])]  # (cost, node, path)
        visited = set()
        exploration_order = []
        nodes_explored = []
        
        while priority_queue:
            current_cost, current_node, path = heapq.heappop(priority_queue)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            exploration_order.append(current_node)
            nodes_explored.append(current_node)
            
            if self.trace_enabled:
                print(f"UCS: Exploring {current_node}, Cost: {current_cost}, "
                      f"Queue size: {len(priority_queue)}")
            
            if current_node == goal:
                return SearchResult(path, current_cost, nodes_explored, 
                                  exploration_order, "UCS")
            
            # Add neighbors to priority queue
            for neighbor, edge_cost in self.graph.get_neighbors(current_node).items():
                if neighbor not in visited:
                    new_cost = current_cost + edge_cost
                    new_path = path + [neighbor]
                    heapq.heappush(priority_queue, (new_cost, neighbor, new_path))
        
        return SearchResult([], 0, nodes_explored, exploration_order, "UCS", False)
    
    def a_star_search(self, start: str, goal: str) -> SearchResult:
        """
        A* Search implementation with Euclidean distance heuristic.
        
        Args:
            start: Starting node name
            goal: Goal node name
            
        Returns:
            SearchResult with optimal path and exploration details
        """
        if not self.graph.is_valid_node(start) or not self.graph.is_valid_node(goal):
            return SearchResult([], 0, [], [], "A*", False)
        
        if start == goal:
            return SearchResult([start], 0, [start], [start], "A*")
        
        # Initialize A* data structures
        # (f_cost, g_cost, node, path)
        priority_queue = [(self.graph.euclidean_distance(start, goal), 0, start, [start])]
        visited = set()
        exploration_order = []
        nodes_explored = []
        g_costs = {start: 0}  # Track best g-cost to each node
        
        while priority_queue:
            f_cost, g_cost, current_node, path = heapq.heappop(priority_queue)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            exploration_order.append(current_node)
            nodes_explored.append(current_node)
            
            if self.trace_enabled:
                h_cost = f_cost - g_cost
                print(f"A*: Exploring {current_node}, g={g_cost}, h={h_cost:.1f}, "
                      f"f={f_cost:.1f}, Queue size: {len(priority_queue)}")
            
            if current_node == goal:
                return SearchResult(path, g_cost, nodes_explored, 
                                  exploration_order, "A*")
            
            # Add neighbors to priority queue
            for neighbor, edge_cost in self.graph.get_neighbors(current_node).items():
                if neighbor not in visited:
                    new_g_cost = g_cost + edge_cost
                    
                    # Skip if we've found a better path to this neighbor
                    if neighbor in g_costs and g_costs[neighbor] <= new_g_cost:
                        continue
                    
                    g_costs[neighbor] = new_g_cost
                    h_cost = self.graph.euclidean_distance(neighbor, goal)
                    f_cost = new_g_cost + h_cost
                    new_path = path + [neighbor]
                    
                    heapq.heappush(priority_queue, (f_cost, new_g_cost, neighbor, new_path))
        
        return SearchResult([], 0, nodes_explored, exploration_order, "A*", False)
    
    def compare_algorithms(self, start: str, goal: str) -> Dict[str, SearchResult]:
        """
        Compare all algorithms on the same search problem.
        
        Args:
            start: Starting node name
            goal: Goal node name
            
        Returns:
            Dictionary mapping algorithm names to SearchResult objects
        """
        print(f"\n=== Comparing Algorithms: {start} → {goal} ===")
        
        # Disable tracing for comparison
        original_trace = self.trace_enabled
        self.trace_enabled = False
        
        results = {}
        
        # Run all algorithms
        algorithms = [
            ("BFS", self.breadth_first_search),
            ("DFS", self.depth_first_search),
            ("UCS", self.uniform_cost_search),
            ("A*", self.a_star_search)
        ]
        
        for name, algorithm in algorithms:
            print(f"\nRunning {name}...")
            result = algorithm(start, goal)
            results[name] = result
            print(f"{name}: {'Success' if result.success else 'Failed'}")
            if result.success:
                print(f"  Path length: {len(result.path)} nodes")
                print(f"  Total distance: {result.cost}m")
                print(f"  Nodes explored: {result.num_nodes_explored}")
        
        # Restore tracing
        self.trace_enabled = original_trace
        
        return results
    
    def print_algorithm_trace(self, result: SearchResult):
        """
        Print detailed trace of algorithm execution.
        
        Args:
            result: SearchResult object
        """
        print(f"\n=== {result.algorithm} Algorithm Trace ===")
        print(f"Problem: Find path with total exploration")
        print(f"Success: {result.success}")
        
        if not result.success:
            print("No path found!")
            return
        
        print(f"\nExploration order:")
        for i, node in enumerate(result.exploration_order, 1):
            print(f"  {i:2d}. {node}")
        
        print(f"\nFinal path:")
        for i, node in enumerate(result.path):
            if i < len(result.path) - 1:
                distance = self.graph.get_distance(result.path[i], result.path[i+1])
                print(f"  {node} → ({distance}m)")
            else:
                print(f"  {node}")
        
        print(f"\nSummary:")
        print(f"  Total distance: {result.cost}m")
        print(f"  Nodes in path: {len(result.path)}")
        print(f"  Unique nodes explored: {result.num_nodes_explored}")
        print(f"  Walking time: ~{self.graph.estimate_walking_time(result.cost) // 60} minutes")
    
    def set_tracing(self, enabled: bool):
        """Enable or disable algorithm tracing."""
        self.trace_enabled = enabled


# Example usage and testing
if __name__ == "__main__":
    # Create campus graph and search algorithms
    campus = CampusGraph()
    search = SearchAlgorithms(campus)
    
    # Test cases
    test_cases = [
        ("Main Gate", "Library"),
        ("Boys Hostel", "Cricket Ground"),
        ("Food Court", "Girls Hostel")
    ]
    
    for start, goal in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {start} → {goal}")
        print(f"{'='*60}")
        
        # Test each algorithm individually with tracing
        search.set_tracing(True)
        
        print(f"\n--- BFS Trace ---")
        bfs_result = search.breadth_first_search(start, goal)
        search.print_algorithm_trace(bfs_result)
        
        print(f"\n--- A* Trace ---")
        astar_result = search.a_star_search(start, goal)
        search.print_algorithm_trace(astar_result)
        
        # Compare all algorithms
        comparison = search.compare_algorithms(start, goal)
        
        print(f"\n--- Algorithm Comparison ---")
        for alg_name, result in comparison.items():
            if result.success:
                print(f"{alg_name:4s}: {result.cost:4d}m, "
                      f"{result.num_nodes_explored:2d} nodes explored")
            else:
                print(f"{alg_name:4s}: No path found")
    
    print(f"\n{'='*60}")
    print("Testing completed!")
    print(f"{'='*60}")