from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import heapq
import json
import os
import sys
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom paths storage
SAVED_PATHS = {}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Campus data structure - Chanakya University, Karnataka, India
CAMPUS_BUILDINGS = {
    "Main Gate": {"lat": 13.2215, "lng": 77.7545, "type": "entrance"},
    "Admin Office": {"lat": 13.2220, "lng": 77.7554, "type": "administrative"},
    "Auditorium": {"lat": 13.2218, "lng": 77.7550, "type": "academic"},
    "Engineering Block": {"lat": 13.2225, "lng": 77.7558, "type": "academic"},
    "Science Block": {"lat": 13.2224, "lng": 77.7550, "type": "academic"},
    "Library": {"lat": 13.2222, "lng": 77.7552, "type": "academic"},
    "Student Center": {"lat": 13.2216, "lng": 77.7548, "type": "student_services"},
    "Canteen": {"lat": 13.2217, "lng": 77.7546, "type": "dining"},
    "Food Court": {"lat": 13.2218, "lng": 77.7548, "type": "dining"},
    "Sports Complex": {"lat": 13.2212, "lng": 77.7560, "type": "sports"},
    "Basketball Court": {"lat": 13.2213, "lng": 77.7562, "type": "sports"},
    "Badminton Court": {"lat": 13.2213, "lng": 77.7559, "type": "sports"},
    "Cricket Ground": {"lat": 13.2210, "lng": 77.7568, "type": "sports"},
    "Football Ground": {"lat": 13.2209, "lng": 77.7570, "type": "sports"},
    "Boys Hostel": {"lat": 13.2208, "lng": 77.7565, "type": "residential"},
    "Girls Hostel": {"lat": 13.2207, "lng": 77.7542, "type": "residential"},
    "Faculty Quarters": {"lat": 13.2228, "lng": 77.7545, "type": "residential"},
    "Central Plaza": {"lat": 13.2220, "lng": 77.7552, "type": "landmark"},
    "Parking Area": {"lat": 13.2216, "lng": 77.7542, "type": "utility"},
    "Security Office": {"lat": 13.2215, "lng": 77.7544, "type": "administrative"},
    "Computer Center": {"lat": 13.2223, "lng": 77.7556, "type": "technology"},
    "Medical Center": {"lat": 13.2219, "lng": 77.7543, "type": "health"},
    "Bookstore": {"lat": 13.2217, "lng": 77.7549, "type": "services"},
    "ATM Center": {"lat": 13.2218, "lng": 77.7547, "type": "services"},
    "Gymnasium": {"lat": 13.2211, "lng": 77.7561, "type": "sports"},
    "Tennis Court": {"lat": 13.2214, "lng": 77.7563, "type": "sports"},
    "Volleyball Court": {"lat": 13.2212, "lng": 77.7559, "type": "sports"},
    "Guest House": {"lat": 13.2226, "lng": 77.7547, "type": "accommodation"}
}

