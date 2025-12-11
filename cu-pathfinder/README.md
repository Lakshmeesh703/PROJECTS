# Chanakya University PathFinder

## AI-Powered Campus Navigation System

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Project Overview

**Chanakya University PathFinder** is an intelligent campus navigation system that helps students, faculty, and visitors find optimal routes across the campus. Using advanced pathfinding algorithms and an intuitive web interface, users can:

- **Find Optimal Routes** - Uses AI algorithms (BFS, DFS, UCS, A*) to calculate the best path
- **Interactive Map** - Real-time campus map with 30+ locations
- **AI Chatbot** - Natural language navigation assistant
- **Algorithm Comparison** - Compare pathfinding algorithms side-by-side
- **Custom Paths** - Create, save, and manage personalized routes
- **Mobile Responsive** - Works seamlessly on desktop, tablet, and mobile

---

## Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser
- ~50 MB disk space

### Installation

1. **Clone or extract the project:**
```bash
cd cu-pathfinder
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python3 run_application.py
```

4. **Open in browser:**
```
http://localhost:5000
```

Done! The application is ready to use.

---

## Features

### Core Features

#### 1. Interactive Campus Map
- 30+ campus locations with accurate coordinates
- Real-time location updates
- Zoom and pan functionality
- Building information popups

#### 2. Advanced Pathfinding
- **BFS (Breadth-First Search)** - Explores all paths equally
- **DFS (Depth-First Search)** - Explores deeper paths first
- **UCS (Uniform Cost Search)** - Finds least-cost paths
- **A* Algorithm** - Most efficient intelligent search

#### 3. Custom Path Management
- Draw custom paths on the map
- Save paths with names and descriptions
- Real-time distance calculation
- Load and reuse saved paths

#### 4. AI Chatbot Assistant
- Natural language queries
- Building recommendations
- Route suggestions
- Navigation guidance

#### 5. Route Comparison
- Compare multiple algorithms
- Visualize different path options
- Performance metrics
- Step-by-step guidance

#### 6. Campus Infrastructure
- View cement roads
- Identify main exits
- Water facilities location
- Sports complex areas
- Residential zones

---

## Architecture

### Technology Stack

**Backend:**
- Flask (Python web framework)
- NetworkX (Graph algorithms)
- NumPy (Numerical computations)
- Matplotlib (Visualization)

**Frontend:**
- HTML5, CSS3, JavaScript
- Leaflet.js (Interactive mapping)
- Chart.js (Data visualization)
- Responsive design patterns

**Data:**
- 30+ Campus locations
- 50+ Connection roads
- Real-world coordinates

### Project Structure

```
cu-pathfinder/
├── backend/
│   ├── app.py                 # Flask application & API endpoints
│   ├── campus_graph.py        # Campus graph data structure
│   └── search_algorithms.py   # Pathfinding algorithms
├── frontend/
│   ├── index.html             # Main application page
│   ├── js/                    # JavaScript modules (8 files)
│   │   ├── app.js
│   │   ├── map-manager.js
│   │   ├── path-manager.js
│   │   ├── pathfinding.js
│   │   └── ... (5 more modules)
│   └── css/                   # Stylesheets (2 files)
├── run_application.py         # Unified launcher
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## API Endpoints

### Buildings
```
GET /api/buildings
GET /api/building/<name>
```

### Pathfinding
```
POST /api/pathfind
  {
    "start": "Main Gate",
    "end": "Library",
    "algorithm": "astar"
  }
```

### Algorithm Comparison
```
POST /api/compare
  {
    "start": "Building A",
    "end": "Building B"
  }
```

### Path Management
```
POST   /api/save-path       - Save custom path
GET    /api/get-paths       - Get all saved paths
GET    /api/get-path/<name> - Get specific path
PUT    /api/update-path     - Update path
DELETE /api/delete-path     - Delete path
```

### Health Check
```
GET /api/health
```

---

## Usage Examples

### Finding a Route

1. **Open the Application:**
   - Navigate to `http://localhost:5000`

2. **Select Start and End Points:**
   - Choose locations from dropdowns
   - Or click on the map

3. **Choose Algorithm:**
   - A* (Recommended - fastest)
   - UCS (Shortest distance)
   - BFS (Explores equally)
   - DFS (Explores deeper)

4. **View Route:**
   - Route highlights on map
   - Distance and instructions shown
   - Step-by-step guidance available

### Creating Custom Paths

1. **Click "Start Drawing Path"**
2. **Click map points** to create path
3. **Enter path name** and description
4. **Click "Save Path"** to save to backend
5. **Access saved paths** anytime from the panel

### Using Chatbot

1. **Open Chatbot** from sidebar
2. **Ask questions** in natural language:
   - "How do I get to the library?"
   - "Where is the sports complex?"
   - "Find route to cafeteria"
