/**
 * Path Manager - Frontend Path Drawing and Saving
 * Allows users to draw custom paths on the map and save them to the backend
 */

class PathManager {
    constructor(mapManager) {
        this.mapManager = mapManager;
        this.isDrawing = false;
        this.currentPathCoordinates = [];
        this.pathMarkers = [];
        this.pathPolyline = null;
        this.savedPaths = [];
        this.apiUrl = 'http://localhost:5000/api';
        
        this.initialize();
    }
    
    // Initialize path manager
    initialize() {
        console.log('📍 Initializing Path Manager...');
        this.loadSavedPaths();
        this.setupUI();
    }
    
    // Setup UI elements for path drawing
    setupUI() {
        // Create path controls panel
        const controlPanel = `
            <div id="path-controls" class="path-controls-panel">
                <h3>🎯 Path Manager</h3>
                
                <div class="control-buttons">
                    <button id="btn-start-draw" class="btn btn-primary">
                        ✏️ Start Drawing Path
                    </button>
                    <button id="btn-clear-path" class="btn btn-secondary">
                        🗑️ Clear Path
                    </button>
                    <button id="btn-save-path" class="btn btn-success" disabled>
                        💾 Save Path
                    </button>
                </div>
                
                <div class="path-input-section">
                    <input type="text" id="path-name" placeholder="Enter path name..." 
                           class="path-input">
                    <textarea id="path-description" placeholder="Path description (optional)" 
                              class="path-input"></textarea>
                </div>
                
                <div id="path-info" class="path-info">
                    Points: <span id="point-count">0</span> | 
                    Distance: <span id="path-distance">0 km</span>
                </div>
                
                <div id="saved-paths-list" class="saved-paths-section">
                    <h4>📂 Saved Paths</h4>
                    <div id="paths-container" class="paths-container"></div>
                </div>
            </div>
        `;
        
        // Add control panel to map container
        const mapContainer = document.getElementById('campus-map');
        if (mapContainer) {
            mapContainer.insertAdjacentHTML('afterend', controlPanel);
            this.attachEventListeners();
        }
    }
    
    // Attach event listeners
    attachEventListeners() {
        const btnStartDraw = document.getElementById('btn-start-draw');
        const btnClearPath = document.getElementById('btn-clear-path');
        const btnSavePath = document.getElementById('btn-save-path');
        
        if (btnStartDraw) {
            btnStartDraw.addEventListener('click', () => this.toggleDrawMode());
        }
        
        if (btnClearPath) {
            btnClearPath.addEventListener('click', () => this.clearPath());
        }
        
        if (btnSavePath) {
            btnSavePath.addEventListener('click', () => this.savePath());
        }
        
        // Add click listener to map for drawing
        if (this.mapManager && this.mapManager.map) {
            this.mapManager.map.on('click', (e) => {
                if (this.isDrawing) {
                    this.addPointToPath(e.latlng);
                }
            });
        }
    }
    
    // Toggle drawing mode
    toggleDrawMode() {
        this.isDrawing = !this.isDrawing;
        const btn = document.getElementById('btn-start-draw');
        
        if (this.isDrawing) {
            btn.classList.add('active');
            btn.textContent = '⏸️ Stop Drawing';
            console.log('🎨 Drawing mode: ON - Click on map to add points');
            alert('Drawing mode active! Click on the map to add points to your path.');
        } else {
            btn.classList.remove('active');
            btn.textContent = '✏️ Start Drawing Path';
            console.log('🎨 Drawing mode: OFF');
        }
    }
    
    // Add a point to the current path
    addPointToPath(latlng) {
        const coordinate = {
            lat: latlng.lat,
            lng: latlng.lng
        };
        
        this.currentPathCoordinates.push(coordinate);
        
        // Add marker for this point
        const marker = L.circleMarker([latlng.lat, latlng.lng], {
            radius: 6,
            fillColor: '#FF6B6B',
            color: '#fff',
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.8
        }).addTo(this.mapManager.map)
         .bindPopup(`Point ${this.currentPathCoordinates.length}`);
        
        this.pathMarkers.push(marker);
        
        // Draw polyline if we have multiple points
        if (this.currentPathCoordinates.length > 1) {
            this.drawPathPolyline();
        }
        
        // Update UI
        this.updatePathInfo();
        document.getElementById('btn-save-path').disabled = false;
        
        console.log(`📍 Added point ${this.currentPathCoordinates.length}:`, coordinate);
    }
    
    // Draw polyline for the path
    drawPathPolyline() {
        if (this.pathPolyline) {
            this.mapManager.map.removeLayer(this.pathPolyline);
        }
        
        const latlngs = this.currentPathCoordinates.map(c => [c.lat, c.lng]);
        
        this.pathPolyline = L.polyline(latlngs, {
            color: '#FF6B6B',
            weight: 3,
            opacity: 0.8,
            smoothFactor: 1.0,
            dashArray: '5, 5'
        }).addTo(this.mapManager.map);
    }
    
    // Update path information display
    updatePathInfo() {
        const pointCount = this.currentPathCoordinates.length;
        const distance = this.calculatePathDistance();
        
        document.getElementById('point-count').textContent = pointCount;
        document.getElementById('path-distance').textContent = distance.toFixed(2) + ' km';
    }
    
    // Calculate total path distance
    calculatePathDistance() {
        let totalDistance = 0;
        
        for (let i = 0; i < this.currentPathCoordinates.length - 1; i++) {
            const coord1 = this.currentPathCoordinates[i];
            const coord2 = this.currentPathCoordinates[i + 1];
            totalDistance += this.getDistance(coord1, coord2);
        }
        
        return totalDistance;
    }
    