# Campus connections (edges for graph) - Chanakya University layout
CAMPUS_CONNECTIONS = [
    # Main academic connections
    ("Main Gate", "Admin Office", 0.15),
    ("Main Gate", "Security Office", 0.05),
    ("Main Gate", "Parking Area", 0.08),
    ("Admin Office", "Library", 0.10),
    ("Admin Office", "Auditorium", 0.08),
    ("Admin Office", "Central Plaza", 0.06),
    ("Library", "Engineering Block", 0.12),
    ("Library", "Science Block", 0.10),
    ("Library", "Central Plaza", 0.08),
    # Student and academic facilities
    ("Engineering Block", "Science Block", 0.08),
    ("Engineering Block", "Computer Center", 0.06),
    ("Student Center", "Canteen", 0.08),
    ("Student Center", "Food Court", 0.06),
    ("Student Center", "Library", 0.12),
    ("Canteen", "Food Court", 0.05),
    ("Auditorium", "Central Plaza", 0.06),
    ("Auditorium", "Student Center", 0.10),
    # Sports facilities connections
    ("Sports Complex", "Basketball Court", 0.04),
    ("Sports Complex", "Badminton Court", 0.06),
    ("Sports Complex", "Gymnasium", 0.03),
    ("Basketball Court", "Cricket Ground", 0.08),
    ("Basketball Court", "Football Ground", 0.06),
    ("Cricket Ground", "Football Ground", 0.05),
    ("Tennis Court", "Volleyball Court", 0.04),
    ("Tennis Court", "Sports Complex", 0.08),
    ("Volleyball Court", "Badminton Court", 0.05),
    # Residential area connections
    ("Boys Hostel", "Cricket Ground", 0.06),
    ("Boys Hostel", "Football Ground", 0.08),
    ("Boys Hostel", "Sports Complex", 0.10),
    ("Girls Hostel", "Student Center", 0.12),
    ("Girls Hostel", "Canteen", 0.10),
    ("Girls Hostel", "Medical Center", 0.08),
    ("Faculty Quarters", "Admin Office", 0.15),
    ("Faculty Quarters", "Library", 0.12),
    ("Faculty Quarters", "Engineering Block", 0.08),
    
    # Service and utility connections
    ("Parking Area", "Student Center", 0.10),
    ("Parking Area", "Canteen", 0.08),
    ("Medical Center", "Student Center", 0.12),
    ("Medical Center", "Admin Office", 0.08),
    ("Bookstore", "Student Center", 0.06),
    ("Bookstore", "Library", 0.08),
    ("ATM Center", "Canteen", 0.05),
    ("ATM Center", "Food Court", 0.04),
    ("Computer Center", "Engineering Block", 0.05),
    ("Computer Center", "Library", 0.08),
    ("Guest House", "Faculty Quarters", 0.06),
    ("Guest House", "Admin Office", 0.12),
    
    # Central plaza connections (hub)
    ("Central Plaza", "Student Center", 0.08),
    ("Central Plaza", "Engineering Block", 0.10),
    ("Central Plaza", "Science Block", 0.09)
]

def build_graph():
    """Build adjacency graph from connections"""
    graph = {}
    
    # Initialize all buildings
    for building in CAMPUS_BUILDINGS:
        graph[building] = []
    
    # Add connections (bidirectional)
    for source, dest, distance in CAMPUS_CONNECTIONS:
        if source in graph and dest in graph:
            graph[source].append((dest, distance))
            graph[dest].append((source, distance))
    
    return graph

def calculate_distance(building1, building2):
    """Calculate Euclidean distance between two buildings"""
    if building1 not in CAMPUS_BUILDINGS or building2 not in CAMPUS_BUILDINGS:
        return float('inf')
    
    b1 = CAMPUS_BUILDINGS[building1]
    b2 = CAMPUS_BUILDINGS[building2]
    
    # Simple distance calculation (in km, roughly)
    lat_diff = (b1['lat'] - b2['lat']) * 111.0  # 1 degree lat ≈ 111 km
    lng_diff = (b1['lng'] - b2['lng']) * 85.0   # 1 degree lng ≈ 85 km at this latitude
    
    return (lat_diff**2 + lng_diff**2)**0.5

def bfs_pathfinding(graph, start, goal):
    """Breadth-First Search pathfinding"""
    if start == goal:
        return [start], 0, ['Start and destination are the same']
    
    queue = [(start, [start], 0)]
    visited = {start}
    steps = [f"Starting BFS from {start}"]
    
    while queue:
        current, path, cost = queue.pop(0)
        steps.append(f"Exploring {current}")
        
        for neighbor, distance in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                new_cost = cost + distance
                
                if neighbor == goal:
                    steps.append(f"Found destination {goal}")
                    return new_path, new_cost, steps
                
                queue.append((neighbor, new_path, new_cost))
                steps.append(f"Added {neighbor} to queue")
    
    steps.append("No path found")
    return None, float('inf'), steps

def dfs_pathfinding(graph, start, goal):
    """Depth-First Search pathfinding"""
    if start == goal:
        return [start], 0, ['Start and destination are the same']
    
    stack = [(start, [start], 0)]
    visited = set()
    steps = [f"Starting DFS from {start}"]
    
    while stack:
        current, path, cost = stack.pop()
        
        if current in visited:
            continue
            
        visited.add(current)
        steps.append(f"Visiting {current}")
        
        if current == goal:
            steps.append(f"Found destination {goal}")
            return path, cost, steps
        
        for neighbor, distance in graph.get(current, []):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor], cost + distance))
                steps.append(f"Added {neighbor} to stack")
    
    steps.append("No path found")
    return None, float('inf'), steps

