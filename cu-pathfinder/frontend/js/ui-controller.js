// UI Controller for CU PathFinder
// Manages all user interface interactions and state

class UIController {
    constructor() {
        this.currentPath = null;
        this.currentComparison = null;
        this.stops = [];
        this.isNavigating = false;
        
        // Initialize UI after DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }
    
    // Initialize all UI components
    initialize() {
        console.log('🎮 Initializing UI Controller...');
        
        // Populate location selects
        this.populateLocationSelects();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup chat interface
        this.setupChatInterface();
        
        // Update statistics
        this.updateStatistics();
        
        console.log('✅ UI Controller initialized');
    }
    
    // Populate location dropdown menus
    populateLocationSelects() {
        const startSelect = document.getElementById('start-location');
        const endSelect = document.getElementById('end-location');
        
        if (!startSelect || !endSelect) return;
        
        // Get buildings from data manager
        const buildings = Object.keys(dataManager.getAllBuildings());
        
        // Clear existing options (except placeholder)
        startSelect.innerHTML = '<option value="">Select starting location...</option>';
        endSelect.innerHTML = '<option value="">Select destination...</option>';
        
        // Group buildings by type for better organization
        const allBuildings = dataManager.getAllBuildings();
        const groupedBuildings = {};
        
        Object.entries(allBuildings).forEach(([name, data]) => {
            const type = data.type || 'other';
            if (!groupedBuildings[type]) {
                groupedBuildings[type] = [];
            }
            groupedBuildings[type].push(name);
        });
        
        // Add buildings to dropdowns, grouped by type
        Object.entries(groupedBuildings).forEach(([type, buildingList]) => {
            // Create optgroups for organization
            const startOptgroup = document.createElement('optgroup');
            startOptgroup.label = this.getTypeLabel(type);
            const endOptgroup = document.createElement('optgroup');
            endOptgroup.label = this.getTypeLabel(type);
            
            // Sort buildings alphabetically within each group
            buildingList.sort().forEach(building => {
                const startOption = document.createElement('option');
                startOption.value = building;
                startOption.textContent = building;
                startOptgroup.appendChild(startOption);
                
                const endOption = document.createElement('option');
                endOption.value = building;
                endOption.textContent = building;
                endOptgroup.appendChild(endOption);
            });
            
            startSelect.appendChild(startOptgroup);
            endSelect.appendChild(endOptgroup);
        });
        
        console.log(`📍 Populated ${buildings.length} locations in dropdowns`);
    }
    
    // Get user-friendly label for building type
    getTypeLabel(type) {
        const typeLabels = {
            'academic': '🎓 Academic Buildings',
            'entrance': '🚪 Gates & Entrances',
            'landmark': '🏛️ Landmarks',
            'hostel': '🏠 Residential',
            'dining': '🍽️ Food & Dining',
            'sports': '⚽ Sports & Recreation',
            'library': '📚 Library',
            'gate': '🚪 Gates',
            'other': '📍 Other Facilities'
        };
        return typeLabels[type] || `📍 ${type.charAt(0).toUpperCase() + type.slice(1)}`;
    }
    
    // Setup all event listeners
    setupEventListeners() {
        // Pathfinding buttons
        const findPathBtn = document.getElementById('find-path-btn');
        const clearBtn = document.getElementById('clear-path-btn');
        
        if (findPathBtn) {
            findPathBtn.addEventListener('click', () => this.handleFindPath());
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.handleClearPath());
        }
        
        // Path control buttons
        const savePathBtn = document.getElementById('save-path-btn');
        const loadPathsBtn = document.getElementById('load-paths-btn');
        const showPathToggle = document.getElementById('show-path-toggle');
        const showWaypointsToggle = document.getElementById('show-waypoints-toggle');
        
        if (savePathBtn) {
            savePathBtn.addEventListener('click', () => this.handleSavePath());
        }
        
        if (loadPathsBtn) {
            loadPathsBtn.addEventListener('click', () => this.handleLoadPaths());
        }
        
        if (showPathToggle) {
            showPathToggle.addEventListener('change', () => this.handleTogglePath());
        }
        
        if (showWaypointsToggle) {
            showWaypointsToggle.addEventListener('change', () => this.handleToggleWaypoints());
        }
        
        // Cement pathways control
        const showCementPathwaysToggle = document.getElementById('show-cement-pathways-toggle');
        if (showCementPathwaysToggle) {
            showCementPathwaysToggle.addEventListener('change', () => this.handleToggleCementPathways());
        }
        
        // Manual route controls
        const manualModeToggle = document.getElementById('manual-mode-toggle');
        const clearManualRouteBtn = document.getElementById('clear-manual-route-btn');
        const finishManualRouteBtn = document.getElementById('finish-manual-route-btn');
        const saveManualRouteBtn = document.getElementById('save-manual-route-btn');
        
        if (manualModeToggle) {
            manualModeToggle.addEventListener('change', () => this.handleToggleManualMode());
        }
        
        if (clearManualRouteBtn) {
            clearManualRouteBtn.addEventListener('click', () => this.handleClearManualRoute());
        }
        
        if (finishManualRouteBtn) {
            finishManualRouteBtn.addEventListener('click', () => this.handleFinishManualRoute());
        }
        
        if (saveManualRouteBtn) {
            saveManualRouteBtn.addEventListener('click', () => this.handleSaveManualRoute());
        }
        
        // Campus tour button
        const createCampusTourBtn = document.getElementById('create-campus-tour-btn');
        if (createCampusTourBtn) {
            createCampusTourBtn.addEventListener('click', () => this.handleCreateCampusTour());
        }
        
        // Stops management
        const addStopBtn = document.getElementById('add-stop-btn');
        if (addStopBtn) {
            addStopBtn.addEventListener('click', () => this.addStop());
        }
        
        // Map controls
        const centerMapBtn = document.getElementById('center-map-btn');
        const toggleMarkersBtn = document.getElementById('toggle-markers-btn');
        const fullscreenBtn = document.getElementById('fullscreen-btn');
        
        if (centerMapBtn) {
            centerMapBtn.addEventListener('click', () => {
                if (window.mapManager) {
                    window.mapManager.centerMap();
                }
            });
        }
        
        if (toggleMarkersBtn) {
            toggleMarkersBtn.addEventListener('click', () => {
                if (window.mapManager) {
                    const visible = window.mapManager.toggleMarkers();
                    toggleMarkersBtn.innerHTML = visible ? 
                        '<i class="fas fa-map-marker-alt"></i>' : 
                        '<i class="fas fa-eye-slash"></i>';
                }
            });
        }
        
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => {
                if (window.mapManager) {
                    window.mapManager.toggleFullscreen();
                }
            });
        }
        
        // Satellite controls
        const satelliteToggleBtn = document.getElementById('satellite-toggle-btn');
        const layersBtn = document.getElementById('layers-btn');
        const layersMenu = document.getElementById('layers-menu');
        
        if (satelliteToggleBtn) {
            satelliteToggleBtn.addEventListener('click', () => {
                this.toggleSatelliteView();
            });
        }
        
        if (layersBtn) {
            layersBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleLayersMenu();
            });
        }
        
        // Layer option clicks
        const layerOptions = document.querySelectorAll('.layer-option');
        layerOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                const layerName = e.currentTarget.getAttribute('data-layer');
                this.switchMapLayer(layerName);
            });
        });
        
        // Close layers menu when clicking outside
        document.addEventListener('click', (e) => {
            if (layersMenu && !layersMenu.contains(e.target) && !layersBtn.contains(e.target)) {
                layersMenu.classList.add('hidden');
            }
        });
        
        // Navigation panel controls
        const closeNavBtn = document.getElementById('close-nav-btn');
        const startNavBtn = document.getElementById('start-navigation-btn');
        
        if (closeNavBtn) {
            closeNavBtn.addEventListener('click', () => this.hideNavigationPanel());
        }
        
        if (startNavBtn) {
            startNavBtn.addEventListener('click', () => this.startNavigation());
        }
        
        // Modal controls
        const closeModalBtn = document.getElementById('close-modal-btn');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => this.hideComparisonModal());
        }
        
        // Close modal when clicking outside
        const modal = document.getElementById('comparison-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideComparisonModal();
                }
            });
        }
        
        // Location select changes
        const startSelect = document.getElementById('start-location');
        const endSelect = document.getElementById('end-location');
        
        if (startSelect) {
            startSelect.addEventListener('change', () => this.onLocationChange());
        }
        
        if (endSelect) {
            endSelect.addEventListener('change', () => this.onLocationChange());
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
        
        // Custom events
        document.addEventListener('buildingSelected', (e) => {
            this.onBuildingSelected(e.detail.buildingName);
        });
        
        console.log('🎯 Event listeners setup complete');
    }
    
    // Setup chat interface
    setupChatInterface() {
        const chatInput = document.getElementById('chat-input');
        const chatSendBtn = document.getElementById('chat-send-btn');
        const chatMessages = document.getElementById('chat-messages');
        
        if (!chatInput || !chatSendBtn || !chatMessages) return;
        
        // Send message function
        const sendMessage = async () => {
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Clear input
            chatInput.value = '';
            
            // Add user message to chat
            this.addChatMessage('user', message);
            
            // Show typing indicator
            this.showTypingIndicator();
            
            try {
                // Process message with chatbot
                const response = await chatBot.processMessage(message);
                
                // Remove typing indicator
                this.hideTypingIndicator();
                
                // Add bot response to chat
                this.addChatMessage('bot', response);
                
            } catch (error) {
                console.error('Chat error:', error);
                this.hideTypingIndicator();
                this.addChatMessage('bot', "I'm sorry, I encountered an error. Please try again.");
            }
        };
        
        // Event listeners
        chatSendBtn.addEventListener('click', sendMessage);
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Load initial bot message
        const history = chatBot.getHistory();
        if (history.length > 0) {
            history.forEach(msg => {
                this.addChatMessage(msg.sender, msg.content, false);
            });
        }
        
        console.log('💬 Chat interface setup complete');
    }
    
    // Update statistics display
    updateStatistics() {
        const totalLocations = document.getElementById('total-locations');
        const totalConnections = document.getElementById('total-connections');
        
        if (totalLocations) {
            totalLocations.textContent = Object.keys(CampusData.buildings).length;
        }
        
        if (totalConnections) {
            totalConnections.textContent = CampusData.connections.length;
        }
    }
    
    // Handle find path button click
    async handleFindPath() {
        const startSelect = document.getElementById('start-location');
        const endSelect = document.getElementById('end-location');
        
        const start = startSelect?.value;
        const end = endSelect?.value;
        const algorithm = 'A*'; // Fixed to A* algorithm
        
        if (!start || !end) {
            this.showNotification('Please select both start and end locations', 'warning');
            return;
        }
        
        if (start === end) {
            this.showNotification('Start and end locations cannot be the same', 'warning');
            return;
        }
        
        try {
            this.showLoading('Finding optimal path...');
            
            // Get stops
            const stops = this.getStops();
            
            // Find path using A* algorithm
            const result = await pathfindingEngine.findPath(start, end, stops);
            
            this.hideLoading();
            
            if (result.success) {
                // Display results
                this.displayPathResult(result);
                
                // Show on map
                if (window.mapManager) {
                    window.mapManager.displayPath(result);
                }
                
                // Show navigation panel
                this.showNavigationPanel(result);
                
                this.showNotification(`Path found! Distance: ${CampusData.utils.formatDistance(result.distance)}`, 'success');
            } else {
                this.showNotification('No path found between these locations', 'error');
            }
            
        } catch (error) {
            this.hideLoading();
            console.error('Pathfinding error:', error);
            this.showNotification('Error finding path: ' + error.message, 'error');
        }
    }
    
    // Handle clear path button click
    handleClearPath() {
        // Clear map
        if (window.mapManager) {
            window.mapManager.clearPath();
            window.mapManager.clearManualRoute();
            
            // Clear all routes if they exist
            if (window.mapManager.allRoutesLayer) {
                window.mapManager.map.removeLayer(window.mapManager.allRoutesLayer);
                window.mapManager.allRoutesLayer = null;
            }
        }
        
        // Clear results
        this.clearResults();
        
        // Hide navigation panel
        this.hideNavigationPanel();
        
        // Clear stops
        this.clearStops();
        
        // Reset current paths
        this.currentPath = null;
        this.currentManualRoute = null;
        
        // Hide save button
        const saveBtn = document.getElementById('save-manual-route-btn');
        if (saveBtn) {
            saveBtn.style.display = 'none';
        }
        
        this.showNotification('All paths and routes cleared', 'info');
    }
    
    // Display path result in UI
    displayPathResult(result) {
        const resultsContainer = document.getElementById('results-container');
        if (!resultsContainer) return;
        
        this.currentPath = result;
        
        const routeHtml = `
            <div class="route-result fade-in">
                <div class="route-header">
                    <h4><i class="fas fa-route"></i> Route Found</h4>
                    <span class="algorithm-badge">${result.algorithm}</span>
                </div>
                
                <div class="route-info">
                    <div class="info-item">
                        <div class="info-label">Distance</div>
                        <div class="info-value">${CampusData.utils.formatDistance(result.distance)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Walking Time</div>
                        <div class="info-value">${result.walkingTime}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Nodes Explored</div>
                        <div class="info-value">${result.nodesExplored}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Execution Time</div>
                        <div class="info-value">${result.executionTime}ms</div>
                    </div>
                </div>
                
                <div class="route-path">
                    <h4>Route Steps:</h4>
                    <div class="path-steps">
                        ${result.path.map((location, index) => `
                            <span class="path-step">${location}</span>
                            ${index < result.path.length - 1 ? '<span class="path-arrow">→</span>' : ''}
                        `).join('')}
                    </div>
                </div>
                
                <div class="route-actions">
                    <button class="btn btn-success" onclick="uiController.showNavigationPanel()">
                        <i class="fas fa-directions"></i> Start Navigation
                    </button>
                    <button class="btn btn-secondary" onclick="uiController.shareRoute()">
                        <i class="fas fa-share"></i> Share Route
                    </button>
                </div>
            </div>
        `;
        
        resultsContainer.innerHTML = routeHtml;
    }
    
    // Clear results display
    clearResults() {
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="result-placeholder">
                    <i class="fas fa-route"></i>
                    <p>Select start and end locations to find your path</p>
                </div>
            `;
        }
        this.currentPath = null;
    }
    
    // Show algorithm comparison modal
    showAlgorithmComparison(results) {
        const modal = document.getElementById('comparison-modal');
        const resultsContainer = document.getElementById('comparison-results');
        
        if (!modal || !resultsContainer) return;
        
        this.currentComparison = results;
        
        // Generate comparison table
        const tableHtml = `
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Algorithm</th>
                        <th>Distance</th>
                        <th>Nodes Explored</th>
                        <th>Execution Time</th>
                        <th>Optimal</th>
                    </tr>
                </thead>
                <tbody>
                    ${results.map(result => `
                        <tr>
                            <td><strong>${result.algorithm}</strong></td>
                            <td>${result.error ? 'Error' : CampusData.utils.formatDistance(result.distance)}</td>
                            <td>${result.error ? '-' : result.nodesExplored}</td>
                            <td>${result.error ? '-' : result.executionTime + 'ms'}</td>
                            <td>${result.error ? '-' : (result.isOptimal ? '<span class="optimal-badge">✓ Optimal</span>' : '❌')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        resultsContainer.innerHTML = tableHtml;
        modal.classList.remove('hidden');
    }
    
    // Hide algorithm comparison modal
    hideComparisonModal() {
        const modal = document.getElementById('comparison-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }
    
    // Show navigation panel
    showNavigationPanel(result = this.currentPath) {
        if (!result) return;
        
        const panel = document.getElementById('navigation-panel');
        if (!panel) return;
        
        // Update navigation data
        const navDistance = document.getElementById('nav-distance');
        const navTime = document.getElementById('nav-time');
        const navAlgorithm = document.getElementById('nav-algorithm');
        const navStepsList = document.getElementById('nav-steps-list');
        
        if (navDistance) navDistance.textContent = CampusData.utils.formatDistance(result.distance);
        if (navTime) navTime.textContent = result.walkingTime;
        if (navAlgorithm) navAlgorithm.textContent = result.algorithm;
        
        if (navStepsList && result.steps) {
            navStepsList.innerHTML = result.steps.map((step, index) => `
                <div class="nav-step">
                    <div class="step-number">${index + 1}</div>
                    <div class="step-text">${step.instruction}</div>
                </div>
            `).join('');
        }
        
        // Show panel
        panel.classList.remove('hidden');
    }
    
    // Hide navigation panel
    hideNavigationPanel() {
        const panel = document.getElementById('navigation-panel');
        if (panel) {
            panel.classList.add('hidden');
        }
    }
    
    // Start navigation mode
    startNavigation() {
        if (!this.currentPath) {
            this.showNotification('No route available for navigation', 'warning');
            return;
        }
        
        this.isNavigating = true;
        
        // Update button
        const startNavBtn = document.getElementById('start-navigation-btn');
        if (startNavBtn) {
            startNavBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Navigation';
            startNavBtn.onclick = () => this.stopNavigation();
        }
        
        this.showNotification('Navigation started! Follow the highlighted path.', 'success');
        
        // You could add GPS tracking, step-by-step guidance, etc. here
        console.log('🧭 Navigation started');
    }
    
    // Stop navigation mode
    stopNavigation() {
        this.isNavigating = false;
        
        // Update button
        const startNavBtn = document.getElementById('start-navigation-btn');
        if (startNavBtn) {
            startNavBtn.innerHTML = '<i class="fas fa-play"></i> Start Navigation';
            startNavBtn.onclick = () => this.startNavigation();
        }
        
        this.showNotification('Navigation stopped', 'info');
        console.log('🛑 Navigation stopped');
    }
    
    // Add intermediate stop
    addStop() {
        const stopsContainer = document.getElementById('stops-list');
        if (!stopsContainer) return;
        
        const stopIndex = this.stops.length;
        const stopId = `stop-${stopIndex}`;
        
        const stopHtml = `
            <div class="stop-item" data-stop-id="${stopId}">
                <select class="stop-select" data-stop-index="${stopIndex}">
                    <option value="">Select stop location...</option>
                    ${CampusData.utils.getAllBuildingNames().map(building => 
                        `<option value="${building}">${building}</option>`
                    ).join('')}
                </select>
                <button class="remove-stop-btn" onclick="uiController.removeStop('${stopId}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        stopsContainer.insertAdjacentHTML('beforeend', stopHtml);
        this.stops.push({ id: stopId, location: null });
        
        // Add event listener to new select
        const newSelect = stopsContainer.querySelector(`[data-stop-id="${stopId}"] .stop-select`);
        if (newSelect) {
            newSelect.addEventListener('change', (e) => {
                this.stops[stopIndex].location = e.target.value;
            });
        }
    }
    
    // Remove intermediate stop
    removeStop(stopId) {
        const stopElement = document.querySelector(`[data-stop-id="${stopId}"]`);
        if (stopElement) {
            stopElement.remove();
        }
        
        this.stops = this.stops.filter(stop => stop.id !== stopId);
    }
    
    // Get current stops
    getStops() {
        return this.stops.map(stop => stop.location).filter(Boolean);
    }
    
    // Clear all stops
    clearStops() {
        const stopsContainer = document.getElementById('stops-list');
        if (stopsContainer) {
            stopsContainer.innerHTML = '';
        }
        this.stops = [];
    }
    
    // Add message to chat
    addChatMessage(sender, content, scroll = true) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const messageHtml = `
            <div class="chat-message ${sender}-message fade-in">
                <div class="message-avatar">
                    <i class="fas fa-${sender === 'bot' ? 'robot' : 'user'}"></i>
                </div>
                <div class="message-content">
                    <p>${this.formatChatMessage(content)}</p>
                </div>
            </div>
        `;
        
        chatMessages.insertAdjacentHTML('beforeend', messageHtml);
        
        if (scroll) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // Format chat message content
    formatChatMessage(content) {
        return content
            .replace(/\\n/g, '<br>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/•/g, '<span style="margin-right: 8px;">•</span>')
            .replace(/🤖|🛣️|📏|🚶|🧠|📊|📍|🏆|✅|❌|🗺️|💬|🎯|🔍|⏱️|📈/g, '<span class="emoji">$&</span>');
    }
    
    // Show typing indicator
    showTypingIndicator() {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const typingHtml = `
            <div class="chat-message bot-message typing-indicator">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="typing-animation">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.insertAdjacentHTML('beforeend', typingHtml);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Hide typing indicator
    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Show loading overlay
    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            const messageElement = overlay.querySelector('p');
            if (messageElement) {
                messageElement.textContent = message;
            }
            overlay.classList.remove('hidden');
        }
    }
    
    // Hide loading overlay
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    // Show notification
    showNotification(message, type = 'info', duration = 4000) {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notificationId = 'notification-' + Date.now();
        const notificationHtml = `
            <div class="notification ${type}" id="${notificationId}">
                <div class="notification-header">
                    <h4 class="notification-title">${this.getNotificationTitle(type)}</h4>
                    <button class="notification-close" onclick="uiController.hideNotification('${notificationId}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <p class="notification-message">${message}</p>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', notificationHtml);
        
        // Show notification
        setTimeout(() => {
            const notification = document.getElementById(notificationId);
            if (notification) {
                notification.classList.add('show');
            }
        }, 100);
        
        // Auto-hide after duration
        setTimeout(() => {
            this.hideNotification(notificationId);
        }, duration);
    }
    
    // Hide notification
    hideNotification(notificationId) {
        const notification = document.getElementById(notificationId);
        if (notification) {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }
    
    // Get notification title by type
    getNotificationTitle(type) {
        const titles = {
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information'
        };
        return titles[type] || 'Notification';
    }
    
    // Handle location selection changes
    onLocationChange() {
        const startSelect = document.getElementById('start-location');
        const endSelect = document.getElementById('end-location');
        
        const start = startSelect?.value;
        const end = endSelect?.value;
        
        // Update chatbot context
        if (start || end) {
            chatBot.setContext({
                lastStart: start || chatBot.getContext().lastStart,
                lastEnd: end || chatBot.getContext().lastEnd
            });
        }
        
        // Enable/disable find path button
        const findPathBtn = document.getElementById('find-path-btn');
        const compareBtn = document.getElementById('compare-algorithms-btn');
        
        if (findPathBtn) {
            findPathBtn.disabled = !start || !end;
        }
        
        if (compareBtn) {
            compareBtn.disabled = !start || !end;
        }
    }
    
    // Handle building selection from map
    onBuildingSelected(buildingName) {
        console.log(`🏢 Building selected: ${buildingName}`);
        
        // You could implement quick actions here
        // For example, auto-fill the destination if only start is selected
        const startSelect = document.getElementById('start-location');
        const endSelect = document.getElementById('end-location');
        
        if (startSelect && endSelect) {
            if (!startSelect.value) {
                startSelect.value = buildingName;
                this.onLocationChange();
            } else if (!endSelect.value && startSelect.value !== buildingName) {
                endSelect.value = buildingName;
                this.onLocationChange();
            }
        }
    }
    
    // Handle keyboard shortcuts
    handleKeyboardShortcuts(event) {
        // Ctrl+Enter: Find path
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();
            this.handleFindPath();
        }
        
        // Escape: Clear path/close modals
        if (event.key === 'Escape') {
            const modal = document.getElementById('comparison-modal');
            if (modal && !modal.classList.contains('hidden')) {
                this.hideComparisonModal();
            } else {
                this.handleClearPath();
            }
        }
        
        // Ctrl+M: Toggle markers
        if (event.ctrlKey && event.key === 'm') {
            event.preventDefault();
            if (window.mapManager) {
                window.mapManager.toggleMarkers();
            }
        }
    }
    
    // Share route functionality
    shareRoute() {
        if (!this.currentPath) {
            this.showNotification('No route to share', 'warning');
            return;
        }
        
        const routeText = `CU PathFinder Route:\\n` +
                         `From: ${this.currentPath.path[0]}\\n` +
                         `To: ${this.currentPath.path[this.currentPath.path.length - 1]}\\n` +
                         `Distance: ${CampusData.utils.formatDistance(this.currentPath.distance)}\\n` +
                         `Walking Time: ${this.currentPath.walkingTime}\\n` +
                         `Algorithm: ${this.currentPath.algorithm}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'CU PathFinder Route',
                text: routeText
            });
        } else if (navigator.clipboard) {
            navigator.clipboard.writeText(routeText).then(() => {
                this.showNotification('Route copied to clipboard', 'success');
            });
        } else {
            this.showNotification('Sharing not supported', 'warning');
        }
    }
    
    // Toggle satellite view
    toggleSatelliteView() {
        if (!window.mapManager) return;
        
        const currentLayer = window.mapManager.currentBaseLayer;
        const isSatellite = currentLayer.includes('Satellite') || 
                           currentLayer.includes('Hybrid') || 
                           currentLayer.includes('Bhuvan') ||
                           currentLayer.includes('ISRO');
        
        if (isSatellite) {
            // Switch to street view
            window.mapManager.switchToStreet();
            this.showNotification('Switched to Street View', 'info', 2000);
        } else {
            // Switch to best satellite view
            window.mapManager.switchToSatellite('Google Satellite');
            this.showNotification('Switched to Satellite View', 'info', 2000);
        }
    }
    
    // Toggle layers menu
    toggleLayersMenu() {
        const layersMenu = document.getElementById('layers-menu');
        if (layersMenu) {
            layersMenu.classList.toggle('hidden');
        }
    }
    
    // Switch map layer
    switchMapLayer(layerName) {
        if (!window.mapManager || !layerName) return;
        
        // Switch the layer
        window.mapManager.switchToSatellite(layerName);
        
        // Update active state in menu
        const layerOptions = document.querySelectorAll('.layer-option');
        layerOptions.forEach(option => {
            option.classList.remove('active');
            if (option.getAttribute('data-layer') === layerName) {
                option.classList.add('active');
            }
        });
        
        // Hide menu
        const layersMenu = document.getElementById('layers-menu');
        if (layersMenu) {
            layersMenu.classList.add('hidden');
        }
        
        // Show notification based on layer type
        let message = `Switched to ${layerName}`;
        let type = 'info';
        
        if (layerName.includes('ISRO') || layerName.includes('Bhuvan')) {
            message = `🛰️ Now using ${layerName} - Real Indian satellite imagery from Chandrayaan mission!`;
            type = 'success';
        } else if (layerName.includes('Satellite')) {
            message = `🛰️ Switched to ${layerName} satellite view`;
            type = 'info';
        }
        
        this.showNotification(message, type, 3000);
        
        console.log(`🗺️ Switched to map layer: ${layerName}`);
    }
    
    // Get current UI state
    getState() {
        return {
            currentPath: this.currentPath,
            currentComparison: this.currentComparison,
            stops: this.stops,
            isNavigating: this.isNavigating
        };
    }
    
    // Set UI state
    setState(state) {
        this.currentPath = state.currentPath || null;
        this.currentComparison = state.currentComparison || null;
        this.stops = state.stops || [];
        this.isNavigating = state.isNavigating || false;
    }
    
    // Handle save path button click
    handleSavePath() {
        if (!this.currentPath) {
            this.showNotification('No path to save! Find a path first.', 'warning');
            return;
        }
        
        const pathName = prompt('Enter a name for this path:', 
            `Path from ${this.currentPath.path[0]} to ${this.currentPath.path[this.currentPath.path.length - 1]}`);
        
        if (!pathName) return;
        
        const savedPaths = JSON.parse(localStorage.getItem('cuPathfinderSavedPaths') || '[]');
        
        const pathData = {
            id: Date.now(),
            name: pathName,
            path: this.currentPath.path,
            distance: this.currentPath.distance,
            algorithm: this.currentPath.algorithm,
            savedAt: new Date().toISOString(),
            coordinates: this.currentPath.coordinates
        };
        
        savedPaths.push(pathData);
        localStorage.setItem('cuPathfinderSavedPaths', JSON.stringify(savedPaths));
        
        this.showNotification(`Path "${pathName}" saved successfully!`, 'success');
        
        // Auto-follow: Keep the saved route displayed on the map
        // Instead of clearing and redrawing, just update the style of the existing path
        if (window.mapManager && this.currentPath && this.currentPath.coordinates) {
            try {
                console.log('🔵 Attempting to save path with auto-follow styling');
                console.log('Coordinates length:', this.currentPath.coordinates.length);
                
                // Create a new styled path for the saved route
                const savedPathStyle = {
                    color: '#2563eb',
                    weight: 4,
                    opacity: 0.8,
                    dashArray: '8, 4' // Dashed line to indicate saved route
                };
                
                // Temporarily store current path info
                const tempPath = { ...this.currentPath };
                
                // Clear existing path
                window.mapManager.clearPath();
                
                // Draw the saved path with custom styling
                const drawnPath = window.mapManager.drawPath(tempPath.coordinates, savedPathStyle);
                
                if (drawnPath) {
                    console.log('🔵 Saved path displayed with dashed styling');
                } else {
                    console.warn('❌ Failed to draw saved path');
                }
                
                // Restore current path for UI consistency
                this.currentPath = tempPath;
                
            } catch (error) {
                console.error('❌ Error in auto-follow path display:', error);
            }
        } else {
            console.warn('⚠️ Cannot display saved path - missing mapManager or coordinates');
        }
    }
    
    // Handle load paths button click
    handleLoadPaths() {
        const savedPaths = JSON.parse(localStorage.getItem('cuPathfinderSavedPaths') || '[]');
        const manualRoutes = JSON.parse(localStorage.getItem('manualRoutes') || '[]');
        
        if (savedPaths.length === 0 && manualRoutes.length === 0) {
            this.showNotification('No saved paths or routes found.', 'info');
            return;
        }
        
        // Create and show modal with both saved paths and manual routes
        this.showSavedPathsModal(savedPaths, manualRoutes);
    }
    
    // Show modal with saved paths and manual routes
    showSavedPathsModal(savedPaths, manualRoutes = []) {
        const modalHtml = `
            <div class="modal" id="saved-paths-modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3><i class="fas fa-folder-open"></i> Saved Paths & Routes</h3>
                        <div class="modal-header-actions">
                            <button class="btn btn-success btn-small" id="save-all-routes-btn">
                                <i class="fas fa-save"></i> Save All Routes
                            </button>
                            <button class="btn btn-primary btn-small" id="mark-all-routes-btn">
                                <i class="fas fa-check-double"></i> Mark All
                            </button>
                            <button class="close-btn" onclick="document.getElementById('saved-paths-modal').remove()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="modal-body">
                        ${savedPaths.length > 0 ? `
                        <h4><i class="fas fa-route"></i> AI Generated Paths</h4>
                        <div class="saved-paths-list">
                            ${savedPaths.map(path => `
                                <div class="saved-path-item" data-path-id="${path.id}" data-path-type="ai">
                                    <div class="path-info">
                                        <h4>${path.name} <span class="badge-ai">AI</span></h4>
                                        <p><strong>Route:</strong> ${path.path.join(' → ')}</p>
                                        <p><strong>Distance:</strong> ${CampusData.utils.formatDistance(path.distance)}</p>
                                        <p><strong>Saved:</strong> ${new Date(path.savedAt).toLocaleDateString()}</p>
                                    </div>
                                    <div class="path-actions">
                                        <button class="btn btn-primary btn-small load-path-btn" data-path-id="${path.id}" data-path-type="ai">
                                            <i class="fas fa-route"></i> Load
                                        </button>
                                        <button class="btn btn-danger btn-small delete-path-btn" data-path-id="${path.id}" data-path-type="ai">
                                            <i class="fas fa-trash"></i> Delete
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        ` : ''}
                        
                        ${manualRoutes.length > 0 ? `
                        <h4><i class="fas fa-pencil-alt"></i> Manual Routes</h4>
                        <div class="saved-paths-list">
                            ${manualRoutes.map(route => `
                                <div class="saved-path-item" data-path-id="${route.id}" data-path-type="manual">
                                    <div class="path-info">
                                        <h4>${route.name} <span class="badge-manual">Manual</span></h4>
                                        <p><strong>Waypoints:</strong> ${route.waypoints.length} points</p>
                                        <p><strong>Distance:</strong> ${this.formatDistance(route.distance)}</p>
                                        <p><strong>Created:</strong> ${new Date(route.createdAt).toLocaleDateString()}</p>
                                    </div>
                                    <div class="path-actions">
                                        <button class="btn btn-primary btn-small load-manual-btn" data-path-id="${route.id}">
                                            <i class="fas fa-map"></i> Load
                                        </button>
                                        <button class="btn btn-danger btn-small delete-manual-btn" data-path-id="${route.id}">
                                            <i class="fas fa-trash"></i> Delete
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Add event listeners for AI path buttons
        document.querySelectorAll('.load-path-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const pathId = parseInt(e.target.closest('.load-path-btn').dataset.pathId);
                this.loadSavedPath(pathId);
                document.getElementById('saved-paths-modal').remove();
            });
        });
        
        document.querySelectorAll('.delete-path-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const pathId = parseInt(e.target.closest('.delete-path-btn').dataset.pathId);
                this.deleteSavedPath(pathId);
                // Refresh modal
                document.getElementById('saved-paths-modal').remove();
                this.handleLoadPaths();
            });
        });
        
        // Add event listeners for manual route buttons
        document.querySelectorAll('.load-manual-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const routeId = e.target.closest('.load-manual-btn').dataset.pathId;
                this.loadManualRoute(routeId);
                document.getElementById('saved-paths-modal').remove();
            });
        });
        
        document.querySelectorAll('.delete-manual-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const routeId = e.target.closest('.delete-manual-btn').dataset.pathId;
                this.deleteManualRoute(routeId);
                // Refresh modal
                document.getElementById('saved-paths-modal').remove();
                this.handleLoadPaths();
            });
        });
        
        // Add event listeners for bulk actions
        const saveAllBtn = document.getElementById('save-all-routes-btn');
        const markAllBtn = document.getElementById('mark-all-routes-btn');
        
        if (saveAllBtn) {
            saveAllBtn.addEventListener('click', () => {
                this.handleSaveAllRoutes();
            });
        }
        
        if (markAllBtn) {
            markAllBtn.addEventListener('click', () => {
                this.handleMarkAllRoutes();
            });
        }
    }
    
    // Load a saved path
    loadSavedPath(pathId) {
        const savedPaths = JSON.parse(localStorage.getItem('cuPathfinderSavedPaths') || '[]');
        const path = savedPaths.find(p => p.id === pathId);
        
        if (!path) {
            this.showNotification('Path not found!', 'error');
            return;
        }
        
        // Set the dropdowns
        document.getElementById('start-location').value = path.path[0];
        document.getElementById('end-location').value = path.path[path.path.length - 1];
        
        // Display the path
        this.currentPath = path;
        this.displayPathResult(path);
        
        if (window.mapManager) {
            window.mapManager.displayPath(path);
        }
        
        this.showNotification(`Loaded path: ${path.name}`, 'success');
    }
    
    // Delete a saved path
    deleteSavedPath(pathId) {
        const savedPaths = JSON.parse(localStorage.getItem('cuPathfinderSavedPaths') || '[]');
        const filteredPaths = savedPaths.filter(p => p.id !== pathId);
        localStorage.setItem('cuPathfinderSavedPaths', JSON.stringify(filteredPaths));
        this.showNotification('Path deleted!', 'info');
    }
    
    // Handle toggle path visibility
    handleTogglePath() {
        if (this.currentPath && window.mapManager) {
            window.mapManager.displayPath(this.currentPath);
        }
    }
    
    // Handle toggle waypoints visibility
    handleToggleWaypoints() {
        if (this.currentPath && window.mapManager) {
            window.mapManager.displayPath(this.currentPath);
        }
    }
    
    // Handle toggle cement pathways visibility
    handleToggleCementPathways() {
        const toggle = document.getElementById('show-cement-pathways-toggle');
        
        if (window.mapManager) {
            window.mapManager.toggleCementPathways(toggle.checked);
            
            if (toggle.checked) {
                this.showNotification('🛣️ Cement pathways are now visible', 'success');
            } else {
                this.showNotification('🛣️ Cement pathways are hidden', 'info');
            }
        }
    }
    
    // Manual route handlers
    handleToggleManualMode() {
        const toggle = document.getElementById('manual-mode-toggle');
        const controlsContainer = document.querySelector('.manual-route-controls');
        
        if (toggle.checked) {
            if (window.mapManager) {
                window.mapManager.enableManualRouteMode();
                controlsContainer.classList.add('active');
                this.showNotification('Manual route mode enabled. Click on map to add waypoints.', 'info');
            }
        } else {
            if (window.mapManager) {
                window.mapManager.disableManualRouteMode();
                controlsContainer.classList.remove('active');
                this.showNotification('Manual route mode disabled.', 'info');
            }
        }
    }
    
    handleClearManualRoute() {
        if (window.mapManager) {
            window.mapManager.clearManualRoute();
            window.mapManager.manualWaypoints = [];
            window.mapManager.hideManualRouteActions();
            window.mapManager.updateManualRouteStatus('Click on map to add waypoints', 0);
            this.showNotification('Manual route cleared.', 'info');
        }
    }
    
    handleFinishManualRoute() {
        if (!window.mapManager) return;
        
        const routeData = window.mapManager.finishManualRoute();
        if (routeData) {
            this.currentManualRoute = routeData;
            
            // Update toggle
            const toggle = document.getElementById('manual-mode-toggle');
            const controlsContainer = document.querySelector('.manual-route-controls');
            toggle.checked = false;
            controlsContainer.classList.remove('active');
            
            // Show save button
            const saveBtn = document.getElementById('save-manual-route-btn');
            if (saveBtn) {
                saveBtn.style.display = 'inline-flex';
            }
            
            this.showNotification(`Manual route completed! Distance: ${this.formatDistance(routeData.distance)}`, 'success');
        }
    }
    
    handleSaveManualRoute() {
        if (!this.currentManualRoute) {
            this.showNotification('No manual route to save. Create a manual route first by enabling "Create Route" mode and clicking on the map.', 'warning');
            return;
        }
        
        const name = prompt('Enter a name for this route:');
        if (!name) return;
        
        // Save to local storage
        const savedRoutes = JSON.parse(localStorage.getItem('manualRoutes') || '[]');
        const routeToSave = {
            ...this.currentManualRoute,
            name: name,
            id: Date.now().toString()
        };
        
        savedRoutes.push(routeToSave);
        localStorage.setItem('manualRoutes', JSON.stringify(savedRoutes));
        
        this.showNotification(`Manual route "${name}" saved successfully!`, 'success');
        
        // Auto-follow: Keep the saved manual route displayed on the map
        // Redraw the route with a style indicating it's saved
        if (window.mapManager && this.currentManualRoute && this.currentManualRoute.waypoints) {
            try {
                console.log('🔴 Attempting to save manual route with auto-follow styling');
                console.log('Waypoints length:', this.currentManualRoute.waypoints.length);
                
                const savedRouteStyle = {
                    color: '#dc2626',
                    weight: 4,
                    opacity: 0.8,
                    dashArray: '10, 5' // Dashed line to indicate saved route
                };
                
                // Temporarily store current route info
                const tempRoute = { ...this.currentManualRoute };
                
                // Clear existing route
                window.mapManager.clearManualRoute();
                
                // Restore waypoints and redraw with saved styling
                this.currentManualRoute = tempRoute;
                window.mapManager.manualWaypoints = tempRoute.waypoints.map(coord => ({
                    lat: coord[0],
                    lng: coord[1]
                }));
                
                // Redraw with saved styling
                window.mapManager.redrawManualRoute(savedRouteStyle);
                
                console.log('🔴 Manual route displayed with dashed styling');
                
            } catch (error) {
                console.error('❌ Error in auto-follow manual route display:', error);
            }
        } else {
            console.warn('⚠️ Cannot display saved manual route - missing mapManager or waypoints');
        }
        
        // Hide save button but keep the route reference for continued interaction
        const saveBtn = document.getElementById('save-manual-route-btn');
        if (saveBtn) {
            saveBtn.style.display = 'none';
        }
        
        // Keep the current manual route so it remains interactive
        // Don't set this.currentManualRoute = null;
    }
    
    // Load manual route from storage
    loadManualRoute(routeId) {
        const manualRoutes = JSON.parse(localStorage.getItem('manualRoutes') || '[]');
        const route = manualRoutes.find(r => r.id === routeId);
        
        if (!route) {
            this.showNotification('Manual route not found!', 'error');
            return;
        }
        
        if (window.mapManager) {
            window.mapManager.displayManualRoute(route);
            this.showNotification(`Loaded manual route: ${route.name}`, 'success');
        }
    }
    
    // Delete manual route from storage
    deleteManualRoute(routeId) {
        if (!confirm('Are you sure you want to delete this manual route?')) return;
        
        const manualRoutes = JSON.parse(localStorage.getItem('manualRoutes') || '[]');
        const filteredRoutes = manualRoutes.filter(r => r.id !== routeId);
        
        localStorage.setItem('manualRoutes', JSON.stringify(filteredRoutes));
        this.showNotification('Manual route deleted!', 'info');
    }
    
    // Handle campus tour creation
    handleCreateCampusTour() {
        const confirmed = confirm('This will create a comprehensive campus tour route covering all major buildings. Continue?');
        if (!confirmed) return;
        
        this.showLoading('Creating comprehensive campus tour route...');
        
        try {
            // Generate optimal campus tour route
            const campusTourRoute = this.generateCampusTourRoute();
            
            // Ask user for confirmation to save
            setTimeout(() => {
                this.hideLoading();
                
                if (window.mapManager) {
                    window.mapManager.displayManualRoute(campusTourRoute);
                }
                
                const saveConfirmed = confirm(`Campus tour route created!\n\nRoute covers ${campusTourRoute.waypoints.length} locations\nTotal distance: ${this.formatDistance(campusTourRoute.distance)}\n\nSave this route for future pathfinding?`);
                
                if (saveConfirmed) {
                    // Save to local storage
                    localStorage.setItem('campusTourRoute', JSON.stringify(campusTourRoute));
                    this.showNotification('Campus tour route saved! This route will be used for pathfinding.', 'success');
                } else {
                    this.showNotification('Campus tour route displayed but not saved.', 'info');
                }
            }, 1000);
            
        } catch (error) {
            this.hideLoading();
            console.error('Campus tour creation failed:', error);
            this.showNotification('Failed to create campus tour route: ' + error.message, 'error');
        }
    }
    
    // Generate comprehensive campus tour route
    generateCampusTourRoute() {
        // Get all buildings from campus data
        const buildings = Object.keys(CampusData.buildings);
        
        // Define logical tour order based on campus layout
        const tourOrder = [
            'Entry Gate',
            'Main Gate', 
            'Security Office',
            'Library',
            'Block A',
            'Cafe',
            'Auditorium',
            'Block B',
            'Faculty Apartment',
            'DG Yard',
            'Food Court',
            'Gym',
            'Badminton Court',
            'Temple',
            'Boys Hostel',
            'Girls Hostel',
            'Mart',
            'Water Tank',
            'Laundry Area',
            'Water Treatment Area',
            'Cricket Ground',
            'Football Ground',
            'Basketball Court',
            'Volleyball Court',
            'Tennis Court',
            'Playing Ground',
            'Pottery Making Area',
            'Guest House',
            'Exit Gate'
        ];
        
        // Filter to only include buildings that exist in our data
        const validTourStops = tourOrder.filter(building => buildings.includes(building));
        
        // Add any missing buildings at the end
        const missingBuildings = buildings.filter(building => !validTourStops.includes(building));
        const completeTour = [...validTourStops, ...missingBuildings];
        
        // Convert building names to coordinates
        const waypoints = completeTour
            .map(building => CampusData.buildings[building]?.coordinates)
            .filter(coords => coords);
        
        // Calculate total distance
        let totalDistance = 0;
        for (let i = 0; i < waypoints.length - 1; i++) {
            const from = waypoints[i];
            const to = waypoints[i + 1];
            
            // Calculate distance using Haversine formula
            const R = 6371000; // Earth's radius in meters
            const dLat = (to[0] - from[0]) * Math.PI / 180;
            const dLon = (to[1] - from[1]) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                    Math.cos(from[0] * Math.PI / 180) * Math.cos(to[0] * Math.PI / 180) *
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            totalDistance += R * c;
        }
        
        return {
            name: 'Complete Campus Tour',
            waypoints: waypoints,
            buildingOrder: completeTour,
            distance: Math.round(totalDistance),
            createdAt: new Date().toISOString(),
            type: 'campus-tour'
        };
    }
    
    // Handle save all routes to file
    handleSaveAllRoutes() {
        const savedPaths = JSON.parse(localStorage.getItem('cuPathfinderSavedPaths') || '[]');
        const manualRoutes = JSON.parse(localStorage.getItem('manualRoutes') || '[]');
        const campusTour = localStorage.getItem('campusTourRoute');
        
        const allRoutes = {
            aiPaths: savedPaths,
            manualRoutes: manualRoutes,
            campusTour: campusTour ? JSON.parse(campusTour) : null,
            exportedAt: new Date().toISOString(),
            version: '1.0'
        };
        
        // Create downloadable file
        const dataStr = JSON.stringify(allRoutes, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        // Create download link
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `cu-pathfinder-routes-${new Date().toISOString().split('T')[0]}.json`;
        
        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification(`All routes exported successfully! (${savedPaths.length} AI paths, ${manualRoutes.length} manual routes)`, 'success');
    }
    
    // Handle mark all routes (display all routes on map)
    handleMarkAllRoutes() {
        if (!window.mapManager) {
            this.showNotification('Map not available', 'error');
            return;
        }
        
        const savedPaths = JSON.parse(localStorage.getItem('cuPathfinderSavedPaths') || '[]');
        const manualRoutes = JSON.parse(localStorage.getItem('manualRoutes') || '[]');
        const campusTour = localStorage.getItem('campusTourRoute');
        
        if (savedPaths.length === 0 && manualRoutes.length === 0 && !campusTour) {
            this.showNotification('No routes to display', 'info');
            return;
        }
        
        // Clear existing paths
        window.mapManager.clearPath();
        window.mapManager.clearManualRoute();
        
        // Create a layer group for all routes
        const allRoutesLayer = L.layerGroup().addTo(window.mapManager.map);
        
        // Add AI paths (blue lines)
        savedPaths.forEach((path, index) => {
            if (path.coordinates && path.coordinates.length > 1) {
                const pathLine = L.polyline(path.coordinates, {
                    color: '#3498db',
                    weight: 4,
                    opacity: 0.7,
                    dashArray: '5, 5'
                });
                pathLine.bindPopup(`AI Path: ${path.name}`);
                pathLine.addTo(allRoutesLayer);
            }
        });
        
        // Add manual routes (red lines)
        manualRoutes.forEach((route, index) => {
            if (route.waypoints && route.waypoints.length > 1) {
                const routeLine = L.polyline(route.waypoints, {
                    color: '#e74c3c',
                    weight: 4,
                    opacity: 0.7,
                    dashArray: '10, 5'
                });
                routeLine.bindPopup(`Manual Route: ${route.name}`);
                routeLine.addTo(allRoutesLayer);
            }
        });
        
        // Add campus tour (orange line)
        if (campusTour) {
            const tourData = JSON.parse(campusTour);
            if (tourData.waypoints && tourData.waypoints.length > 1) {
                const tourLine = L.polyline(tourData.waypoints, {
                    color: '#f39c12',
                    weight: 6,
                    opacity: 0.8,
                    lineCap: 'round'
                });
                tourLine.bindPopup(`Campus Tour: ${tourData.name}`);
                tourLine.addTo(allRoutesLayer);
            }
        }
        
        // Fit map to show all routes
        if (allRoutesLayer.getLayers().length > 0) {
            const group = new L.featureGroup(allRoutesLayer.getLayers());
            window.mapManager.map.fitBounds(group.getBounds().pad(0.1));
        }
        
        // Store reference for clearing later
        window.mapManager.allRoutesLayer = allRoutesLayer;
        
        const totalRoutes = savedPaths.length + manualRoutes.length + (campusTour ? 1 : 0);
        this.showNotification(`Displaying all ${totalRoutes} routes on map! Click any route for details.`, 'success');
        
        // Close modal
        document.getElementById('saved-paths-modal').remove();
    }
    
    // Format distance helper
    formatDistance(meters) {
        if (meters < 1000) {
            return Math.round(meters) + " m";
        } else {
            return (meters / 1000).toFixed(1) + " km";
        }
    }
}

// Create global UI controller instance
const uiController = new UIController();

// Make it available globally
window.uiController = uiController;