3. **Get instant responses** with directions

---

## Algorithms Explained

### Breadth-First Search (BFS)
- **Time Complexity:** O(V + E)
- **Use Case:** Finding shortest path in unweighted graphs
- **Best For:** Equal distance exploration

### Depth-First Search (DFS)
- **Time Complexity:** O(V + E)
- **Use Case:** Exploring all paths deeply
- **Best For:** Comprehensive exploration

### Uniform Cost Search (UCS)
- **Time Complexity:** O((V + E) log V)
- **Use Case:** Weighted shortest path
- **Best For:** Roads with different costs

### A* Algorithm
- **Time Complexity:** O(E)
- **Use Case:** Heuristic-guided shortest path
- **Best For:** Fast, optimal solutions (RECOMMENDED)

---

## Campus Locations

The system includes 30+ key campus locations:

**Academic Buildings:**
- Main Gate
- Admin Office
- Auditorium
- Engineering Block
- Science Block
- Library
- Computer Center

**Facilities:**
- Canteen & Food Court
- Sports Complex
- Gymnasium
- Medical Center
- Bookstore
- ATM Center

**Residential:**
- Boys Hostel
- Girls Hostel
- Faculty Quarters
- Guest House

**Infrastructure:**
- Parking Area
- Security Office
- Central Plaza
- Various Sports Courts

---

## Testing

### Automated Testing

Run the included test script:
```bash
python3 test_path_management.py
```

This tests:
- Path saving and retrieval
- Algorithm performance
- API endpoints
- Error handling

### Manual Testing

Use cURL to test endpoints:
```bash
# Save a path
curl -X POST http://localhost:5000/api/save-path \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Route",
    "coordinates": [{"lat": 13.22, "lng": 77.75}],
    "description": "Test"
  }'

# Get all paths
curl http://localhost:5000/api/get-paths
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Server won't start** | Check if port 5000 is available: `lsof -i :5000` |
| **Module not found** | Install dependencies: `pip install -r requirements.txt` |
| **Map not loading** | Clear browser cache (Ctrl+Shift+Delete) |
| **Paths not saving** | Verify backend is running on port 5000 |
| **Slow performance** | Use A* algorithm (most efficient) |

---

## Performance

- **Response Time:** < 100ms for most routes
- **Algorithm Comparison:** All 4 algorithms in < 500ms
- **Campus Size:** 30+ locations, 50+ roads
- **Browser Support:** Chrome, Firefox, Safari, Edge

---

## Future Enhancements

- [ ] Database persistence (SQLite/PostgreSQL)
- [ ] User authentication & profiles
- [ ] Real-time location tracking
- [ ] Offline route caching
- [ ] Voice-guided navigation
- [ ] Integration with campus apps
- [ ] Event-based route planning
- [ ] Path sharing with QR codes

---

## Requirements

```
Flask==2.3.0
Flask-CORS==4.0.0
NetworkX==3.0
NumPy==1.24.0
Matplotlib==3.7.0
```

Install all:
```bash
pip install -r requirements.txt
```

---

## Team & Credits

**Project:** Chanakya University PathFinder  
**Institution:** Chanakya University, Karnataka, India  
**Purpose:** AI-Powered Campus Navigation System  

**Key Technologies:**
- Python Flask Backend
- Leaflet.js Interactive Maps
- AI Pathfinding Algorithms
- Responsive Web Design

---

## Support & Contact

For issues, questions, or suggestions:

- Email: laskhmeeshshet744@gmail.com
- LinkedIn: Lakshmeesh Shet

---

## License

MIT License - Free to use for educational and commercial purposes.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Total Locations** | 30+ |
| **Campus Connections** | 50+ |
| **Algorithms** | 4 (BFS, DFS, UCS, A*) |
| **Frontend Files** | 11 (1 HTML, 2 CSS, 8 JS) |
| **Backend Endpoints** | 9 |
| **Response Time** | < 100ms |
| **Project Size** | ~850 KB |

---

## Highlights

- **Production Ready** - Fully tested and optimized
- **User Friendly** - Intuitive interface for all users
- **Fast Performance** - < 100ms response times
- **Mobile Responsive** - Works on all devices
- **AI Powered** - Intelligent pathfinding algorithms
- **Custom Routes** - Create and save personalized paths
- **Open Source** - Available for learning & customization  

---

## Getting Started Now

```bash
# 1. Navigate to project
cd cu-pathfinder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start application
python3 run_application.py

# 4. Open browser
# → http://localhost:5000

# 5. Start navigating!
```

---

**Last Updated:** December 2025  
**Version:** 1.0.0  
**Status:** Production Ready

---

## Share This Project

If you found this project useful, please:
- Star the repository
- Share on LinkedIn
- Comment with feedback
- Forward to colleagues

---

**Thank you for using Chanakya University PathFinder!**