def ucs_pathfinding(graph, start, goal):
    """Uniform Cost Search pathfinding"""
    if start == goal:
        return [start], 0, ['Start and destination are the same']
    
    priority_queue = [(0, start, [start])]
    visited = set()
    steps = [f"Starting UCS from {start}"]
    
    while priority_queue:
        cost, current, path = heapq.heappop(priority_queue)
        
        if current in visited:
            continue
            
        visited.add(current)
        steps.append(f"Visiting {current} with cost {cost:.2f}")
        
        if current == goal:
            steps.append(f"Found optimal path to {goal} with cost {cost:.2f}")
            return path, cost, steps
        
        for neighbor, distance in graph.get(current, []):
            if neighbor not in visited:
                new_cost = cost + distance
                new_path = path + [neighbor]
                heapq.heappush(priority_queue, (new_cost, neighbor, new_path))
                steps.append(f"Added {neighbor} to queue with cost {new_cost:.2f}")
    
    steps.append("No path found")
    return None, float('inf'), steps

def a_star_pathfinding(graph, start, goal):
    """A* Search pathfinding"""
    if start == goal:
        return [start], 0, ['Start and destination are the same']
    
    def heuristic(node):
        return calculate_distance(node, goal)
    
    priority_queue = [(heuristic(start), 0, start, [start])]
    visited = set()
    steps = [f"Starting A* from {start} to {goal}"]
    
    while priority_queue:
        f_cost, g_cost, current, path = heapq.heappop(priority_queue)
        
        if current in visited:
            continue
            
        visited.add(current)
        h_cost = f_cost - g_cost
        steps.append(f"Visiting {current}: g={g_cost:.2f}, h={h_cost:.2f}, f={f_cost:.2f}")
        
        if current == goal:
            steps.append(f"Found optimal path to {goal} with cost {g_cost:.2f}")
            return path, g_cost, steps
        
        for neighbor, distance in graph.get(current, []):
            if neighbor not in visited:
                new_g_cost = g_cost + distance
                new_h_cost = heuristic(neighbor)
                new_f_cost = new_g_cost + new_h_cost
                new_path = path + [neighbor]
                heapq.heappush(priority_queue, (new_f_cost, new_g_cost, neighbor, new_path))
                steps.append(f"Added {neighbor}: g={new_g_cost:.2f}, h={new_h_cost:.2f}, f={new_f_cost:.2f}")
    
    steps.append("No path found")
    return None, float('inf'), steps

# Build the campus graph
campus_graph = build_graph()

# Algorithm mapping
ALGORITHMS = {
    'BFS': bfs_pathfinding,
    'DFS': dfs_pathfinding,
    'UCS': ucs_pathfinding,
    'A*': a_star_pathfinding
}

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    try:
        return send_from_directory('../frontend', filename)
    except:
        return "File not found", 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'message': 'Chanakya University PathFinder API is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/buildings')
def get_buildings():
    """Get all available buildings"""
    buildings = []
    for name, data in CAMPUS_BUILDINGS.items():
        buildings.append({
            'name': name,
            'lat': data['lat'],
            'lng': data['lng'],
            'type': data['type']
        })
    
    return jsonify({
        'buildings': buildings,
        'count': len(buildings)
    })