    // Calculate distance between two coordinates (Haversine formula)
    getDistance(coord1, coord2) {
        const R = 6371; // Earth's radius in km
        const dLat = (coord2.lat - coord1.lat) * Math.PI / 180;
        const dLng = (coord2.lng - coord1.lng) * Math.PI / 180;
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(coord1.lat * Math.PI / 180) * Math.cos(coord2.lat * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    // Clear current path
    clearPath() {
        this.isDrawing = false;
        this.currentPathCoordinates = [];
        
        // Remove markers
        this.pathMarkers.forEach(marker => {
            this.mapManager.map.removeLayer(marker);
        });
        this.pathMarkers = [];
        
        // Remove polyline
        if (this.pathPolyline) {
            this.mapManager.map.removeLayer(this.pathPolyline);
            this.pathPolyline = null;
        }
        
        // Reset UI
        document.getElementById('point-count').textContent = '0';
        document.getElementById('path-distance').textContent = '0 km';
        document.getElementById('btn-save-path').disabled = true;
        document.getElementById('btn-start-draw').classList.remove('active');
        document.getElementById('btn-start-draw').textContent = '✏️ Start Drawing Path';
        
        console.log('🗑️ Path cleared');
    }
    
    // Save path to backend
    async savePath() {
        if (this.currentPathCoordinates.length === 0) {
            alert('❌ Please draw a path first!');
            return;
        }
        
        const pathName = document.getElementById('path-name').value.trim();
        const description = document.getElementById('path-description').value.trim();
        
        if (!pathName) {
            alert('❌ Please enter a path name!');
            return;
        }
        
        try {
            console.log(`💾 Saving path: ${pathName}...`);
            
            const response = await fetch(`${this.apiUrl}/save-path`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: pathName,
                    coordinates: this.currentPathCoordinates,
                    description: description
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log('✅ Path saved successfully:', result.path);
                alert(`✅ Path "${pathName}" saved successfully!\nCoordinates: ${this.currentPathCoordinates.length}`);
                
                // Clear form and path
                document.getElementById('path-name').value = '';
                document.getElementById('path-description').value = '';
                this.clearPath();
                
                // Reload saved paths
                await this.loadSavedPaths();
            } else {
                console.error('❌ Error saving path:', result.error);
                alert(`❌ Error: ${result.error}`);
            }
        } catch (error) {
            console.error('❌ Error saving path:', error);
            alert(`❌ Error saving path: ${error.message}`);
        }
    }
    
    // Load saved paths from backend
    async loadSavedPaths() {
        try {
            console.log('📂 Loading saved paths...');
            
            const response = await fetch(`${this.apiUrl}/get-paths`);
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.savedPaths = result.paths;
                console.log(`✅ Loaded ${result.total_paths} saved paths`);
                this.displaySavedPaths();
            }
        } catch (error) {
            console.error('❌ Error loading saved paths:', error);
        }
    }
    
    // Display saved paths in UI
    displaySavedPaths() {
        const container = document.getElementById('paths-container');
        if (!container) return;
        
        if (this.savedPaths.length === 0) {
            container.innerHTML = '<p class="no-paths">No saved paths yet</p>';
            return;
        }
        
        let html = '';
        this.savedPaths.forEach(path => {
            html += `
                <div class="saved-path-item">
                    <div class="path-header">
                        <h5>${path.name}</h5>
                        <span class="path-points">${path.coordinate_count} points</span>
                    </div>
                    <p class="path-desc">${path.description || 'No description'}</p>
                    <div class="path-actions">
                        <button class="btn-small" onclick="pathManager.loadPath('${path.name}')">
                            📍 Load
                        </button>
                        <button class="btn-small btn-delete" onclick="pathManager.deletePath('${path.name}')">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    // Load a saved path onto the map
    async loadPath(pathName) {
        try {
            const response = await fetch(`${this.apiUrl}/get-path/${encodeURIComponent(pathName)}`);
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.clearPath();
                this.currentPathCoordinates = result.path.coordinates;
                
                // Redraw path on map
                this.pathMarkers = [];
                this.currentPathCoordinates.forEach((coord, index) => {
                    const marker = L.circleMarker([coord.lat, coord.lng], {
                        radius: 6,
                        fillColor: '#4ECDC4',
                        color: '#fff',
                        weight: 2,
                        opacity: 0.8,
                        fillOpacity: 0.8
                    }).addTo(this.mapManager.map)
                     .bindPopup(`${pathName} - Point ${index + 1}`);
                    
                    this.pathMarkers.push(marker);
                });
                
                this.drawPathPolyline();
                this.updatePathInfo();
                
                console.log(`✅ Loaded path: ${pathName}`);
                alert(`✅ Path "${pathName}" loaded!`);
            }
        } catch (error) {
            console.error('❌ Error loading path:', error);
            alert(`❌ Error loading path: ${error.message}`);
        }
    }
    
    // Delete a saved path
    async deletePath(pathName) {
        if (!confirm(`Are you sure you want to delete "${pathName}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/delete-path/${encodeURIComponent(pathName)}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log(`✅ Deleted path: ${pathName}`);
                alert(`✅ Path "${pathName}" deleted!`);
                await this.loadSavedPaths();
            } else {
                console.error('❌ Error deleting path:', result.error);
                alert(`❌ Error: ${result.error}`);
            }
        } catch (error) {
            console.error('❌ Error deleting path:', error);
            alert(`❌ Error deleting path: ${error.message}`);
        }
    }
}

// Initialize PathManager when available
console.log('📍 Path Manager script loaded');
