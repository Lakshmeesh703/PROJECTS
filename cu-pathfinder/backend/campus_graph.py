"""
CU PathFinder - Campus Graph Implementation
===========================================

This module implements the weighted graph representation of Chanakya University campus.
It includes all campus buildings, their coordinates, and walking distances.

Author: AI Assistant
Date: September 19, 2025
"""

import math
from typing import Dict, List, Tuple, Optional
import numpy as np

class CampusGraph:
    """
    Represents Chanakya University campus as a weighted graph.
    
    Attributes:
        nodes: Dictionary mapping node names to their properties
        edges: Dictionary representing the adjacency list with weights
        coordinates: Dictionary mapping node names to (x, y) coordinates
        building_info: Dictionary containing building operational information
    """
    
    def __init__(self):
        """Initialize the campus graph with all buildings and connections."""
        self.nodes = {}
        self.edges = {}
        self.coordinates = {}
        self.building_info = {}
        self._initialize_campus()
    
    def _initialize_campus(self):
        """Initialize campus with all buildings, coordinates, and connections."""
        # Initialize coordinates (based on 824×1741 image)
        self.coordinates = {
            'Entry Gate': (296, 1724),
            'Main Gate': (379, 1458),
            'Security Office': (296, 1473),
            'Flag Post': (327, 1431),
            'Library': (388, 1393),
            'Block A': (353, 1384),
            'Block B': (349, 1223),
            'Auditorium': (353, 1384),  
            'Food Court': (445, 829),
            'Gym': (445, 829),  
            'Badminton Court': (445, 829), 
            'Boys Hostel': (737, 820),
            'Girls Hostel': (807, 746),
            'Mart': (785, 779),
            'Cricket Ground': (157, 131),
            'Football Ground': (78, 371),
            'Volleyball Court': (567, 58),
            'Basketball Court': (371, 76),
            'Tennis Court': (567, 58),  
            'Guest House': (126, 1263),
            'Pottery Making Area': (22, 1348),
            'Faculty Apartment': (514, 1121),
            'DG Yard': (680, 1229),
            'Water Treatment Area': (534, 822),
            'Exit Gate': (453, 1729),
            'Playing Ground': (83, 1602),
            'Medical Center': (445, 900),  
            'Admin Office': (379, 1458),  
            'Student Center': (353, 1300),  
            'Canteen': (438, 1343)  
        }
        
        # Initialize building information
        self.building_info = {
            'Entry Gate': {'type': 'entrance', 'hours': '24/7', 'description': 'Main campus entry point'},
            'Main Gate': {'type': 'entrance', 'hours': '24/7', 'description': 'Primary campus gate with security'},
            'Security Office': {'type': 'security', 'hours': '24/7', 'description': 'Campus security headquarters'},
            'Flag Post': {'type': 'landmark', 'hours': '24/7', 'description': 'Central campus landmark'},
            'Library': {'type': 'academic', 'hours': '8:00 AM - 10:00 PM', 'description': 'Central library with study halls'},
            'Block A': {'type': 'academic', 'hours': '8:00 AM - 8:00 PM', 'description': 'Main academic building'},
            'Block B': {'type': 'academic', 'hours': '8:00 AM - 8:00 PM', 'description': 'Secondary academic building'},
            'Auditorium': {'type': 'academic', 'hours': '8:00 AM - 10:00 PM', 'description': 'Main auditorium for events'},
            'Food Court': {'type': 'dining', 'hours': '7:00 AM - 11:00 PM', 'description': 'Central food court'},
            'Gym': {'type': 'sports', 'hours': '6:00 AM - 10:00 PM', 'description': 'Fitness center and gymnasium'},
            'Badminton Court': {'type': 'sports', 'hours': '6:00 AM - 10:00 PM', 'description': 'Indoor badminton facilities'},
            'Boys Hostel': {'type': 'residential', 'hours': '24/7', 'description': 'Male student accommodation'},
            'Girls Hostel': {'type': 'residential', 'hours': '24/7', 'description': 'Female student accommodation'},
            'Mart': {'type': 'retail', 'hours': '8:00 AM - 10:00 PM', 'description': 'Campus convenience store'},
            'Cricket Ground': {'type': 'sports', 'hours': '6:00 AM - 8:00 PM', 'description': 'Full-size cricket ground'},
            'Football Ground': {'type': 'sports', 'hours': '6:00 AM - 8:00 PM', 'description': 'Football field'},
            'Volleyball Court': {'type': 'sports', 'hours': '6:00 AM - 8:00 PM', 'description': 'Volleyball court'},
            'Basketball Court': {'type': 'sports', 'hours': '6:00 AM - 8:00 PM', 'description': 'Basketball court'},
            'Tennis Court': {'type': 'sports', 'hours': '6:00 AM - 8:00 PM', 'description': 'Tennis facilities'},
            'Guest House': {'type': 'accommodation', 'hours': '24/7', 'description': 'Visitor accommodation'},
            'Pottery Making Area': {'type': 'workshop', 'hours': '9:00 AM - 5:00 PM', 'description': 'Art and pottery workshop'},
            'Faculty Apartment': {'type': 'residential', 'hours': '24/7', 'description': 'Faculty housing complex'},
            'DG Yard': {'type': 'utility', 'hours': '24/7', 'description': 'Power generation facility'},
            'Water Treatment Area': {'type': 'utility', 'hours': '24/7', 'description': 'Water treatment plant'},
            'Exit Gate': {'type': 'entrance', 'hours': '24/7', 'description': 'Alternative campus exit'},
            'Playing Ground': {'type': 'recreation', 'hours': '6:00 AM - 8:00 PM', 'description': 'General sports area'},
            'Medical Center': {'type': 'medical', 'hours': '8:00 AM - 8:00 PM', 'description': 'Campus health center'},
            'Admin Office': {'type': 'administrative', 'hours': '9:00 AM - 5:00 PM', 'description': 'Administration office'},
            'Student Center': {'type': 'student services', 'hours': '8:00 AM - 8:00 PM', 'description': 'Student activities center'},
            'Canteen': {'type': 'dining', 'hours': '7:00 AM - 10:00 PM', 'description': 'Student canteen'}
        }
        
        # Initialize nodes
        for node_name in self.coordinates.keys():
            self.nodes[node_name] = {
                'coordinates': self.coordinates[node_name],
                'info': self.building_info.get(node_name, {})
            }
            self.edges[node_name] = {}
        
        # Add connections based on provided measurements
        self._add_campus_connections()
    
    def _add_campus_connections(self):
        """Add all campus connections with measured distances."""
        # Based on provided measurements (in meters)
        connections = [
            ('Entry Gate', 'Security Office', 180),
            ('Security Office', 'Main Gate', 70),  # From security to main gate
            ('Main Gate', 'Flag Post', 70),
            ('Main Gate', 'Block A', 80),
            ('Main Gate', 'Auditorium', 80),
            ('Main Gate', 'Library', 80),
            ('Library', 'Canteen', 50),
            ('Block A', 'Block B', 120),
            ('Block B', 'Food Court', 230),
            ('Food Court', 'Gym', 35),
            ('Food Court', 'Badminton Court', 45),
            ('Food Court', 'Boys Hostel', 260),
            ('Food Court', 'Girls Hostel', 345),
            ('Boys Hostel', 'Mart', 70),
            ('Mart', 'Girls Hostel', 70),
            ('Boys Hostel', 'Cricket Ground', 560),
            ('Cricket Ground', 'Football Ground', 100),
            ('Cricket Ground', 'Volleyball Court', 80),
            ('Cricket Ground', 'Basketball Court', 80),
            ('Cricket Ground', 'Tennis Court', 80),
            ('Block A', 'Guest House', 250),
            ('Block A', 'Pottery Making Area', 230),
            ('Block B', 'Guest House', 330),
            ('Block B', 'Faculty Apartment', 165),
            ('Block A', 'DG Yard', 350),
            ('Block A', 'Water Treatment Area', 503),
            ('Block A', 'Boys Hostel', 600),
            ('Main Gate', 'Exit Gate', 140),
            
            # Additional logical connections for better connectivity
            ('Block A', 'Student Center', 120),
            ('Block B', 'Student Center', 100),
            ('Student Center', 'Library', 90),
            ('Food Court', 'Medical Center', 75),
            ('Medical Center', 'Water Treatment Area', 80),
            ('Admin Office', 'Main Gate', 50),
            ('Playing Ground', 'Guest House', 150),
            ('Entry Gate', 'Playing Ground', 200),
            
            # Sports area interconnections
            ('Volleyball Court', 'Basketball Court', 50),
            ('Volleyball Court', 'Tennis Court', 20),
            ('Basketball Court', 'Tennis Court', 40),
            
            # Hostel area connections
            ('Boys Hostel', 'Girls Hostel', 120),
            ('Girls Hostel', 'Mart', 50),
            
            # Utility connections
            ('DG Yard', 'Water Treatment Area', 200),
            ('Water Treatment Area', 'Food Court', 100)
        ]
        
        # Add bidirectional edges
        for node1, node2, distance in connections:
            if node1 in self.nodes and node2 in self.nodes:
                self.edges[node1][node2] = distance
                self.edges[node2][node1] = distance
    
    def get_neighbors(self, node: str) -> Dict[str, int]:
        """
        Get all neighbors of a node with their distances.
        
        Args:
            node: Node name
            
        Returns:
            Dictionary of neighbor names and distances
        """
        return self.edges.get(node, {})
    
    def get_distance(self, node1: str, node2: str) -> Optional[int]:
        """
        Get distance between two directly connected nodes.
        
        Args:
            node1: First node name
            node2: Second node name
            
        Returns:
            Distance in meters if connected, None otherwise
        """
        return self.edges.get(node1, {}).get(node2)
    
    def euclidean_distance(self, node1: str, node2: str) -> float:
        """
        Calculate Euclidean distance between two nodes (for heuristic).
        
        Args:
            node1: First node name
            node2: Second node name
            
        Returns:
            Euclidean distance in coordinate units
        """
        if node1 not in self.coordinates or node2 not in self.coordinates:
            return float('inf')
        
        x1, y1 = self.coordinates[node1]
        x2, y2 = self.coordinates[node2]
        
        # Convert pixel coordinates to approximate meters
        # Assuming the image represents approximately 1000m x 2000m campus
        scale_x = 1000 / 824  # meters per pixel
        scale_y = 2000 / 1741  # meters per pixel
        
        dx = (x2 - x1) * scale_x
        dy = (y2 - y1) * scale_y
        
        return math.sqrt(dx * dx + dy * dy)
    
    def get_all_nodes(self) -> List[str]:
        """Get list of all node names."""
        return list(self.nodes.keys())
    
    def is_valid_node(self, node: str) -> bool:
        """Check if node exists in the graph."""
        return node in self.nodes
    
    def get_node_info(self, node: str) -> Dict:
        """Get detailed information about a node."""
        return self.nodes.get(node, {})
    
    def get_building_hours(self, node: str) -> str:
        """Get operating hours for a building."""
        info = self.building_info.get(node, {})
        return info.get('hours', 'Unknown')
    
    def get_building_type(self, node: str) -> str:
        """Get building type/category."""
        info = self.building_info.get(node, {})
        return info.get('type', 'Unknown')
    
    def get_building_description(self, node: str) -> str:
        """Get building description."""
        info = self.building_info.get(node, {})
        return info.get('description', 'No description available')
    
    def print_graph_stats(self):
        """Print graph statistics."""
        print(f"Campus Graph Statistics:")
        print(f"- Total nodes: {len(self.nodes)}")
        print(f"- Total edges: {sum(len(neighbors) for neighbors in self.edges.values()) // 2}")
        print(f"- Building types: {len(set(info.get('type', 'Unknown') for info in self.building_info.values()))}")
        
        # Count by type
        type_counts = {}
        for info in self.building_info.values():
            building_type = info.get('type', 'Unknown')
            type_counts[building_type] = type_counts.get(building_type, 0) + 1
        
        print("\nBuilding distribution:")
        for building_type, count in sorted(type_counts.items()):
            print(f"  - {building_type}: {count}")
    
    def get_path_distance(self, path: List[str]) -> int:
        """
        Calculate total distance for a given path.
        
        Args:
            path: List of node names representing the path
            
        Returns:
            Total distance in meters
        """
        if len(path) < 2:
            return 0
        
        total_distance = 0
        for i in range(len(path) - 1):
            distance = self.get_distance(path[i], path[i + 1])
            if distance is None:
                return float('inf')  # Invalid path
            total_distance += distance
        
        return total_distance
    
    def estimate_walking_time(self, distance_meters: int, walking_speed_mps: float = 1.4) -> int:
        """
        Estimate walking time for a given distance.
        
        Args:
            distance_meters: Distance in meters
            walking_speed_mps: Walking speed in meters per second (default: 1.4 m/s = 5 km/h)
            
        Returns:
            Estimated time in seconds
        """
        return int(distance_meters / walking_speed_mps)

# Example usage and testing
if __name__ == "__main__":
    # Create campus graph
    campus = CampusGraph()
    
    # Print statistics
    campus.print_graph_stats()
    
    # Test some connections
    print(f"\nSample connections:")
    print(f"Main Gate to Library: {campus.get_distance('Main Gate', 'Library')}m")
    print(f"Boys Hostel to Girls Hostel: {campus.get_distance('Boys Hostel', 'Girls Hostel')}m")
    print(f"Food Court to Cricket Ground: {campus.get_distance('Food Court', 'Cricket Ground')}m")
    
    # Test heuristic
    print(f"\nEuclidean distances (heuristic):")
    print(f"Main Gate to Cricket Ground: {campus.euclidean_distance('Main Gate', 'Cricket Ground'):.1f}m")
    print(f"Library to Boys Hostel: {campus.euclidean_distance('Library', 'Boys Hostel'):.1f}m")
    
    # Test building info
    print(f"\nBuilding information:")
    print(f"Library hours: {campus.get_building_hours('Library')}")
    print(f"Food Court type: {campus.get_building_type('Food Court')}")
    print(f"Cricket Ground description: {campus.get_building_description('Cricket Ground')}")