@app.route('/api/pathfind', methods=['POST'])
def find_path():
    """Find path between two buildings using A* algorithm"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        start = data.get('start')
        end = data.get('end')
        algorithm = 'A*'  # Fixed to A* algorithm only
        
        # Validate inputs
        if not start or not end:
            return jsonify({'error': 'Start and end locations are required'}), 400
        
        if start not in CAMPUS_BUILDINGS:
            return jsonify({'error': f'Unknown start location: {start}'}), 400
        
        if end not in CAMPUS_BUILDINGS:
            return jsonify({'error': f'Unknown end location: {end}'}), 400
        
        # Find path using A* algorithm only
        logger.info(f"Finding path from {start} to {end} using A* algorithm")
        
        path_func = ALGORITHMS['A*']
        path, cost, steps = path_func(campus_graph, start, end)
        
        if path is None:
            return jsonify({
                'success': False,
                'error': 'No path found',
                'steps': steps
            }), 404
        
        # Calculate additional metrics
        walking_speed_kmh = 5.0  # Average walking speed
        walking_time_hours = cost / walking_speed_kmh
        walking_time_minutes = walking_time_hours * 60
        
        # Get coordinates for path
        coordinates = []
        for building in path:
            if building in CAMPUS_BUILDINGS:
                building_data = CAMPUS_BUILDINGS[building]
                coordinates.append([building_data['lat'], building_data['lng']])
        
        response = {
            'success': True,
            'path': path,
            'cost': round(cost, 3),
            'distance_km': round(cost, 3),
            'walking_time_minutes': round(walking_time_minutes, 1),
            'num_stops': len(path) - 2,  # Excluding start and end
            'algorithm': algorithm,
            'coordinates': coordinates,
            'steps': steps,
            'start': start,
            'end': end,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Path found: {' -> '.join(path)} (Cost: {cost:.3f}km, Time: {walking_time_minutes:.1f}min)")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in pathfinding: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/compare', methods=['POST'])
def compare_algorithms():
    """Compare multiple algorithms for the same path"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        start = data.get('start')
        end = data.get('end')
        algorithms = data.get('algorithms', ['BFS', 'DFS', 'UCS', 'A*'])
        
        # Validate inputs
        if not start or not end:
            return jsonify({'error': 'Start and end locations are required'}), 400
        
        if start not in CAMPUS_BUILDINGS:
            return jsonify({'error': f'Unknown start location: {start}'}), 400
        
        if end not in CAMPUS_BUILDINGS:
            return jsonify({'error': f'Unknown end location: {end}'}), 400
        
        results = {}
        
        for algorithm in algorithms:
            if algorithm in ALGORITHMS:
                logger.info(f"Running {algorithm} for comparison")
                
                path_func = ALGORITHMS[algorithm]
                path, cost, steps = path_func(campus_graph, start, end)
                
                if path is not None:
                    walking_speed_kmh = 5.0
                    walking_time_hours = cost / walking_speed_kmh
                    walking_time_minutes = walking_time_hours * 60
                    
                    results[algorithm] = {
                        'path': path,
                        'cost': round(cost, 3),
                        'distance_km': round(cost, 3),
                        'walking_time_minutes': round(walking_time_minutes, 1),
                        'num_stops': len(path) - 2,
                        'steps_count': len(steps),
                        'found': True
                    }
                else:
                    results[algorithm] = {
                        'path': None,
                        'cost': float('inf'),
                        'distance_km': float('inf'),
                        'walking_time_minutes': float('inf'),
                        'num_stops': 0,
                        'steps_count': len(steps),
                        'found': False
                    }
        
        response = {
            'success': True,
            'start': start,
            'end': end,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in algorithm comparison: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/satellite-info')
def get_satellite_info():
    """Get information about available satellite imagery sources"""
    satellite_sources = {
        'Google Satellite': {
            'provider': 'Google',
            'description': 'High-resolution commercial satellite imagery',
            'max_zoom': 20,
            'coverage': 'Global',
            'update_frequency': 'Monthly to Yearly'
        },
        'Google Hybrid': {
            'provider': 'Google',
            'description': 'Satellite imagery with street labels overlay',
            'max_zoom': 20,
            'coverage': 'Global',
            'update_frequency': 'Monthly to Yearly'
        },
        'ISRO Bhuvan': {
            'provider': 'Indian Space Research Organisation (ISRO)',
            'description': 'Real satellite imagery from Indian Chandrayaan missions',
            'max_zoom': 18,
            'coverage': 'India and surrounding regions',
            'update_frequency': 'Quarterly',
            'satellite_missions': ['Chandrayaan-1', 'Chandrayaan-2', 'Mangalyaan', 'RISAT'],
            'special_features': 'Authentic Indian space program data'
        },
        'ISRO Hybrid': {
            'provider': 'Indian Space Research Organisation (ISRO)',
            'description': 'ISRO satellite data with geographical labels',
            'max_zoom': 18,
            'coverage': 'India focused',
            'update_frequency': 'Quarterly'
        },
        'Esri Satellite': {
            'provider': 'Esri/Maxar',
            'description': 'Professional GIS satellite imagery',
            'max_zoom': 18,
            'coverage': 'Global',
            'update_frequency': 'Regular updates'
        },
        'Mapbox Satellite': {
            'provider': 'Mapbox',
            'description': 'Customizable satellite imagery for developers',
            'max_zoom': 19,
            'coverage': 'Global',
            'update_frequency': 'Regular updates'
        }
    }
    
    return jsonify({
        'satellite_sources': satellite_sources,
        'total_sources': len(satellite_sources),
        'recommended_for_india': 'ISRO Bhuvan',
        'recommended_global': 'Google Satellite',
        'info': 'CU PathFinder supports multiple satellite imagery sources including real Indian satellite data from ISRO Chandrayaan missions'
    })

@app.route('/api/building/<building_name>')
def get_building_info(building_name):
    """Get information about a specific building"""
    if building_name not in CAMPUS_BUILDINGS:
        return jsonify({'error': f'Building not found: {building_name}'}), 404
    
    building_data = CAMPUS_BUILDINGS[building_name]
    
    # Find connected buildings
    connections = []
    for neighbor, distance in campus_graph.get(building_name, []):
        connections.append({
            'building': neighbor,
            'distance_km': round(distance, 3),
            'walking_time_minutes': round(distance / 5.0 * 60, 1)
        })
    
    response = {
        'name': building_name,
        'coordinates': {
            'lat': building_data['lat'],
            'lng': building_data['lng']
        },
        'type': building_data['type'],
        'connections': connections,
        'connection_count': len(connections)
    }
    
    return jsonify(response)

@app.route('/api/chatbot', methods=['POST'])
def chatbot_query():
    """Process chatbot queries with simple pattern matching"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        logger.info(f"Processing chatbot query: {user_message}")
        
        # Simple pattern matching for pathfinding queries
        message_lower = user_message.lower()
        
        # Building mapping for easier recognition
        building_keywords = {
            'library': 'Library',
            'engineering center': 'Engineering Center',
            'engineering': 'Engineering Center',
            'student center': 'Student Center', 
            'canteen': 'C4C',
            'food court': 'Food Court',
            'c4c': 'C4C',
            'gym': 'Rec Center',
            'rec center': 'Rec Center',
            'recreation': 'Rec Center',
            'medical center': 'Medical Center',
            'bookstore': 'Bookstore',
            'parking': 'Parking Garage',
            'sports complex': 'Sports Complex',
            'sports': 'Sports Complex',
            'auditorium': 'Auditorium'
        }
        
        # Check for "where is" queries or "tell me about" queries
        if 'where is' in message_lower or 'tell me about' in message_lower:
            for keyword, building_name in building_keywords.items():
                if keyword in message_lower and building_name in CAMPUS_BUILDINGS:
                    building_data = CAMPUS_BUILDINGS[building_name]
                    
                    response_text = f"📍 **{building_name}**\n\n"
                    response_text += f"**Type:** {building_data['type'].title()}\n"
                    response_text += f"**Coordinates:** {building_data['lat']:.4f}, {building_data['lng']:.4f}\n\n"
                    
                    # Find connections
                    connections = []
                    for neighbor, distance in campus_graph.get(building_name, []):
                        connections.append(f"• {neighbor} ({round(distance * 1000)}m away)")
                    
                    if connections:
                        response_text += f"**Connected to:**\n"
                        response_text += "\n".join(connections[:3])  # Show first 3 connections
                        if len(connections) > 3:
                            response_text += f"\n... and {len(connections) - 3} more locations"
                    
                    response_text += f"\n\nWould you like directions to {building_name}? Just ask!"
                    
                    return jsonify({
                        'success': True,
                        'response': response_text,
                        'type': 'information'
                    })
        
        # Check for pathfinding patterns
        elif ('from' in message_lower and 'to' in message_lower) or 'get' in message_lower or 'route' in message_lower:
            start = None
            end = None
            
            # Handle "from X to Y" pattern
            if 'from' in message_lower and 'to' in message_lower:
                parts = message_lower.split('from')[1].split('to')
                if len(parts) >= 2:
                    from_part = parts[0].strip()
                    to_part = parts[1].strip()
                    
                    for keyword, building_name in building_keywords.items():
                        if keyword in from_part:
                            start = building_name
                        if keyword in to_part:
                            end = building_name
            else:
                # Find any building mentioned and assume Student Center as start
                for keyword, building_name in building_keywords.items():
                    if keyword in message_lower:
                        end = building_name
                        start = 'Student Center'  # Central location as default
                        break
            
            if start and end and start in CAMPUS_BUILDINGS and end in CAMPUS_BUILDINGS:
                # Find path using A* algorithm
                path_func = ALGORITHMS['A*']
                path, cost, steps = path_func(campus_graph, start, end)
                
                if path is None:
                    return jsonify({
                        'success': True,
                        'response': f"I couldn't find a path from {start} to {end}.",
                        'type': 'error'
                    })
                
                # Calculate walking time
                walking_speed_kmh = 5.0
                walking_time_minutes = (cost / walking_speed_kmh) * 60
                
                response_text = f"�️ **Route found from {start} to {end}!**\n\n"
                response_text += f"📏 **Distance:** {round(cost * 1000)}m\n"
                response_text += f"🚶 **Walking time:** {round(walking_time_minutes, 1)} minutes\n\n"
                response_text += f"The shortest route has been found using A* algorithm! 🎯"
                
                return jsonify({
                    'success': True,
                    'response': response_text,
                    'type': 'pathfinding',
                    'path_data': {
                        'path': path,
                        'cost': round(cost, 3),
                        'distance_meters': round(cost * 1000),
                        'walking_time_minutes': round(walking_time_minutes, 1),
                        'algorithm': 'A*'
                    }
                })
        
        # Handle help queries
        elif 'help' in message_lower:
            response_text = "🤖 **I'm your AI campus navigation assistant!**\n\n"
            response_text += "**🛣️ Find Routes:**\n"
            response_text += "• \"How do I get from Engineering Center to Library?\"\n"
            response_text += "• \"Find route to Rec Center\"\n\n"
            response_text += "**📍 Get Information:**\n"
            response_text += "• \"Where is the Library?\"\n"
            response_text += "• \"Where is the Student Center?\"\n\n"
            response_text += "Just ask me and I'll help you navigate! 🗺️"
            
            return jsonify({
                'success': True,
                'response': response_text,
                'type': 'help'
            })
        
        # Handle greetings
        elif any(greeting in message_lower for greeting in ['hello', 'hi', 'hey']):
            response_text = "Hello! I'm your AI campus navigation assistant. Ask me for directions or building locations!"
            
            return jsonify({
                'success': True,
                'response': response_text,
                'type': 'greeting'
            })
        
        # Default response
        else:
            response_text = "Try asking:\n"
            response_text += "• 'How do I get from Engineering Center to Library?'\n"
            response_text += "• 'Find route to Rec Center'\n"
            response_text += "• 'Where is the Student Center?'\n\n"
            response_text += "What can I help you with?"
            
            return jsonify({
                'success': True,
                'response': response_text,
                'type': 'help'
            })
            
    except Exception as e:
        logger.error(f"Error in chatbot query: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'response': "I'm sorry, I encountered an error. Please try again."
        }), 500

@app.route('/api/save-buildings', methods=['POST'])
def save_buildings():
    """Save building data to campus-data.js file"""
    try:
        data = request.get_json()
        buildings = data.get('buildings', {})
        
        # Path to campus-data.js file
        campus_data_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'js', 'campus-data.js')
        
        # Read current file content
        with open(campus_data_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the buildings object
        start_marker = 'buildings: {'
        end_marker = '},'
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return jsonify({'success': False, 'error': 'Could not find buildings object'}), 400
        
        # Find the end of buildings object (looking for the closing brace followed by comma)
        brace_count = 0
        end_idx = -1
        for i in range(start_idx + len(start_marker), len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                if brace_count == 0:
                    end_idx = i + 1
                    break
                brace_count -= 1
        
        if end_idx == -1:
            return jsonify({'success': False, 'error': 'Could not find end of buildings object'}), 400
        
        # Build new buildings string
        buildings_str = 'buildings: {\n'
        for name, data in buildings.items():
            buildings_str += f'        "{name}": {{\n'
            buildings_str += f'            "lat": {data["lat"]},\n'
            buildings_str += f'            "lng": {data["lng"]},\n'
            buildings_str += f'            "type": "{data.get("type", "building")}"\n'
            buildings_str += '        },\n'
        buildings_str += '    }'
        
        # Replace the content
        new_content = content[:start_idx] + buildings_str + content[end_idx:]
        
        # Write back to file
        with open(campus_data_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Saved {len(buildings)} buildings to campus-data.js")
        
        return jsonify({
            'success': True,
            'message': f'Successfully saved {len(buildings)} buildings',
            'buildings_count': len(buildings)
        })
        
    except Exception as e:
        logger.error(f"Error saving buildings: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error saving buildings: {str(e)}'
        }), 500

# ===== CUSTOM PATH MANAGEMENT ENDPOINTS =====

@app.route('/api/save-path', methods=['POST'])
def save_custom_path():
    """Save a custom path created by the user."""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Path name is required'}), 400
        
        if not data.get('coordinates') or len(data['coordinates']) == 0:
            return jsonify({'error': 'Path coordinates are required'}), 400
        
        path_name = data['name']
        coordinates = data['coordinates']
        description = data.get('description', '')
        
        # Create path object
        custom_path = {
            'id': len(SAVED_PATHS) + 1,
            'name': path_name,
            'coordinates': coordinates,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'coordinate_count': len(coordinates)
        }
        
        # Save to storage
        SAVED_PATHS[path_name] = custom_path
        
        logger.info(f"✅ Saved custom path: {path_name} with {len(coordinates)} coordinates")
        
        return jsonify({
            'success': True,
            'message': f'Path "{path_name}" saved successfully',
            'path': custom_path
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error saving custom path: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-paths', methods=['GET'])
def get_saved_paths():
    """Retrieve all saved custom paths."""
    try:
        paths_list = list(SAVED_PATHS.values())
        
        return jsonify({
            'success': True,
            'total_paths': len(paths_list),
            'paths': paths_list
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error retrieving paths: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-path/<path_name>', methods=['GET'])
def get_path_by_name(path_name):
    """Retrieve a specific saved path by name."""
    try:
        if path_name in SAVED_PATHS:
            return jsonify({
                'success': True,
                'path': SAVED_PATHS[path_name]
            }), 200
        else:
            return jsonify({'error': f'Path "{path_name}" not found'}), 404
            
    except Exception as e:
        logger.error(f"❌ Error retrieving path: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-path/<path_name>', methods=['DELETE'])
def delete_path(path_name):
    """Delete a saved custom path."""
    try:
        if path_name in SAVED_PATHS:
            deleted_path = SAVED_PATHS.pop(path_name)
            logger.info(f"✅ Deleted custom path: {path_name}")
            
            return jsonify({
                'success': True,
                'message': f'Path "{path_name}" deleted successfully',
                'deleted_path': deleted_path
            }), 200
        else:
            return jsonify({'error': f'Path "{path_name}" not found'}), 404
            
    except Exception as e:
        logger.error(f"❌ Error deleting path: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/update-path/<path_name>', methods=['PUT'])
def update_path(path_name):
    """Update an existing custom path."""
    try:
        if path_name not in SAVED_PATHS:
            return jsonify({'error': f'Path "{path_name}" not found'}), 404
        
        data = request.json
        
        # Update fields
        if 'coordinates' in data and len(data['coordinates']) > 0:
            SAVED_PATHS[path_name]['coordinates'] = data['coordinates']
            SAVED_PATHS[path_name]['coordinate_count'] = len(data['coordinates'])
        
        if 'description' in data:
            SAVED_PATHS[path_name]['description'] = data['description']
        
        SAVED_PATHS[path_name]['updated_at'] = datetime.now().isoformat()
        
        logger.info(f"✅ Updated custom path: {path_name}")
        
        return jsonify({
            'success': True,
            'message': f'Path "{path_name}" updated successfully',
            'path': SAVED_PATHS[path_name]
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error updating path: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting CU PathFinder API server on port {port}")
    logger.info(f"Available buildings: {len(CAMPUS_BUILDINGS)}")
    logger.info(f"Available connections: {len(CAMPUS_CONNECTIONS)}")
    logger.info(f"Available algorithms: {list(ALGORITHMS.keys())}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
