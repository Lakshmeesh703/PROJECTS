// Map Manager for Chanakya University PathFinder
// Handles all map operations, markers, and interactive building placement

class MapManager {
    constructor(containerId) {
        this.containerId = containerId;
        this.map = null;
        this.markers = {};
        this.pathLayer = null;
        this.currentPath = null;
        this.isInitialized = false;
        this.showAllMarkers = true;
        this.animationInProgress = false;
        this.baseLayers = {};
        this.layerControl = null;
        this.currentBaseLayer = 'Esri Satellite';
        this.buildingPlacementMode = false;
        this.editMode = false;
        this.editModeActive = false;
        this.currentEditingBuilding = null;
        this.tempMarker = null;
        this.placementCallback = null;
        
        // Manual route creation properties
        this.manualRouteMode = false;
        this.manualWaypoints = [];
        this.manualRouteLayer = null;
        this.currentManualPath = null;
        
        // Initialize the map
        this.initializeMap();
    }
    
    // Initialize Leaflet map
    initializeMap() {
        try {
            // Create map instance with higher max zoom for precise building placement
            this.map = L.map(this.containerId, {
                center: CampusData.bounds.center,
                zoom: CampusData.bounds.zoom,
                minZoom: CampusData.bounds.minZoom,
                maxZoom: 22, // Increased from default to allow detailed satellite view
                zoomControl: true,
                attributionControl: true,
                doubleClickZoom: false // Disable for building placement
            });
            
            // Initialize base map layers
            this.initializeMapLayers();
            
            // Set Esri Satellite as default layer
            this.baseLayers['Esri Satellite'].addTo(this.map);
            
            // Add building placement controls
            this.addBuildingPlacementControls();
            
            // Add layer control
            this.layerControl = L.control.layers(this.baseLayers).addTo(this.map);
            
            // Create marker clusters group
            this.markerGroup = L.layerGroup().addTo(this.map);
            
            // Initialize path layer
            this.pathLayer = L.layerGroup().addTo(this.map);
            
            // Initialize manual route layer
            this.manualRouteLayer = L.layerGroup().addTo(this.map);
            
            // Wait for data manager to initialize, then add markers
            setTimeout(() => {
                this.addAllMarkers();
                // Add test marker to verify the system is working
                this.addTestMarker();
            }, 100);
            
            // Set map event listeners
            this.setupMapEvents();
            
            this.isInitialized = true;
            console.log('✅ Map initialized successfully');
            
        } catch (error) {
            console.error('❌ Map initialization failed:', error);
            this.showMapError();
        }
    }
    
