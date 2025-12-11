// Pathfinding Module for CU PathFinder Frontend
// Handles all pathfinding operations and backend communication

class PathfindingEngine {
    constructor() {
        this.baseURL = 'http://localhost:5000'; // Flask backend URL
        this.isOnline = false;
        this.fallbackMode = true; // Use client-side algorithms when backend unavailable
        this.lastResult = null;
        this.algorithm = 'A*'; // Fixed to A* only
        
        // Initialize connection to backend
        this.checkBackendConnection();
    }
    
    // Check if backend is available
    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.baseURL}/health`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                timeout: 3000
            });
            
            if (response.ok) {
                this.isOnline = true;
                console.log('✅ Backend connection established');
                return true;
            }
        } catch (error) {
            console.log('⚠️  Backend unavailable, using fallback mode');
            this.isOnline = false;
        }
        return false;
    }
    
    // Main pathfinding function
    async findPath(startLocation, endLocation, stops = []) {
        // Validate inputs
        if (!startLocation || !endLocation) {
            throw new Error('Start and end locations are required');
        }
        
        // Check if CampusData is available
        if (typeof CampusData === 'undefined' || !CampusData.buildings) {
            throw new Error('Campus data not loaded. Please refresh the page.');
        }
        
        // Check if campus tour route is available and use it for pathfinding
        const savedCampusTour = localStorage.getItem('campusTourRoute');
        if (savedCampusTour) {
            try {
                const campusTour = JSON.parse(savedCampusTour);
                const campusRouteResult = this.findPathUsingCampusTour(startLocation, endLocation, campusTour);
                if (campusRouteResult) {
                    return campusRouteResult;
                }
            } catch (error) {
                console.warn('Failed to use campus tour route, falling back to normal pathfinding:', error);
            }
        }
        
        // Normalize location names
        const start = this.normalizeLocationName(startLocation);
        const end = this.normalizeLocationName(endLocation);
        
        if (!start || !end) {
            console.error('Location normalization failed:', {
                startLocation, endLocation,
                availableBuildings: Object.keys(CampusData.buildings || {})
            });
            throw new Error(`Invalid location names: "${startLocation}" -> "${endLocation}"`);
        }
        
        // Prepare request data
        const requestData = {
            start: start,
            end: end,
            algorithm: 'A*', // Fixed to A* algorithm
            stops: stops.map(stop => this.normalizeLocationName(stop)).filter(Boolean)
        };
        
        try {
            let result;
            
            if (this.isOnline) {
                // Try backend first
                result = await this.findPathOnline(requestData);
            } else {
                // Use fallback client-side algorithm
                result = await this.findPathOffline(requestData);
            }
            
            this.lastResult = result;
            return result;
            
        } catch (error) {
            console.error('Pathfinding error:', error);
            
            // If online fails, try offline
            if (this.isOnline) {
                console.log('Backend failed, falling back to client-side algorithm');
                return await this.findPathOffline(requestData);
            }
            
            throw error;
        }
    }
    
    // Backend pathfinding
    async findPathOnline(requestData) {
        const response = await fetch(`${this.baseURL}/api/pathfind`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`Backend error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        return {
            success: true,
            algorithm: data.algorithm,
            path: data.path,
            distance: data.distance,
            walkingTime: data.walkingTime || CampusData.utils.calculateWalkingTime(data.distance),
            executionTime: data.executionTime,
            nodesExplored: data.nodesExplored,
            isOptimal: data.isOptimal,
            steps: data.steps || this.generateSteps(data.path),
            coordinates: this.getPathCoordinates(data.path),
            source: 'backend'
        };
    }
    
    // Client-side fallback pathfinding using UCS
    async findPathOffline(requestData) {
        const { start, end, algorithm } = requestData;
        
        // Build graph from campus data
        const graph = this.buildGraph();
        
        // Select algorithm (default to UCS for offline mode)
        let pathResult;
        switch (algorithm) {
            case 'BFS':
                pathResult = this.breadthFirstSearch(graph, start, end);
                break;
            case 'DFS':
                pathResult = this.depthFirstSearch(graph, start, end);
                break;
            case 'A*':
                pathResult = this.aStarSearch(graph, start, end);
                break;
            case 'UCS':
            default:
                pathResult = this.uniformCostSearch(graph, start, end);
                break;
        }
        
        if (!pathResult.path) {
            throw new Error(`No path found from ${start} to ${end}`);
        }
        
        return {
            success: true,
            algorithm: algorithm,
            path: pathResult.path,
            distance: pathResult.distance,
            walkingTime: CampusData.utils.calculateWalkingTime(pathResult.distance),
            executionTime: pathResult.executionTime,
            nodesExplored: pathResult.nodesExplored,
            isOptimal: algorithm === 'UCS' || algorithm === 'A*',
            steps: this.generateSteps(pathResult.path),
            coordinates: this.getPathCoordinates(pathResult.path),
            source: 'client'
        };
    }
    
    // Compare all algorithms
    async compareAlgorithms(startLocation, endLocation) {
        const start = this.normalizeLocationName(startLocation);
        const end = this.normalizeLocationName(endLocation);
        
        if (!start || !end) {
            throw new Error('Invalid location names provided');
        }
        
        const results = [];
        const algorithms = ['BFS', 'DFS', 'UCS', 'A*'];
        
        for (const algorithm of algorithms) {
            try {
                const result = await this.findPath(start, end, algorithm);
                results.push({
                    algorithm: algorithm,
                    distance: result.distance,
                    nodesExplored: result.nodesExplored,
                    executionTime: result.executionTime,
                    isOptimal: result.isOptimal,
                    path: result.path
                });
            } catch (error) {
                results.push({
                    algorithm: algorithm,
                    error: error.message,
                    distance: null,
                    nodesExplored: null,
                    executionTime: null,
                    isOptimal: false
                });
            }
        }
        
        return results;
    }
    
    // Build graph from campus data
    buildGraph() {
        const graph = {};
        
        // Initialize nodes
        for (const building of Object.keys(CampusData.buildings)) {
            graph[building] = {};
        }
        
        // Add edges with validation
        for (const connection of CampusData.connections) {
            // Validate that both buildings exist in our data
            if (CampusData.buildings[connection.from] && CampusData.buildings[connection.to]) {
                // Initialize if not exists
                if (!graph[connection.from]) graph[connection.from] = {};
                if (!graph[connection.to]) graph[connection.to] = {};
                
                // Add bidirectional connections
                graph[connection.from][connection.to] = connection.distance;
                graph[connection.to][connection.from] = connection.distance;
            } else {
                console.warn(`Connection references missing buildings: ${connection.from} -> ${connection.to}`);
            }
        }
        
        return graph;
    }
    
    // Uniform Cost Search (Dijkstra's Algorithm)
    uniformCostSearch(graph, start, end) {
        const startTime = performance.now();
        
        const distances = {};
        const previous = {};
        const visited = new Set();
        const queue = [{node: start, cost: 0}];
        let nodesExplored = 0;
        
        // Initialize distances
        for (const node of Object.keys(graph)) {
            distances[node] = Infinity;
        }
        distances[start] = 0;
        
        while (queue.length > 0) {
            // Sort queue by cost (min-heap simulation)
            queue.sort((a, b) => a.cost - b.cost);
            const current = queue.shift();
            
            if (visited.has(current.node)) continue;
            
            visited.add(current.node);
            nodesExplored++;
            
            if (current.node === end) {
                break;
            }
            
            // Explore neighbors
            for (const neighbor of Object.keys(graph[current.node])) {
                if (visited.has(neighbor)) continue;
                
                const newCost = distances[current.node] + graph[current.node][neighbor];
                
                if (newCost < distances[neighbor]) {
                    distances[neighbor] = newCost;
                    previous[neighbor] = current.node;
                    queue.push({node: neighbor, cost: newCost});
                }
            }
        }
        
        // Reconstruct path
        const path = [];
        let current = end;
        while (current !== undefined) {
            path.unshift(current);
            current = previous[current];
        }
        
        const executionTime = (performance.now() - startTime).toFixed(2);
        
        return {
            path: path.length > 1 ? path : null,
            distance: distances[end] === Infinity ? null : distances[end],
            nodesExplored: nodesExplored,
            executionTime: parseFloat(executionTime)
        };
    }
    
    // Breadth-First Search
    breadthFirstSearch(graph, start, end) {
        const startTime = performance.now();
        
        const queue = [start];
        const visited = new Set([start]);
        const previous = {};
        let nodesExplored = 0;
        
        while (queue.length > 0) {
            const current = queue.shift();
            nodesExplored++;
            
            if (current === end) {
                break;
            }
            
            for (const neighbor of Object.keys(graph[current])) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    previous[neighbor] = current;
                    queue.push(neighbor);
                }
            }
        }
        
        // Reconstruct path
        const path = [];
        let current = end;
        while (current !== undefined) {
            path.unshift(current);
            current = previous[current];
        }
        
        // Calculate distance
        let distance = 0;
        if (path.length > 1) {
            for (let i = 0; i < path.length - 1; i++) {
                distance += graph[path[i]][path[i + 1]] || 0;
            }
        }
        
        const executionTime = (performance.now() - startTime).toFixed(2);
        
        return {
            path: path.length > 1 ? path : null,
            distance: path.length > 1 ? distance : null,
            nodesExplored: nodesExplored,
            executionTime: parseFloat(executionTime)
        };
    }
    
    // Depth-First Search
    depthFirstSearch(graph, start, end) {
        const startTime = performance.now();
        
        const stack = [start];
        const visited = new Set();
        const previous = {};
        let nodesExplored = 0;
        
        while (stack.length > 0) {
            const current = stack.pop();
            
            if (visited.has(current)) continue;
            
            visited.add(current);
            nodesExplored++;
            
            if (current === end) {
                break;
            }
            
            const neighbors = Object.keys(graph[current]).reverse(); // Reverse for consistent ordering
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    previous[neighbor] = current;
                    stack.push(neighbor);
                }
            }
        }
        
        // Reconstruct path
        const path = [];
        let current = end;
        while (current !== undefined) {
            path.unshift(current);
            current = previous[current];
        }
        
        // Calculate distance
        let distance = 0;
        if (path.length > 1) {
            for (let i = 0; i < path.length - 1; i++) {
                distance += graph[path[i]][path[i + 1]] || 0;
            }
        }
        
        const executionTime = (performance.now() - startTime).toFixed(2);
        
        return {
            path: path.length > 1 ? path : null,
            distance: path.length > 1 ? distance : null,
            nodesExplored: nodesExplored,
            executionTime: parseFloat(executionTime)
        };
    }
    
    // A* Search
    aStarSearch(graph, start, end) {
        const startTime = performance.now();
        
        const openSet = [{node: start, g: 0, f: this.heuristic(start, end)}];
        const closedSet = new Set();
        const gScore = {[start]: 0};
        const previous = {};
        let nodesExplored = 0;
        
        while (openSet.length > 0) {
            // Sort by f score
            openSet.sort((a, b) => a.f - b.f);
            const current = openSet.shift();
            
            if (closedSet.has(current.node)) continue;
            
            closedSet.add(current.node);
            nodesExplored++;
            
            if (current.node === end) {
                break;
            }
            
            for (const neighbor of Object.keys(graph[current.node])) {
                if (closedSet.has(neighbor)) continue;
                
                const tentativeG = gScore[current.node] + graph[current.node][neighbor];
                
                if (tentativeG < (gScore[neighbor] || Infinity)) {
                    previous[neighbor] = current.node;
                    gScore[neighbor] = tentativeG;
                    const f = tentativeG + this.heuristic(neighbor, end);
                    openSet.push({node: neighbor, g: tentativeG, f: f});
                }
            }
        }
        
        // Reconstruct path
        const path = [];
        let current = end;
        while (current !== undefined) {
            path.unshift(current);
            current = previous[current];
        }
        
        const executionTime = (performance.now() - startTime).toFixed(2);
        
        return {
            path: path.length > 1 ? path : null,
            distance: gScore[end] || null,
            nodesExplored: nodesExplored,
            executionTime: parseFloat(executionTime)
        };
    }
    
    // Heuristic function for A* (Euclidean distance)
    heuristic(node1, node2) {
        const building1 = CampusData.buildings[node1];
        const building2 = CampusData.buildings[node2];
        
        if (!building1 || !building2) return 0;
        
        return CampusData.utils.calculateDistance(
            building1.coordinates,
            building2.coordinates
        );
    }
    
    // Normalize location name using campus data
    normalizeLocationName(locationName) {
        if (!locationName) return null;
        
        // Check if CampusData is available
        if (!CampusData || !CampusData.buildings) {
            console.error('CampusData not available in normalizeLocationName');
            return null;
        }
        
        // Direct match first
        if (CampusData.buildings[locationName]) {
            return locationName;
        }
        
        // Try case-insensitive match
        const buildingNames = Object.keys(CampusData.buildings);
        const match = buildingNames.find(name => 
            name.toLowerCase() === locationName.toLowerCase()
        );
        
        if (match) {
            return match;
        }
        
        console.error(`Building not found: "${locationName}". Available buildings:`, buildingNames);
        return null;
    }
    
    // Find path using saved campus tour route
    findPathUsingCampusTour(startLocation, endLocation, campusTour) {
        const start = this.normalizeLocationName(startLocation);
        const end = this.normalizeLocationName(endLocation);
        
        if (!start || !end || !campusTour.buildingOrder) {
            return null;
        }
        
        // Find start and end indices in the campus tour
        const startIndex = campusTour.buildingOrder.indexOf(start);
        const endIndex = campusTour.buildingOrder.indexOf(end);
        
        if (startIndex === -1 || endIndex === -1) {
            return null; // Buildings not in tour, fall back to normal pathfinding
        }
        
        // Extract the relevant portion of the campus tour
        let pathSegment;
        let segmentWaypoints;
        let distance = 0;
        
        if (startIndex <= endIndex) {
            // Forward direction through tour
            pathSegment = campusTour.buildingOrder.slice(startIndex, endIndex + 1);
            segmentWaypoints = campusTour.waypoints.slice(startIndex, endIndex + 1);
        } else {
            // Reverse direction through tour
            pathSegment = campusTour.buildingOrder.slice(endIndex, startIndex + 1).reverse();
            segmentWaypoints = campusTour.waypoints.slice(endIndex, startIndex + 1).reverse();
        }
        
        // Calculate distance for this segment
        for (let i = 0; i < segmentWaypoints.length - 1; i++) {
            const from = segmentWaypoints[i];
            const to = segmentWaypoints[i + 1];
            
            const R = 6371000; // Earth's radius in meters
            const dLat = (to[0] - from[0]) * Math.PI / 180;
            const dLon = (to[1] - from[1]) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                    Math.cos(from[0] * Math.PI / 180) * Math.cos(to[0] * Math.PI / 180) *
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            distance += R * c;
        }
        
        return {
            success: true,
            algorithm: 'Campus Tour Route',
            path: pathSegment,
            distance: Math.round(distance),
            walkingTime: CampusData.utils.calculateWalkingTime(distance),
            executionTime: 0.1,
            nodesExplored: pathSegment.length,
            isOptimal: true,
            steps: this.generateSteps(pathSegment),
            coordinates: segmentWaypoints,
            source: 'campus-tour'
        };
    }
    
    // Generate step-by-step directions
    generateSteps(path) {
        if (!path || path.length < 2) return [];
        
        const steps = [];
        
        for (let i = 0; i < path.length - 1; i++) {
            const from = path[i];
            const to = path[i + 1];
            const connection = CampusData.utils.getConnection(from, to);
            const distance = connection ? connection.distance : 0;
            
            steps.push({
                step: i + 1,
                from: from,
                to: to,
                instruction: `Walk from ${from} to ${to}`,
                distance: distance,
                formattedDistance: CampusData.utils.formatDistance(distance),
                walkingTime: CampusData.utils.calculateWalkingTime(distance)
            });
        }
        
        return steps;
    }
    
    // Get coordinates for path visualization
    getPathCoordinates(path) {
        if (!path) return [];
        
        return path.map(building => {
            const buildingData = CampusData.buildings[building];
            return buildingData ? buildingData.coordinates : null;
        }).filter(Boolean);
    }
    
    // Get available locations
    getAvailableLocations() {
        return CampusData.utils.getAllBuildingNames();
    }
    
    // Search locations
    searchLocations(query) {
        return CampusData.utils.searchBuildings(query);
    }
    
    // Get location details
    getLocationDetails(locationName) {
        const building = CampusData.utils.getBuildingByName(locationName);
        if (!building) return null;
        
        return {
            name: building.name,
            ...building.data,
            connections: CampusData.utils.getBuildingConnections(building.name),
            style: CampusData.utils.getBuildingStyle(building.name)
        };
    }
}

// Export the pathfinding engine
const pathfindingEngine = new PathfindingEngine();