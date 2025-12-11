// Main Application File for CU PathFinder
// Initializes and coordinates all modules

class CUPathFinderApp {
    constructor() {
        this.version = '1.0.0';
        this.isInitialized = false;
        this.modules = {};
        
        // Initialize the application
        this.initialize();
    }
    
    // Initialize the application
    async initialize() {
        console.log('🚀 Initializing CU PathFinder...');
        
        try {
            // Wait for DOM to be ready
            await this.waitForDOM();
            
            // Initialize modules in order
            await this.initializeModules();
            
            // Setup global event handlers
            this.setupGlobalEvents();
            
            // Perform initial setup
            this.performInitialSetup();
            
            // Mark as initialized
            this.isInitialized = true;
            
            console.log('✅ CU PathFinder initialized successfully!');
            this.showWelcomeMessage();
            
        } catch (error) {
            console.error('❌ Failed to initialize CU PathFinder:', error);
            this.showErrorMessage(error);
        }
    }
    
    // Wait for DOM to be ready
    waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }
    
    // Initialize all modules
    async initializeModules() {
        console.log('📦 Initializing modules...');
        
        // Initialize Map Manager
        try {
            this.modules.mapManager = new MapManager('campus-map');
            window.mapManager = this.modules.mapManager;
            console.log('✅ Map Manager initialized');
        } catch (error) {
            console.error('❌ Map Manager initialization failed:', error);
        }
        
        // Pathfinding Engine is already initialized globally
        this.modules.pathfindingEngine = window.pathfindingEngine || pathfindingEngine;
        console.log('✅ Pathfinding Engine ready');
        
        // ChatBot is already initialized globally
        this.modules.chatBot = window.chatBot || chatBot;
        console.log('✅ ChatBot ready');
        
        // UI Controller is already initialized globally
        this.modules.uiController = window.uiController || uiController;
        console.log('✅ UI Controller ready');
        
        // Check backend connectivity
        await this.checkBackendStatus();
    }
    
    // Check backend status
    async checkBackendStatus() {
        console.log('🔗 Checking backend connectivity...');
        
        const isOnline = await this.modules.pathfindingEngine.checkBackendConnection();
        
        if (isOnline) {
            console.log('✅ Backend connected');
            this.showBackendStatus('online');
        } else {
            console.log('⚠️  Backend offline - using client-side algorithms');
            this.showBackendStatus('offline');
        }
    }
    
    // Setup global event handlers
    setupGlobalEvents() {
        // Window resize handler
        window.addEventListener('resize', () => {
            if (this.modules.mapManager && this.modules.mapManager.isReady()) {
                this.modules.mapManager.resize();
            }
        });
        
        // Online/offline status
        window.addEventListener('online', () => {
            console.log('🌐 Network connection restored');
            this.modules.pathfindingEngine.checkBackendConnection();
            this.showBackendStatus('online');
        });
        
        window.addEventListener('offline', () => {
            console.log('📴 Network connection lost');
            this.showBackendStatus('offline');
        });
        
        // Page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.modules.mapManager) {
                // Refresh map when page becomes visible
                setTimeout(() => {
                    this.modules.mapManager.resize();
                }, 100);
            }
        });
        
        // Unload handler
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        // Error handler
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.handleGlobalError(event.error);
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleGlobalError(event.reason);
        });
        
        console.log('🎯 Global event handlers setup');
    }
    
    // Perform initial setup
    performInitialSetup() {
        // Load user preferences
        this.loadUserPreferences();
        
        // Setup analytics (if needed)
        this.setupAnalytics();
        
        // Check for URL parameters
        this.handleURLParameters();
        
        // Setup keyboard shortcuts help
        this.setupKeyboardShortcuts();
        
        console.log('⚙️  Initial setup complete');
    }
    
    // Show welcome message
    showWelcomeMessage() {
        if (this.modules.uiController) {
            this.modules.uiController.showNotification(
                `Welcome to CU PathFinder v${this.version}! 🗺️ Find the best routes around campus using AI algorithms.`,
                'success',
                6000
            );
        }
    }
    
    // Show error message
    showErrorMessage(error) {
        const errorMessage = `Failed to initialize CU PathFinder: ${error.message}`;
        
        // Try to show in UI
        if (this.modules.uiController) {
            this.modules.uiController.showNotification(errorMessage, 'error', 10000);
        } else {
            // Fallback to alert
            alert(errorMessage);
        }
    }
    
    // Show backend status
    showBackendStatus(status) {
        const statusElement = document.querySelector('.backend-status');
        
        if (!statusElement) {
            // Create status indicator
            const indicator = document.createElement('div');
            indicator.className = 'backend-status';
            indicator.style.cssText = `
                position: fixed;
                top: 90px;
                right: 20px;
                padding: 8px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                z-index: 1500;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            `;
            document.body.appendChild(indicator);
        }
        
        const indicator = document.querySelector('.backend-status');
        
        if (status === 'online') {
            indicator.textContent = '🟢 Backend Online';
            indicator.style.background = 'rgba(39, 174, 96, 0.9)';
            indicator.style.color = 'white';
        } else {
            indicator.textContent = '🔴 Offline Mode';
            indicator.style.background = 'rgba(243, 156, 18, 0.9)';
            indicator.style.color = 'white';
        }
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (indicator) {
                indicator.style.opacity = '0.7';
            }
        }, 3000);
    }
    
    // Load user preferences
    loadUserPreferences() {
        try {
            const preferences = localStorage.getItem('cuPathfinderPreferences');
            if (preferences) {
                const prefs = JSON.parse(preferences);
                this.applyPreferences(prefs);
                console.log('📋 User preferences loaded');
            }
        } catch (error) {
            console.warn('Failed to load user preferences:', error);
        }
    }
    
    // Apply user preferences
    applyPreferences(preferences) {
        // Apply algorithm preference
        if (preferences.defaultAlgorithm) {
            const algorithmSelect = document.getElementById('algorithm-select');
            if (algorithmSelect) {
                algorithmSelect.value = preferences.defaultAlgorithm;
            }
        }
        
        // Apply theme preference
        if (preferences.theme) {
            document.body.classList.toggle('dark-theme', preferences.theme === 'dark');
        }
        
        // Apply map preferences
        if (preferences.showMarkers !== undefined && this.modules.mapManager) {
            if (!preferences.showMarkers) {
                this.modules.mapManager.toggleMarkers();
            }
        }
    }
    
    // Save user preferences
    saveUserPreferences() {
        try {
            const algorithmSelect = document.getElementById('algorithm-select');
            
            const preferences = {
                defaultAlgorithm: algorithmSelect?.value || 'UCS',
                theme: document.body.classList.contains('dark-theme') ? 'dark' : 'light',
                showMarkers: this.modules.mapManager?.showAllMarkers !== false,
                version: this.version,
                lastSaved: new Date().toISOString()
            };
            
            localStorage.setItem('cuPathfinderPreferences', JSON.stringify(preferences));
            console.log('💾 User preferences saved');
        } catch (error) {
            console.warn('Failed to save user preferences:', error);
        }
    }
    
    // Setup analytics (placeholder)
    setupAnalytics() {
        // This is where you would initialize analytics
        // For example: Google Analytics, Mixpanel, etc.
        console.log('📊 Analytics setup (placeholder)');
    }
    
    // Handle URL parameters
    handleURLParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // Handle start parameter
        const start = urlParams.get('start');
        if (start) {
            const startSelect = document.getElementById('start-location');
            if (startSelect) {
                startSelect.value = start;
            }
        }
        
        // Handle end parameter
        const end = urlParams.get('end');
        if (end) {
            const endSelect = document.getElementById('end-location');
            if (endSelect) {
                endSelect.value = end;
            }
        }
        
        // Handle algorithm parameter
        const algorithm = urlParams.get('algorithm');
        if (algorithm) {
            const algorithmSelect = document.getElementById('algorithm-select');
            if (algorithmSelect) {
                algorithmSelect.value = algorithm;
            }
        }
        
        // Auto-find path if both start and end are provided
        if (start && end) {
            setTimeout(() => {
                if (this.modules.uiController) {
                    this.modules.uiController.handleFindPath();
                }
            }, 1000);
        }
        
        console.log('🔗 URL parameters processed');
    }
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        // Add help modal for keyboard shortcuts
        const helpHtml = `
            <div id="keyboard-help-modal" class="modal hidden">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3><i class="fas fa-keyboard"></i> Keyboard Shortcuts</h3>
                        <button class="close-btn" onclick="app.hideKeyboardHelp()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="shortcuts-grid">
                            <div class="shortcut-item">
                                <kbd>Ctrl</kbd> + <kbd>Enter</kbd>
                                <span>Find Path</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Esc</kbd>
                                <span>Clear Path / Close Modal</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Ctrl</kbd> + <kbd>M</kbd>
                                <span>Toggle Map Markers</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>F11</kbd>
                                <span>Toggle Fullscreen Map</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>?</kbd>
                                <span>Show This Help</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', helpHtml);
        
        // Listen for ? key to show help
        document.addEventListener('keydown', (e) => {
            if (e.key === '?' && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                this.showKeyboardHelp();
            }
        });
        
        console.log('⌨️  Keyboard shortcuts setup');
    }
    
    // Show keyboard help modal
    showKeyboardHelp() {
        const modal = document.getElementById('keyboard-help-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }
    
    // Hide keyboard help modal
    hideKeyboardHelp() {
        const modal = document.getElementById('keyboard-help-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }
    
    // Handle global errors
    handleGlobalError(error) {
        console.error('Application error:', error);
        
        // Don't spam users with error notifications
        if (!this.lastErrorTime || Date.now() - this.lastErrorTime > 5000) {
            this.lastErrorTime = Date.now();
            
            if (this.modules.uiController) {
                this.modules.uiController.showNotification(
                    'An unexpected error occurred. Please refresh the page if problems persist.',
                    'error',
                    8000
                );
            }
        }
    }
    
    // Get application status
    getStatus() {
        return {
            version: this.version,
            isInitialized: this.isInitialized,
            modules: Object.keys(this.modules),
            backendOnline: this.modules.pathfindingEngine?.isOnline || false,
            mapReady: this.modules.mapManager?.isReady() || false
        };
    }
    
    // Restart application
    async restart() {
        console.log('🔄 Restarting CU PathFinder...');
        
        // Cleanup
        this.cleanup();
        
        // Reset state
        this.isInitialized = false;
        this.modules = {};
        
        // Reinitialize
        await this.initialize();
    }
    
    // Cleanup resources
    cleanup() {
        console.log('🧹 Cleaning up CU PathFinder...');
        
        // Save user preferences
        this.saveUserPreferences();
        
        // Cleanup modules
        if (this.modules.mapManager) {
            // Map cleanup would go here
        }
        
        // Clear timers, intervals, etc.
        // (Add as needed)
        
        console.log('✅ Cleanup complete');
    }
    
    // Debug information
    debug() {
        return {
            app: this.getStatus(),
            campus: {
                buildings: Object.keys(CampusData.buildings).length,
                connections: CampusData.connections.length,
                categories: Object.keys(CampusData.categories).length
            },
            pathfinding: {
                isOnline: this.modules.pathfindingEngine?.isOnline,
                algorithms: this.modules.pathfindingEngine?.algorithms
            },
            map: {
                isReady: this.modules.mapManager?.isReady(),
                markersVisible: this.modules.mapManager?.showAllMarkers,
                currentZoom: this.modules.mapManager?.getZoom()
            },
            chat: {
                historyLength: this.modules.chatBot?.getHistory().length,
                context: this.modules.chatBot?.getContext()
            },
            ui: {
                currentPath: this.modules.uiController?.currentPath !== null,
                isNavigating: this.modules.uiController?.isNavigating,
                stops: this.modules.uiController?.stops.length
            }
        };
    }
}

// Initialize the application
const app = new CUPathFinderApp();

// Make app available globally for debugging
window.app = app;

// Add CSS for keyboard shortcuts modal
const keyboardShortcutsCSS = `
<style>
.shortcuts-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
}