    // Initialize different map layers including satellite imagery
    initializeMapLayers() {
        // 1. OpenStreetMap (Default)
        this.baseLayers['OpenStreetMap'] = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors | CU PathFinder',
            maxZoom: 19
        });
        
        // 2. Google Satellite (High Resolution)
        this.baseLayers['Google Satellite'] = L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
            attribution: '© Google Satellite Imagery | CU PathFinder',
            maxZoom: 20
        });
        
        // 3. Google Hybrid (Satellite + Labels)
        this.baseLayers['Google Hybrid'] = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
            attribution: '© Google Hybrid Imagery | CU PathFinder',
            maxZoom: 20
        });
        
        // 1. Esri World Imagery (High Quality Satellite) - PRIMARY DEFAULT
        this.baseLayers['Esri Satellite'] = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: '© Esri, Maxar, GeoEye, Earthstar Geographics | Chanakya University PathFinder',
            maxZoom: 22, // Maximum zoom for detailed building placement
            minZoom: 1,
            errorTileUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=' // Transparent fallback
        });
        
        // 5. ISRO Bhuvan (Indian Satellite Data - Real Chandrayaan imagery)
        this.baseLayers['ISRO Bhuvan'] = L.tileLayer('https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/gmaps?layers=rgb&zoom={z}&x={x}&y={y}&format=image/png', {
            attribution: '© ISRO Bhuvan - Indian Space Research Organisation | Real Chandrayaan Satellite Data',
            maxZoom: 18
        });
        
        // 5b. ISRO Bhuvan Hybrid (Satellite + Labels)
        this.baseLayers['ISRO Hybrid'] = L.tileLayer('https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/gmaps?layers=hybrid&zoom={z}&x={x}&y={y}&format=image/png', {
            attribution: '© ISRO Bhuvan Hybrid - Chandrayaan Satellite with Labels',
            maxZoom: 18
        });
        
        // 6. Mapbox Satellite (Professional Quality)
        // Note: Requires API key for production use
        this.baseLayers['Mapbox Satellite'] = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
            attribution: '© Mapbox Satellite | CU PathFinder',
            maxZoom: 19
        });
        
        // 7. CartoDB Positron (Clean minimal style)
        this.baseLayers['Minimal'] = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '© CartoDB | CU PathFinder',
            maxZoom: 18
        });
        
        // 8. OpenTopoMap (Topographical)
        this.baseLayers['Topographical'] = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenTopoMap (CC-BY-SA) | CU PathFinder',
            maxZoom: 17
        });
        
        console.log('🛰️ Enhanced satellite layers initialized with Esri Satellite as default');
        console.log('📍 Ready for precise building placement at zoom level 22');
    }
    
    // Add building placement controls to the map
    addBuildingPlacementControls() {
        const placementControl = L.control({ position: 'topright' });
        
        placementControl.onAdd = (map) => {
            const div = L.DomUtil.create('div', 'building-placement-controls');
            div.innerHTML = `
                <div class="placement-controls">
                    <button id="add-building-btn" class="control-btn" title="Add New Building">
                        <i class="fas fa-plus"></i> Add Building
                    </button>
                    <button id="edit-buildings-btn" class="control-btn" title="Edit Building Positions">
                        <i class="fas fa-edit"></i> Edit Positions
                    </button>
                    <button id="export-coords-btn" class="control-btn" title="Export Coordinates">
                        <i class="fas fa-download"></i> Export
                    </button>
                    <div id="building-form" class="building-form" style="display: none;">
                        <div class="form-header">
                            <h4>📍 Place New Building</h4>
                            <small>Click on the satellite map to place</small>
                        </div>
                        <input type="text" id="building-name-input" placeholder="Building Name (e.g., Main Library)" />
                        <select id="building-type-select">
                            <option value="academic">🏫 Academic Building</option>
                            <option value="hostel">🏠 Hostel/Dormitory</option>
                            <option value="admin">🏛️ Administrative</option>
                            <option value="sports">⚽ Sports Facility</option>
                            <option value="dining">🍽️ Dining/Cafeteria</option>
                            <option value="medical">🏥 Medical/Health</option>
                            <option value="library">📚 Library</option>
                            <option value="laboratory">🔬 Laboratory</option>
                            <option value="auditorium">🎭 Auditorium/Hall</option>
                            <option value="parking">🅿️ Parking</option>
                            <option value="gate">🚪 Gate/Entrance</option>
                            <option value="other">📍 Other</option>
                        </select>
                        <textarea id="building-description" placeholder="Building Description (optional)"></textarea>
                        <div class="coordinate-display" id="coordinate-display" style="display: none;">
                            <small>📍 Coordinates: <span id="coord-text"></span></small>
                        </div>
                        <div class="form-buttons">
                            <button id="save-building-btn" class="btn-save" disabled>
                                <i class="fas fa-save"></i> Save Building
                            </button>
                            <button id="cancel-building-btn" class="btn-cancel">
                                <i class="fas fa-times"></i> Cancel
                            </button>
                        </div>
                    </div>
                    <div id="placement-instructions" class="instructions" style="display: none;">
                        <div class="instruction-text">
                            <i class="fas fa-mouse-pointer"></i>
                            Click anywhere on the satellite map to place the building
                        </div>
                    </div>
                </div>
            `;
            
            // Prevent map events on control
            L.DomEvent.disableClickPropagation(div);
            L.DomEvent.disableScrollPropagation(div);
            
            return div;
        };
        
        placementControl.addTo(this.map);
        
        // Add event listeners for placement controls
        this.setupBuildingPlacementEvents();
    }
    
    // Setup building placement event listeners
    setupBuildingPlacementEvents() {
        // Add building button
        document.getElementById('add-building-btn').addEventListener('click', () => {
            this.startBuildingPlacement();
        });
        
        // Edit buildings button
        document.getElementById('edit-buildings-btn').addEventListener('click', () => {
            this.toggleEditMode();
        });
        
        // Export coordinates button
        document.getElementById('export-coords-btn').addEventListener('click', () => {
            this.exportBuildingCoordinates();
        });
        
        // Save building button
        document.getElementById('save-building-btn').addEventListener('click', () => {
            this.saveBuildingPlacement();
        });
        
        // Cancel building button
        document.getElementById('cancel-building-btn').addEventListener('click', () => {
            this.cancelBuildingPlacement();
        });
        
        // Building name input validation
        document.getElementById('building-name-input').addEventListener('input', () => {
            this.validateBuildingForm();
        });
    }
    
    // Start building placement mode
    startBuildingPlacement() {
        this.buildingPlacementMode = true;
        this.map.getContainer().style.cursor = 'crosshair';
        
        // Show building form and instructions
        document.getElementById('building-form').style.display = 'block';
        document.getElementById('placement-instructions').style.display = 'block';
        document.getElementById('add-building-btn').style.display = 'none';
        document.getElementById('edit-buildings-btn').style.display = 'none';
        document.getElementById('export-coords-btn').style.display = 'none';
        
        // Show success message
        this.showNotification('Building placement mode activated! Click on the satellite map to place a new building.', 'info');
        
        // Focus on building name input
        setTimeout(() => {
            document.getElementById('building-name-input').focus();
        }, 500);
        
        // Add click listener for placement
        this.map.on('click', this.onBuildingPlacementClick.bind(this));
        
        console.log('🏗️ Building placement mode activated');
    }
    
    // Handle building placement click
    onBuildingPlacementClick(e) {
        if (!this.buildingPlacementMode) return;
        
        const { lat, lng } = e.latlng;
        
        // Remove previous temp marker
        if (this.tempMarker) {
            this.map.removeLayer(this.tempMarker);
        }
        
        // Create temporary marker with pulsing animation
        this.tempMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'temp-building-marker',
                html: '<i class="fas fa-map-pin"></i>',
                iconSize: [30, 30],
                iconAnchor: [15, 30]
            })
        }).addTo(this.map);
        
        // Store coordinates
        this.tempCoordinates = [lat, lng];
        
        // Update coordinate display
        document.getElementById('coordinate-display').style.display = 'block';
        document.getElementById('coord-text').textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        
        // Validate form
        this.validateBuildingForm();
        
        // Hide instructions
        document.getElementById('placement-instructions').style.display = 'none';
        
        console.log(`📍 Building placement coordinates: ${lat.toFixed(6)}, ${lng.toFixed(6)}`);
    }
    
    // Validate building form
    validateBuildingForm() {
        const buildingName = document.getElementById('building-name-input').value.trim();
        const saveBtn = document.getElementById('save-building-btn');
        
        if (buildingName && this.tempCoordinates) {
            saveBtn.disabled = false;
            saveBtn.classList.add('enabled');
        } else {
            saveBtn.disabled = true;
            saveBtn.classList.remove('enabled');
        }
    }
    
    // Save building placement
    saveBuildingPlacement() {
        const buildingName = document.getElementById('building-name-input').value.trim();
        const buildingType = document.getElementById('building-type-select').value;
        const description = document.getElementById('building-description').value.trim();
        
        if (!buildingName) {
            this.showNotification('Please enter a building name', 'error');
            return;
        }
        
        if (!this.tempCoordinates) {
            this.showNotification('Please click on the map to select a location', 'error');
            return;
        }
        
        // Check if building name already exists
        if (CampusData.buildings[buildingName]) {
            if (!confirm(`A building named "${buildingName}" already exists. Do you want to replace it?`)) {
                return;
            }
        }
        
        // Create building data
        const buildingData = {
            coordinates: this.tempCoordinates,
            type: buildingType,
            description: description || `${buildingName} - ${this.getBuildingTypeLabel(buildingType)}`,
            facilities: this.getDefaultFacilities(buildingType),
            dateAdded: new Date().toISOString(),
            addedBy: 'Manual Placement'
        };
        
        // Add using data manager for consistent format
        const savedBuilding = dataManager.addBuilding(
            buildingName,
            this.tempCoordinates,
            buildingType,
            description || `${buildingName} - ${this.getBuildingTypeLabel(buildingType)}`
        );
        
        // Add marker to map
        this.addMarker(buildingName, savedBuilding);
        
        // Clean up
        this.cancelBuildingPlacement();
        
        // Show success message
        this.showNotification(`✅ Building "${buildingName}" added successfully!`, 'success');
        
        // Log detailed information
        console.log(`✅ New building added: ${buildingName}`);
        console.log(`📍 Coordinates: [${this.tempCoordinates[0].toFixed(6)}, ${this.tempCoordinates[1].toFixed(6)}]`);
        console.log(`🏢 Type: ${buildingType}`);
        console.log(`📝 Description: ${buildingData.description}`);
        console.log(`🏗️ Building data:`, buildingData);
        
        // Ask if user wants to add more buildings
        setTimeout(() => {
            if (confirm('Would you like to add another building?')) {
                this.startBuildingPlacement();
            }
        }, 1000);
    }
    
    // Cancel building placement
    cancelBuildingPlacement() {
        this.buildingPlacementMode = false;
        this.map.getContainer().style.cursor = '';
        
        // Remove temp marker
        if (this.tempMarker) {
            this.map.removeLayer(this.tempMarker);
            this.tempMarker = null;
        }
        
        // Hide building form and show buttons
        document.getElementById('building-form').style.display = 'none';
        document.getElementById('placement-instructions').style.display = 'none';
        document.getElementById('coordinate-display').style.display = 'none';
        document.getElementById('add-building-btn').style.display = 'inline-block';
        document.getElementById('edit-buildings-btn').style.display = 'inline-block';
        document.getElementById('export-coords-btn').style.display = 'inline-block';
        
        // Clear form
        document.getElementById('building-name-input').value = '';
        document.getElementById('building-description').value = '';
        document.getElementById('building-type-select').selectedIndex = 0;
        
        // Remove click listener
        this.map.off('click', this.onBuildingPlacementClick);
        
        this.tempCoordinates = null;
        
        console.log('❌ Building placement mode cancelled');
    }
    
    // Get building type label
    getBuildingTypeLabel(type) {
        const labels = {
            academic: 'Academic Building',
            hostel: 'Hostel/Dormitory',
            admin: 'Administrative Building',
            sports: 'Sports Facility',
            dining: 'Dining/Cafeteria',
            medical: 'Medical/Health Center',
            library: 'Library',
            laboratory: 'Laboratory',
            auditorium: 'Auditorium/Hall',
            parking: 'Parking Area',
            gate: 'Gate/Entrance',
            other: 'General Building'
        };
        return labels[type] || 'Building';
    }
    
    // Get default facilities based on building type
    getDefaultFacilities(type) {
        const facilityMap = {
            academic: ['Classrooms', 'Faculty Offices', 'Study Areas'],
            hostel: ['Dormitories', 'Common Room', 'Mess Hall', 'Recreation Area'],
            admin: ['Offices', 'Reception', 'Meeting Rooms', 'Records'],
            sports: ['Playing Area', 'Equipment Storage', 'Changing Rooms', 'Restrooms'],
            dining: ['Seating Area', 'Kitchen', 'Restrooms', 'Takeaway Counter'],
            medical: ['Consultation Rooms', 'First Aid', 'Pharmacy', 'Emergency Services'],
            library: ['Reading Halls', 'Book Collection', 'Study Rooms', 'Computer Lab'],
            laboratory: ['Lab Equipment', 'Research Areas', 'Storage', 'Safety Equipment'],
            auditorium: ['Main Hall', 'Stage', 'Sound System', 'Green Rooms'],
            parking: ['Vehicle Parking', 'Security', 'Lighting'],
            gate: ['Security Post', 'Barrier System', 'Visitor Registration'],
            other: ['Multi-purpose Space', 'General Facilities']
        };
        
        return facilityMap[type] || ['General Facilities'];
    }
    
    // Toggle edit mode for existing buildings
    toggleEditMode() {
        if (Object.keys(this.markers).length === 0) {
            this.showNotification('No buildings to edit. Use "Add Building" to place buildings first.', 'info');
            return;
        }
        
        if (this.editModeActive) {
            this.exitEditMode();
            return;
        }
        
        // Show building selection interface
        this.showBuildingSelector();
    }
    
    // Show building selector interface
    showBuildingSelector() {
        // Create selector modal
        const selectorHTML = `
            <div id="building-selector-modal" class="modal-overlay">
                <div class="modal-content">
                    <h3><i class="fas fa-edit"></i> Select Building to Edit</h3>
                    <p>Choose which building you want to move or reposition:</p>
                    <div class="building-list">
                        ${Object.entries(dataManager.getAllBuildings()).map(([buildingName, buildingData]) => `
                            <div class="building-item" onclick="mapManager.selectBuildingToEdit('${buildingName}')">
                                <i class="fas fa-building"></i>
                                <span>${buildingName}</span>
                                <small>(${buildingData.type || 'building'})</small>
                            </div>
                        `).join('')}
                    </div>
                    <div class="modal-buttons">
                        <button onclick="mapManager.cancelBuildingSelection()" class="btn-secondary">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.insertAdjacentHTML('beforeend', selectorHTML);
        
        // Add styles for the modal
        this.addBuildingSelectorStyles();
    }
    
    // Add styles for building selector
    addBuildingSelectorStyles() {
        if (!document.getElementById('building-selector-styles')) {
            const styles = document.createElement('style');
            styles.id = 'building-selector-styles';
            styles.textContent = `
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.7);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 10000;
                }
                .modal-content {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    max-width: 400px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                }
                .building-list {
                    max-height: 300px;
                    overflow-y: auto;
                    margin: 15px 0;
                }
                .building-item {
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    margin: 5px 0;
                    cursor: pointer;
                    transition: all 0.3s;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .building-item:hover {
                    background: #f0f8ff;
                    border-color: #3498db;
                    transform: translateX(5px);
                }
                .building-item i {
                    color: #3498db;
                }
                .building-item small {
                    color: #666;
                    margin-left: auto;
                }
                .modal-buttons {
                    display: flex;
                    justify-content: center;
                    gap: 10px;
                    margin-top: 15px;
                }
                .btn-secondary {
                    background: #95a5a6;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                }
            `;
            document.head.appendChild(styles);
        }
    }
    
    // Select a specific building to edit
    selectBuildingToEdit(buildingName) {
        this.cancelBuildingSelection();
        
        this.editModeActive = true;
        this.currentEditingBuilding = buildingName;
        
        // Update button text
        document.getElementById('edit-buildings-btn').innerHTML = '<i class="fas fa-check"></i> Exit Edit';
        document.getElementById('edit-buildings-btn').style.background = '#e74c3c';
        
        this.showNotification(`📝 Editing ${buildingName}. Drag the marker to reposition it.`, 'info');
        
        // Make only the selected building's marker draggable
        const marker = this.markers[buildingName];
        if (marker) {
            marker.dragging.enable();
            
            // Add visual indicator for draggable marker
            const markerElement = marker.getElement();
            if (markerElement) {
                markerElement.style.cursor = 'move';
                markerElement.style.transform = 'scale(1.1)';
                markerElement.style.boxShadow = '0 0 15px rgba(255, 193, 7, 0.8)';
            }
            
            marker.on('dragstart', (e) => {
                this.showNotification(`Moving ${buildingName}...`, 'info');
            });
            
            marker.on('dragend', (e) => {
                const marker = e.target;
                const position = marker.getLatLng();
                
                // Update building coordinates using data manager
                dataManager.updateBuildingPosition(buildingName, [position.lat, position.lng]);
                
                console.log(`📍 Moved ${buildingName} to: ${position.lat.toFixed(6)}, ${position.lng.toFixed(6)}`);
                this.showNotification(`✅ ${buildingName} moved to new position: ${position.lat.toFixed(6)}, ${position.lng.toFixed(6)}`, 'success');
            });
            
            // Center the map on the selected building
            const building = dataManager.getBuilding(buildingName);
            if (building) {
                this.map.panTo([building.coordinates[0], building.coordinates[1]]);
            }
        }
        
        console.log(`✏️ Edit mode activated for ${buildingName}`);
    }
    
    // Cancel building selection
    cancelBuildingSelection() {
        const modal = document.getElementById('building-selector-modal');
        if (modal) {
            modal.remove();
        }
    }
    
    // Exit edit mode
    exitEditMode() {
        this.editModeActive = false;
        this.currentEditingBuilding = null;
        
        // Update button text back to normal
        document.getElementById('edit-buildings-btn').innerHTML = '<i class="fas fa-edit"></i> Edit Positions';
        document.getElementById('edit-buildings-btn').style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
        
        // Disable dragging for all markers and reset styles
        Object.values(this.markers).forEach(marker => {
            marker.dragging.disable();
            marker.off('dragstart');
            marker.off('dragend');
            
            // Remove visual indicators
            const markerElement = marker.getElement();
            if (markerElement) {
                markerElement.style.cursor = 'pointer';
                markerElement.style.transform = 'scale(1)';
                markerElement.style.boxShadow = '0 2px 10px rgba(0,0,0,0.3)';
            }
        });
        
        this.showNotification('📝 Edit mode disabled', 'info');
        console.log('✏️ Edit mode deactivated - markers no longer draggable');
    }
    
    // Get building name for a marker
    getMarkerBuildingName(targetMarker) {
        for (const [buildingName, marker] of Object.entries(this.markers)) {
            if (marker === targetMarker) {
                return buildingName;
            }
        }
        return null;
    }
    
    // Export building coordinates to console and clipboard
    exportBuildingCoordinates() {
        const buildingCoords = {};
        
        for (const [name, data] of Object.entries(CampusData.buildings)) {
            buildingCoords[name] = {
                coordinates: data.coordinates,
                type: data.type,
                description: data.description
            };
        }
        
        const exportData = {
            exportDate: new Date().toISOString(),
            totalBuildings: Object.keys(buildingCoords).length,
            buildings: buildingCoords
        };
        
        const jsonString = JSON.stringify(exportData, null, 2);
        
        console.log('📋 Building Coordinates Export:');
        console.log(jsonString);
        
        // Copy to clipboard if available
        if (navigator.clipboard) {
            navigator.clipboard.writeText(jsonString).then(() => {
                this.showNotification('✅ Building coordinates exported and copied to clipboard!', 'success');
            }).catch(() => {
                this.showNotification('📋 Building coordinates exported to console', 'info');
            });
        } else {
            this.showNotification('📋 Building coordinates exported to console', 'info');
        }
        
        return exportData;
    }
    
    // Switch to satellite view
    switchToSatellite(layerName = 'Google Satellite') {
        if (this.baseLayers[layerName]) {
            // Remove current layer
            this.map.eachLayer((layer) => {
                if (layer.options && layer.options.attribution && layer.options.attribution.includes('©')) {
                    this.map.removeLayer(layer);
                }
            });
            
            // Add satellite layer
            this.baseLayers[layerName].addTo(this.map);
            this.currentBaseLayer = layerName;
            
            // Update UI if needed
            this.onLayerChange(layerName);
            
            console.log(`🛰️ Switched to ${layerName}`);
        }
    }
    
    // Switch to street view
    switchToStreet() {
        this.switchToSatellite('OpenStreetMap');
    }
    
    // Get available satellite layers
    getSatelliteLayers() {
        return Object.keys(this.baseLayers).filter(name => 
            name.includes('Satellite') || name.includes('Hybrid') || name.includes('Bhuvan') || name.includes('ISRO')
        );
    }
    
    // Handle layer change events
    onLayerChange(layerName) {
        // Update any UI elements that depend on current layer
        const satelliteBtn = document.getElementById('satellite-toggle-btn');
        if (satelliteBtn) {
            const isSatellite = layerName.includes('Satellite') || layerName.includes('Hybrid') || layerName.includes('Bhuvan') || layerName.includes('ISRO');
            satelliteBtn.innerHTML = isSatellite ? 
                '<i class="fas fa-map"></i>' : 
                '<i class="fas fa-satellite"></i>';
            satelliteBtn.title = isSatellite ? 'Switch to Street View' : 'Switch to Satellite View';
        }
        
        // Emit custom event
        document.dispatchEvent(new CustomEvent('mapLayerChanged', {
            detail: { layerName: layerName }
        }));
    }
    
    // Add all building markers to the map
    addAllMarkers() {
        console.log('🔍 Loading buildings from data manager...');
        const buildings = dataManager.getAllBuildings();
        console.log('📍 Buildings loaded:', Object.keys(buildings));
        
        if (Object.keys(buildings).length === 0) {
            console.log('⚠️ No buildings found in data manager');
            return;
        }
        
        for (const [buildingName, buildingData] of Object.entries(buildings)) {
            console.log(`📌 Adding marker for: ${buildingName}`, buildingData);
            this.addMarker(buildingName, buildingData);
        }
        
        console.log(`✅ Added ${Object.keys(buildings).length} building markers to map`);
    }
    
    // Add a single marker
    addMarker(buildingName, buildingData) {
        try {
            console.log(`🔧 Adding marker for ${buildingName}:`, buildingData);
            
            const style = CampusData.utils.getBuildingStyle(buildingName);
            console.log(`🎨 Style for ${buildingName}:`, style);
            
            const [lat, lng] = buildingData.coordinates;
            console.log(`📍 Coordinates for ${buildingName}: [${lat}, ${lng}]`);
            
            // Create custom icon
        const icon = L.divIcon({
            className: 'custom-marker',
            html: `
                <div class="marker-container" style="background-color: ${style.color}">
                    <i class="fas fa-${style.icon}"></i>
                    <div class="marker-label">${buildingName}</div>
                </div>
            `,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        // Create marker
        const marker = L.marker([lat, lng], { icon: icon });
        
        // Create popup content
        const popupContent = this.createPopupContent(buildingName, buildingData);
        marker.bindPopup(popupContent, {
            maxWidth: 300,
            className: 'custom-popup'
        });
        
        // Add click event
        marker.on('click', (e) => {
            this.onMarkerClick(buildingName, e);
        });
        
        // Store marker reference
        this.markers[buildingName] = marker;
        
        // Add to marker group
        marker.addTo(this.markerGroup);
        
        console.log(`✅ Successfully added marker for ${buildingName} to map`);
        
        } catch (error) {
            console.error(`❌ Error adding marker for ${buildingName}:`, error);
        }
    }
    
    // Create popup content for building
    createPopupContent(buildingName, buildingData) {
        const style = CampusData.utils.getBuildingStyle(buildingName);
        
        let facilitiesHtml = '';
        if (buildingData.facilities) {
            facilitiesHtml = `
                <div class="popup-facilities">
                    <strong>Facilities:</strong>
                    <ul>
                        ${buildingData.facilities.map(facility => `<li>${facility}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        let additionalInfo = '';
        if (buildingData.capacity) {
            additionalInfo += `<div class="popup-info"><strong>Capacity:</strong> ${buildingData.capacity}</div>`;
        }
        if (buildingData.floors) {
            additionalInfo += `<div class="popup-info"><strong>Floors:</strong> ${buildingData.floors}</div>`;
        }
        
        return `
            <div class="building-popup">
                <div class="popup-header" style="background-color: ${style.color}">
                    <i class="fas fa-${style.icon}"></i>
                    <h3>${buildingName}</h3>
                </div>
                <div class="popup-body">
                    <p class="popup-description">${buildingData.description}</p>
                    ${additionalInfo}
                    ${facilitiesHtml}
                    <div class="popup-actions">
                        <button class="popup-btn" onclick="mapManager.setAsStart('${buildingName}')">
                            <i class="fas fa-play"></i> Set as Start
                        </button>
                        <button class="popup-btn" onclick="mapManager.setAsDestination('${buildingName}')">
                            <i class="fas fa-flag"></i> Set as Destination
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Setup map event listeners
    setupMapEvents() {
        // Map click event
        this.map.on('click', (e) => {
            if (this.manualRouteMode) {
                this.addManualWaypoint(e.latlng);
            } else {
                this.clearHighlights();
            }
        });
        
        // Zoom event
        this.map.on('zoomend', () => {
            this.updateMarkerVisibility();
        });
        
        // Map ready event
        this.map.whenReady(() => {
            console.log('🗺️  Map is ready');
        });
    }
    
    // Display path on map with realistic cement road following
    displayPath(pathResult) {
        this.clearPath();
        
        if (!pathResult || !pathResult.path || pathResult.path.length < 2) {
            console.warn('Invalid path data provided');
            return;
        }
        
        this.currentPath = pathResult;
        
        // Generate realistic path coordinates following cement roads
        const realisticCoordinates = this.generateRealisticPath(pathResult.path);
        
        // Check if path display is enabled
        const showPath = document.getElementById('show-path-toggle')?.checked !== false;
        const showWaypoints = document.getElementById('show-waypoints-toggle')?.checked !== false;
        
        if (showPath) {
            // Create main path polyline (cement road style)
            const pathLine = L.polyline(realisticCoordinates, {
                color: '#2c5aa0',      // Road blue color
                weight: 8,             // Thicker to represent roads
                opacity: 0.8,
                lineCap: 'round',
                lineJoin: 'round'
            });
            
            // Add path border (road outline)
            const pathBorder = L.polyline(realisticCoordinates, {
                color: '#1a365d',      // Darker border
                weight: 10,
                opacity: 0.6,
                lineCap: 'round',
                lineJoin: 'round'
            });
            
            // Add border first, then main path
            pathBorder.addTo(this.pathLayer);
            pathLine.addTo(this.pathLayer);
            
            // Add walking direction arrows
            this.addDirectionArrows(realisticCoordinates);
        }
        
        // Add start and end markers
        this.addStartEndMarkers(pathResult);
        
        // Add waypoint markers if enabled
        if (showWaypoints) {
            this.addWaypointMarkers(realisticCoordinates);
        }
        
        // Fit map to path
        this.fitToPath(realisticCoordinates);
        
        console.log(`🛣️  Realistic cement path displayed: ${pathResult.path.join(' → ')}`);
    }
    
    // Generate realistic path coordinates following cement roads and walkways
    generateRealisticPath(buildingPath) {
        const coordinates = [];
        
        for (let i = 0; i < buildingPath.length - 1; i++) {
            const fromBuilding = buildingPath[i];
            const toBuilding = buildingPath[i + 1];
            
            // Get building coordinates
            const fromCoords = CampusData.buildings[fromBuilding]?.coordinates;
            const toCoords = CampusData.buildings[toBuilding]?.coordinates;
            
            if (!fromCoords || !toCoords) continue;
            
            // Add starting point
            if (i === 0) {
                coordinates.push(fromCoords);
            }
            
            // Find connection with waypoints
            const connection = CampusData.connections.find(conn => 
                (conn.from === fromBuilding && conn.to === toBuilding) ||
                (conn.from === toBuilding && conn.to === fromBuilding)
            );
            
            // Add waypoints if they exist (cement road points)
            if (connection && connection.waypoints) {
                const waypoints = connection.from === fromBuilding ? 
                    connection.waypoints : 
                    [...connection.waypoints].reverse();
                
                waypoints.forEach(waypoint => {
                    coordinates.push(waypoint);
                });
            } else {
                // If no waypoints, create curved path instead of straight line
                const curvedPath = this.createCurvedPath(fromCoords, toCoords);
                coordinates.push(...curvedPath);
            }
            
            // Add ending point
            coordinates.push(toCoords);
        }
        
        return coordinates;
    }
    
    // Create a curved path when no waypoints are available
    createCurvedPath(from, to) {
        const waypoints = [];
        const numPoints = 3; // Number of curve points
        
        for (let i = 1; i < numPoints; i++) {
            const ratio = i / numPoints;
            
            // Create slight curve by offsetting perpendicular to the line
            const lat = from[0] + (to[0] - from[0]) * ratio;
            const lng = from[1] + (to[1] - from[1]) * ratio;
            
            // Add small perpendicular offset for curve effect
            const offsetDistance = 0.0001; // Small offset
            const perpLat = lat + offsetDistance * Math.sin(ratio * Math.PI);
            const perpLng = lng + offsetDistance * Math.cos(ratio * Math.PI);
            
            waypoints.push([perpLat, perpLng]);
        }
        
        return waypoints;
    }
    
    // Add direction arrows along the path
    addDirectionArrows(coordinates) {
        if (coordinates.length < 2) return;
        
        for (let i = 1; i < coordinates.length; i += 3) { // Every 3rd point
            const from = coordinates[i - 1];
            const to = coordinates[i];
            
            // Calculate arrow position (midpoint)
            const arrowLat = (from[0] + to[0]) / 2;
            const arrowLng = (from[1] + to[1]) / 2;
            
            // Calculate rotation angle
            const angle = Math.atan2(to[0] - from[0], to[1] - from[1]) * 180 / Math.PI;
            
            // Create arrow marker
            const arrowIcon = L.divIcon({
                html: `<i class="fas fa-arrow-up" style="transform: rotate(${angle}deg); color: #2c5aa0; font-size: 12px;"></i>`,
                className: 'direction-arrow',
                iconSize: [16, 16],
                iconAnchor: [8, 8]
            });
            
            const arrowMarker = L.marker([arrowLat, arrowLng], { icon: arrowIcon });
            arrowMarker.addTo(this.pathLayer);
        }
    }
    
    // Add waypoint markers along the path
    addWaypointMarkers(coordinates) {
        coordinates.forEach((coord, index) => {
            if (index === 0 || index === coordinates.length - 1) return; // Skip start/end
            
            const waypointIcon = L.divIcon({
                html: `<div class="waypoint-marker">${index}</div>`,
                className: 'waypoint-icon',
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });
            
            const waypointMarker = L.marker(coord, { icon: waypointIcon });
            waypointMarker.addTo(this.pathLayer);
        });
    }
    
    // Fit map to path coordinates
    fitToPath(coordinates = null) {
        if (!coordinates && this.currentPath) {
            coordinates = this.currentPath.coordinates;
        }
        
        if (!coordinates || coordinates.length === 0) return;
        
        const group = new L.featureGroup(coordinates.map(coord => L.marker(coord)));
        this.map.fitBounds(group.getBounds().pad(0.1));
    }
    
    // Add start and end markers
    addStartEndMarkers(pathResult) {
        const path = pathResult.path;
        const coordinates = pathResult.coordinates;
        
        if (path.length < 2) return;
        
        // Start marker
        const startIcon = L.divIcon({
            className: 'path-marker start-marker',
            html: '<i class="fas fa-play-circle"></i>',
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });
        
        const startMarker = L.marker(coordinates[0], { icon: startIcon });
        startMarker.bindPopup(`<strong>Start:</strong> ${path[0]}`);
        startMarker.addTo(this.pathLayer);
        
        // End marker
        const endIcon = L.divIcon({
            className: 'path-marker end-marker',
            html: '<i class="fas fa-flag-checkered"></i>',
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });
        
        const endMarker = L.marker(coordinates[coordinates.length - 1], { icon: endIcon });
        endMarker.bindPopup(`<strong>Destination:</strong> ${path[path.length - 1]}`);
        endMarker.addTo(this.pathLayer);
    }
    
    // Add waypoint markers
    addWaypointMarkers(pathResult) {
        const path = pathResult.path;
        const coordinates = pathResult.coordinates;
        
        // Skip start and end points
        for (let i = 1; i < path.length - 1; i++) {
            const waypointIcon = L.divIcon({
                className: 'path-marker waypoint-marker',
                html: `<span>${i}</span>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });
            
            const waypointMarker = L.marker(coordinates[i], { icon: waypointIcon });
            waypointMarker.bindPopup(`<strong>Waypoint ${i}:</strong> ${path[i]}`);
            waypointMarker.addTo(this.pathLayer);
        }
    }
    
    // Animate path drawing
    animatePath(pathLine) {
        // Remove the path temporarily
        this.pathLayer.removeLayer(pathLine);
        
        // Get path coordinates
        const latlngs = pathLine.getLatLngs();
        
        // Create animated polyline
        const animatedPath = L.polyline([], {
            color: CampusData.defaultSettings.pathColor,
            weight: CampusData.defaultSettings.pathWeight + 2,
            opacity: 1,
            dashArray: '10, 5'
        }).addTo(this.pathLayer);
        
        // Animate drawing
        this.animationInProgress = true;
        let currentIndex = 0;
        
        const animateStep = () => {
            if (currentIndex < latlngs.length) {
                animatedPath.addLatLng(latlngs[currentIndex]);
                currentIndex++;
                setTimeout(animateStep, 200); // 200ms delay between points
            } else {
                this.animationInProgress = false;
                // Add the original path back
                pathLine.addTo(this.pathLayer);
                // Remove animated path
                this.pathLayer.removeLayer(animatedPath);
            }
        };
        
        animateStep();
    }
    
    // Clear current path
    clearPath() {
        if (this.pathLayer) {
            this.pathLayer.clearLayers();
        }
        this.currentPath = null;
    }
    
    // Draw path with custom styling (for saved routes)
    drawPath(coordinates, customStyle = {}) {
        if (!coordinates || coordinates.length < 2) {
            console.warn('Invalid coordinates provided for drawPath');
            return;
        }
        
        // Default style
        const defaultStyle = {
            color: '#2c5aa0',
            weight: 8,
            opacity: 0.8,
            lineCap: 'round',
            lineJoin: 'round'
        };
        
        // Merge custom style with defaults
        const style = { ...defaultStyle, ...customStyle };
        
        // Create path polyline
        const pathLine = L.polyline(coordinates, style);
        
        // Add border if not disabled
        if (style.showBorder !== false) {
            const borderStyle = {
                color: style.borderColor || '#1a365d',
                weight: (style.weight || 8) + 2,
                opacity: (style.opacity || 0.8) * 0.6,
                lineCap: 'round',
                lineJoin: 'round',
                dashArray: style.dashArray // Inherit dash pattern
            };
            
            const pathBorder = L.polyline(coordinates, borderStyle);
            pathBorder.addTo(this.pathLayer);
        }
        
        // Add main path
        pathLine.addTo(this.pathLayer);
        
        // Add direction arrows if enabled
        if (style.showArrows !== false) {
            this.addDirectionArrows(coordinates);
        }
        
        return pathLine;
    }
    
    // Fit map view to current path
    fitToPath() {
        if (this.currentPath && this.currentPath.coordinates) {
            const bounds = L.latLngBounds(this.currentPath.coordinates);
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }
    }
    
    // Highlight specific building
    highlightBuilding(buildingName) {
        this.clearHighlights();
        
        const marker = this.markers[buildingName];
        if (marker) {
            // Add highlight class
            const markerElement = marker.getElement();
            if (markerElement) {
                markerElement.classList.add('highlighted');
            }
            
            // Pan to marker
            this.map.setView(marker.getLatLng(), Math.max(this.map.getZoom(), 18));
            
            // Open popup
            marker.openPopup();
        }
    }
    
    // Clear all highlights
    clearHighlights() {
        Object.values(this.markers).forEach(marker => {
            const markerElement = marker.getElement();
            if (markerElement) {
                markerElement.classList.remove('highlighted');
            }
            marker.closePopup();
        });
    }
    
    // Toggle marker visibility
    toggleMarkers() {
        this.showAllMarkers = !this.showAllMarkers;
        
        if (this.showAllMarkers) {
            this.markerGroup.addTo(this.map);
        } else {
            this.map.removeLayer(this.markerGroup);
        }
        
        return this.showAllMarkers;
    }
    
    // Update marker visibility based on zoom level
    updateMarkerVisibility() {
        const currentZoom = this.map.getZoom();
        const showLabels = currentZoom >= 17;
        
        Object.values(this.markers).forEach(marker => {
            const markerElement = marker.getElement();
            if (markerElement) {
                const label = markerElement.querySelector('.marker-label');
                if (label) {
                    label.style.display = showLabels ? 'block' : 'none';
                }
            }
        });
    }
    
    // Center map on campus
    centerMap() {
        this.map.setView(CampusData.bounds.center, CampusData.bounds.zoom);
    }
    
    // Set building as start location
    setAsStart(buildingName) {
        const startSelect = document.getElementById('start-location');
        if (startSelect) {
            startSelect.value = buildingName;
            // Trigger change event
            startSelect.dispatchEvent(new Event('change'));
        }
        
        // Close any open popups
        this.map.closePopup();
        
        // Show notification
        this.showNotification(`Start location set to: ${buildingName}`, 'success');
    }
    
    // Set building as destination
    setAsDestination(buildingName) {
        const endSelect = document.getElementById('end-location');
        if (endSelect) {
            endSelect.value = buildingName;
            // Trigger change event
            endSelect.dispatchEvent(new Event('change'));
        }
        
        // Close any open popups
        this.map.closePopup();
        
        // Show notification
        this.showNotification(`Destination set to: ${buildingName}`, 'success');
    }
    
    // Show notification
    showNotification(message, type = 'info') {
        // This will be handled by the UI controller
        if (window.uiController) {
            window.uiController.showNotification(message, type);
        }
    }
    
    // Handle marker click events
    onMarkerClick(buildingName, event) {
        console.log(`📍 Clicked on: ${buildingName}`);
        
        // Highlight the clicked building
        this.highlightBuilding(buildingName);
        
        // Emit custom event for other components
        document.dispatchEvent(new CustomEvent('buildingSelected', {
            detail: { buildingName: buildingName }
        }));
    }
    
    // Show map error
    showMapError() {
        const mapContainer = document.getElementById(this.containerId);
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div class="map-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Map Loading Error</h3>
                    <p>Unable to load the campus map. Please check your internet connection and try again.</p>
                    <button onclick="location.reload()" class="btn btn-primary">
                        <i class="fas fa-refresh"></i> Retry
                    </button>
                </div>
            `;
        }
    }
    
    // Get current map bounds
    getBounds() {
        return this.map ? this.map.getBounds() : null;
    }
    
    // Get current zoom level
    getZoom() {
        return this.map ? this.map.getZoom() : null;
    }
    
    // Check if map is initialized
    isReady() {
        return this.isInitialized && this.map;
    }
    
    // Resize map (useful for responsive layouts)
    resize() {
        if (this.map) {
            setTimeout(() => {
                this.map.invalidateSize();
            }, 100);
        }
    }
    
    // Toggle fullscreen mode
    toggleFullscreen() {
        const mapContainer = document.getElementById(this.containerId);
        
        if (!document.fullscreenElement) {
            mapContainer.requestFullscreen().then(() => {
                setTimeout(() => this.resize(), 200);
            });
        } else {
            document.exitFullscreen().then(() => {
                setTimeout(() => this.resize(), 200);
            });
        }
    }
    
    // Export map as image (future feature)
    async exportMap() {
        // This would require additional libraries like html2canvas
        console.log('Map export feature - coming soon!');
    }
    
    // Test function to verify markers are working
    addTestMarker() {
        console.log('🧪 Adding test marker...');
        const testMarker = L.marker([13.2220167, 77.755403], {
            icon: L.divIcon({
                className: 'test-marker',
                html: '<div style="background: red; color: white; padding: 5px; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;">TEST</div>',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            })
        });
        
        testMarker.addTo(this.markerGroup);
        console.log('✅ Test marker added to map');
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.markerGroup.removeLayer(testMarker);
            console.log('🗑️ Test marker removed');
        }, 5000);
    }
}

// Add custom CSS for markers
const mapStyles = `
<style>
.custom-marker {
    background: none;
    border: none;
}

.marker-container {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 12px;
    border: 2px solid white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
}

.marker-container:hover {
    transform: scale(1.2);
}

.marker-container.highlighted {
    transform: scale(1.3);
    border-color: #ffff00;
    box-shadow: 0 0 20px rgba(255,255,0,0.5);
    animation: pulse 1s infinite;
}

.marker-label {
    position: absolute;
    top: 35px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.8);
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    white-space: nowrap;
    pointer-events: none;
    display: none;
}

.path-marker {
    background: none;
    border: none;
}

.start-marker {
    background: #27ae60;
    color: white;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 4px 15px rgba(39,174,96,0.4);
}

.end-marker {
    background: #e74c3c;
    color: white;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 4px 15px rgba(231,76,60,0.4);
}

.waypoint-marker {
    background: #667eea;
    color: white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    box-shadow: 0 2px 10px rgba(102,126,234,0.4);
}

.building-popup {
    min-width: 250px;
}

.popup-header {
    color: white;
    padding: 10px;
    margin: -10px -10px 10px -10px;
    border-radius: 4px 4px 0 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.popup-header h3 {
    margin: 0;
    font-size: 16px;
}

.popup-description {
    margin-bottom: 10px;
    color: #555;
    line-height: 1.4;
}

.popup-info {
    margin-bottom: 5px;
    font-size: 14px;
}

.popup-facilities ul {
    margin: 5px 0 10px 20px;
    font-size: 13px;
}

.popup-actions {
    display: flex;
    gap: 5px;
    margin-top: 10px;
}

.popup-btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
}

.popup-btn:hover {
    background: #5a67d8;
}

.map-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #7f8c8d;
    text-align: center;
    padding: 40px;
}

.map-error i {
    font-size: 4rem;
    margin-bottom: 20px;
    color: #e74c3c;
}

.map-error h3 {
    margin-bottom: 10px;
    color: #2c3e50;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255,255,0,0.7); }
    70% { box-shadow: 0 0 0 10px rgba(255,255,0,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,255,0,0); }
}
</style>
`;

// Enhanced CSS for building placement
const buildingPlacementStyles = `
<style>
/* Building Placement Controls */
.building-placement-controls {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    padding: 15px;
    margin: 10px;
    max-width: 320px;
}

.control-btn {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    cursor: pointer;
    margin: 3px;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.3s ease;
}

.control-btn:hover {
    background: linear-gradient(135deg, #5a67d8, #6b46c1);
    transform: translateY(-1px);
}

.building-form {
    margin-top: 15px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 2px solid #e9ecef;
}

.form-header {
    margin-bottom: 15px;
    text-align: center;
}

.form-header h4 {
    margin: 0 0 5px 0;
    color: #2c3e50;
    font-size: 16px;
}

.form-header small {
    color: #6c757d;
    font-style: italic;
}

.building-form input,
.building-form select,
.building-form textarea {
    width: 100%;
    padding: 10px;
    margin: 8px 0;
    border: 2px solid #dee2e6;
    border-radius: 6px;
    font-size: 13px;
    transition: border-color 0.3s ease;
    box-sizing: border-box;
}

.building-form input:focus,
.building-form select:focus,
.building-form textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.building-form textarea {
    height: 70px;
    resize: vertical;
}

.coordinate-display {
    background: #e7f3ff;
    padding: 8px 12px;
    border-radius: 6px;
    margin: 8px 0;
    border-left: 4px solid #0066cc;
}

.coordinate-display small {
    color: #0066cc;
    font-weight: 500;
}

.form-buttons {
    display: flex;
    gap: 8px;
    margin-top: 15px;
}

.btn-save {
    background: #6c757d;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    cursor: not-allowed;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.3s ease;
    opacity: 0.6;
}

.btn-save.enabled {
    background: #28a745;
    cursor: pointer;
    opacity: 1;
    box-shadow: 0 2px 10px rgba(40, 167, 69, 0.3);
}

.btn-save.enabled:hover {
    background: #218838;
    transform: translateY(-1px);
}

.btn-cancel {
    background: #dc3545;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    cursor: pointer;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.3s ease;
}

.btn-cancel:hover {
    background: #c82333;
    transform: translateY(-1px);
}

.instructions {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 6px;
    padding: 12px;
    margin-top: 10px;
    text-align: center;
}

.instruction-text {
    color: #856404;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.temp-building-marker {
    background: linear-gradient(135deg, #ff6b6b, #ee5a52);
    color: white;
    border-radius: 50% 50% 50% 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    transform: rotate(-45deg);
    border: 3px solid white;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    animation: pulse-temp 2s infinite;
}

.temp-building-marker i {
    transform: rotate(45deg);
    font-size: 14px;
}

@keyframes pulse-temp {
    0% { 
        transform: rotate(-45deg) scale(1);
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    50% { 
        transform: rotate(-45deg) scale(1.1);
        box-shadow: 0 6px 25px rgba(255, 107, 107, 0.6);
    }
    100% { 
        transform: rotate(-45deg) scale(1);
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
}
</style>
`;

// Inject enhanced styles
document.head.insertAdjacentHTML('beforeend', mapStyles);
document.head.insertAdjacentHTML('beforeend', buildingPlacementStyles);

// Add manual route methods to MapManager prototype
MapManager.prototype.enableManualRouteMode = function() {
    this.manualRouteMode = true;
    this.manualWaypoints = [];
    this.clearManualRoute();
    this.map.getContainer().style.cursor = 'crosshair';
    this.updateManualRouteStatus('Click on map to add waypoints', 0);
    console.log('🖱️ Manual route mode enabled');
};

MapManager.prototype.disableManualRouteMode = function() {
    this.manualRouteMode = false;
    this.map.getContainer().style.cursor = '';
    this.updateManualRouteStatus('Manual route mode disabled', this.manualWaypoints.length);
    console.log('🖱️ Manual route mode disabled');
};

MapManager.prototype.addManualWaypoint = function(latlng) {
    if (!this.manualRouteMode) return;
    
    const waypointIndex = this.manualWaypoints.length + 1;
    this.manualWaypoints.push(latlng);
    
    // Create waypoint marker
    const waypointIcon = L.divIcon({
        html: `<div class="manual-waypoint">${waypointIndex}</div>`,
        className: 'manual-waypoint-icon',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });
    
    const marker = L.marker(latlng, { 
        icon: waypointIcon,
        draggable: true
    });
    
    // Add click handler to remove waypoint
    marker.on('click', (e) => {
        e.originalEvent.stopPropagation();
        this.removeManualWaypoint(waypointIndex - 1);
    });
    
    // Add drag handler to update waypoint
    marker.on('dragend', (e) => {
        this.manualWaypoints[waypointIndex - 1] = e.target.getLatLng();
        this.updateManualRoutePath();
    });
    
    marker.addTo(this.manualRouteLayer);
    
    // Update path
    this.updateManualRoutePath();
    this.updateManualRouteStatus('Click on map to add more waypoints', this.manualWaypoints.length);
    
    // Show action buttons if we have at least 2 waypoints
    if (this.manualWaypoints.length >= 2) {
        this.showManualRouteActions();
    }
    
    console.log(`📍 Added waypoint ${waypointIndex} at`, latlng);
};

MapManager.prototype.removeManualWaypoint = function(index) {
    if (index < 0 || index >= this.manualWaypoints.length) return;
    
    this.manualWaypoints.splice(index, 1);
    this.redrawManualRoute();
    
    if (this.manualWaypoints.length < 2) {
        this.hideManualRouteActions();
    }
    
    console.log(`🗑️ Removed waypoint ${index + 1}`);
};

MapManager.prototype.updateManualRoutePath = function(customStyle = {}) {
    if (this.manualWaypoints.length < 2) return;
    
    // Clear existing path
    if (this.currentManualPath) {
        this.manualRouteLayer.removeLayer(this.currentManualPath);
    }
    
    // Default manual route style
    const defaultStyle = {
        color: '#e74c3c',
        weight: 6,
        opacity: 0.8,
        dashArray: '10, 5',
        lineCap: 'round',
        lineJoin: 'round'
    };
    
    // Merge custom style with defaults
    const style = { ...defaultStyle, ...customStyle };
    
    // Create new path
    const coordinates = this.manualWaypoints.map(wp => [wp.lat, wp.lng]);
    
    this.currentManualPath = L.polyline(coordinates, style);
    
    this.currentManualPath.addTo(this.manualRouteLayer);
};

MapManager.prototype.redrawManualRoute = function(customStyle = {}) {
    this.clearManualRoute();
    
    this.manualWaypoints.forEach((latlng, index) => {
        const waypointIcon = L.divIcon({
            html: `<div class="manual-waypoint">${index + 1}</div>`,
            className: 'manual-waypoint-icon',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        const marker = L.marker(latlng, { 
            icon: waypointIcon,
            draggable: true
        });
        
        marker.on('click', (e) => {
            e.originalEvent.stopPropagation();
            this.removeManualWaypoint(index);
        });
        
        marker.on('dragend', (e) => {
            this.manualWaypoints[index] = e.target.getLatLng();
            this.updateManualRoutePath(customStyle);
        });
        
        marker.addTo(this.manualRouteLayer);
    });
    
    this.updateManualRoutePath(customStyle);
    this.updateManualRouteStatus('Manual route updated', this.manualWaypoints.length);
};

MapManager.prototype.clearManualRoute = function() {
    this.manualRouteLayer.clearLayers();
    this.currentManualPath = null;
};

MapManager.prototype.finishManualRoute = function() {
    if (this.manualWaypoints.length < 2) {
        alert('Please add at least 2 waypoints to create a route');
        return null;
    }
    
    const routeData = {
        waypoints: this.manualWaypoints.map(wp => [wp.lat, wp.lng]),
        distance: this.calculateManualRouteDistance(),
        createdAt: new Date().toISOString(),
        type: 'manual'
    };
    
    this.disableManualRouteMode();
    this.updateManualRouteStatus('Manual route completed!', this.manualWaypoints.length);
    
    return routeData;
};

MapManager.prototype.calculateManualRouteDistance = function() {
    if (this.manualWaypoints.length < 2) return 0;
    
    let totalDistance = 0;
    for (let i = 0; i < this.manualWaypoints.length - 1; i++) {
        const from = this.manualWaypoints[i];
        const to = this.manualWaypoints[i + 1];
        
        // Calculate distance using Haversine formula
        const R = 6371000; // Earth's radius in meters
        const dLat = (to.lat - from.lat) * Math.PI / 180;
        const dLon = (to.lng - from.lng) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(from.lat * Math.PI / 180) * Math.cos(to.lat * Math.PI / 180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        totalDistance += R * c;
    }
    
    return Math.round(totalDistance);
};

MapManager.prototype.updateManualRouteStatus = function(message, waypointCount) {
    const statusElement = document.getElementById('manual-route-status');
    const countElement = document.getElementById('waypoint-count');
    
    if (statusElement) {
        statusElement.textContent = message;
    }
    
    if (countElement) {
        countElement.textContent = `${waypointCount} waypoint${waypointCount !== 1 ? 's' : ''}`;
    }
};

MapManager.prototype.showManualRouteActions = function() {
    const actionsElement = document.getElementById('manual-route-actions');
    if (actionsElement) {
        actionsElement.style.display = 'flex';
    }
};

MapManager.prototype.hideManualRouteActions = function() {
    const actionsElement = document.getElementById('manual-route-actions');
    if (actionsElement) {
        actionsElement.style.display = 'none';
    }
};

MapManager.prototype.displayManualRoute = function(routeData) {
    this.clearPath();
    this.clearManualRoute();
    
    if (!routeData.waypoints || routeData.waypoints.length < 2) return;
    
    // Set waypoints
    this.manualWaypoints = routeData.waypoints.map(coord => ({
        lat: coord[0],
        lng: coord[1]
    }));
    
    // Draw route with custom style if provided
    const customStyle = routeData.style || {};
    this.redrawManualRoute(customStyle);
    
    // Fit map to route
    const bounds = L.latLngBounds(this.manualWaypoints);
    this.map.fitBounds(bounds.pad(0.1));
    
    console.log('🗺️ Manual route displayed');
};