.shortcut-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.shortcut-item kbd {
    background: #e2e8f0;
    border: 1px solid #cbd5e0;
    border-radius: 4px;
    padding: 4px 8px;
    font-family: monospace;
    font-size: 12px;
    font-weight: bold;
    color: #2d3748;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.shortcut-item span {
    color: #4a5568;
    font-weight: 500;
}

.backend-status {
    user-select: none;
    pointer-events: none;
}

@media (max-width: 768px) {
    .backend-status {
        top: 70px;
        right: 10px;
        font-size: 11px;
        padding: 6px 10px;
    }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', keyboardShortcutsCSS);

// Add some helpful global functions
window.cuPathFinder = {
    findPath: (start, end, algorithm = 'UCS') => {
        return app.modules.pathfindingEngine.findPath(start, end, algorithm);
    },
    
    getBuildings: () => {
        return CampusData.utils.getAllBuildingNames();
    },
    
    highlightBuilding: (name) => {
        if (app.modules.mapManager) {
            app.modules.mapManager.highlightBuilding(name);
        }
    },
    
    askBot: (message) => {
        return app.modules.chatBot.processMessage(message);
    },
    
    debug: () => {
        return app.debug();
    },
    
    restart: () => {
        return app.restart();
    }
};

console.log('🎉 CU PathFinder ready! Try: cuPathFinder.debug() for debug info');