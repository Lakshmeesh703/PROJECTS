// Data Manager - Handles coordinate format consistency and data validation
class CampusDataManager {
    constructor() {
        this.buildings = {};
        this.connections = [];
        this.initialize();
    }

    // Initialize with proper data format validation
    initialize() {
        // Load existing data and normalize coordinates
        this.loadAndNormalizeData();
        
        // Set up automatic format validation
        this.setupFormatValidation();
        
        console.log('🔧 CampusDataManager initialized with format validation');
    }

    // Load existing data and convert to proper format
    loadAndNormalizeData() {
        console.log('🔄 Data manager loading campus data...');
        
        // Check if CampusData exists and has buildings
        if (typeof CampusData !== 'undefined' && CampusData.buildings) {
            console.log('📊 Raw campus data:', CampusData.buildings);
            Object.entries(CampusData.buildings).forEach(([name, data]) => {
                const normalized = this.normalizeBuilding(name, data);
                if (normalized) {
                    this.buildings[name] = normalized;
                    console.log(`✅ Normalized ${name}:`, normalized);
                } else {
                    console.error(`❌ Failed to normalize ${name}:`, data);
                }
            });
        } else {
            console.log('⚠️ No CampusData found or CampusData.buildings is empty');
        }
        
        console.log(`✅ Loaded and normalized ${Object.keys(this.buildings).length} buildings`);
    }

    // Normalize building data to consistent format
    normalizeBuilding(name, data) {
        if (!data || typeof data !== 'object') {
            console.error(`❌ Invalid building data for ${name}:`, data);
            return null;
        }
        
        let coordinates;
        
        // Handle different coordinate formats
        if (Array.isArray(data.coordinates)) {
            // Already in correct format
            coordinates = data.coordinates;
            console.log(`📍 ${name}: Using existing coordinates array`, coordinates);
        } else if (data.lat !== undefined && data.lng !== undefined) {
            // Convert from separate lat/lng properties
            coordinates = [parseFloat(data.lat), parseFloat(data.lng)];
            console.log(`📍 ${name}: Converted lat/lng to coordinates`, coordinates);
        } else if (data.latitude !== undefined && data.longitude !== undefined) {
            // Convert from latitude/longitude properties
            coordinates = [parseFloat(data.latitude), parseFloat(data.longitude)];
            console.log(`📍 ${name}: Converted latitude/longitude to coordinates`, coordinates);
        } else {
            console.error(`❌ Invalid coordinate format for building: ${name}`, data);
            return null;
        }
        
        // Validate coordinates
        if (!Array.isArray(coordinates) || coordinates.length !== 2 || 
            isNaN(coordinates[0]) || isNaN(coordinates[1])) {
            console.error(`❌ Invalid coordinates for building: ${name}`, coordinates);
            return null;
        }

        return {
            coordinates: coordinates,
            type: data.type || 'building',
            description: data.description || `${name} - ${data.type || 'Building'}`,
            facilities: data.facilities || [],
            dateAdded: data.dateAdded || new Date().toISOString(),
            addedBy: data.addedBy || 'System'
        };
    }

    // Add a new building with validation
    addBuilding(name, coordinates, type = 'building', description = '') {
        if (!name || !coordinates || !Array.isArray(coordinates) || coordinates.length !== 2) {
            throw new Error('Invalid building data: name and coordinates [lat, lng] are required');
        }

        const building = {
            coordinates: [parseFloat(coordinates[0]), parseFloat(coordinates[1])],
            type: type,
            description: description || `${name} - ${type}`,
            facilities: [],
            dateAdded: new Date().toISOString(),
            addedBy: 'User'
        };

        this.buildings[name] = building;
        
        // Save to file immediately
        this.saveBuildingsToFile();
        
        console.log(`✅ Added building: ${name} at [${coordinates[0]}, ${coordinates[1]}]`);
        return building;
    }

    // Update building position
    updateBuildingPosition(name, newCoordinates) {
        if (!this.buildings[name]) {
            throw new Error(`Building not found: ${name}`);
        }

        if (!Array.isArray(newCoordinates) || newCoordinates.length !== 2) {
            throw new Error('Invalid coordinates: must be [lat, lng] array');
        }

        this.buildings[name].coordinates = [parseFloat(newCoordinates[0]), parseFloat(newCoordinates[1])];
        
        // Save to file immediately
        this.saveBuildingsToFile();
        
        console.log(`📍 Updated ${name} position to [${newCoordinates[0]}, ${newCoordinates[1]}]`);
    }

    // Get building data in consistent format
    getBuilding(name) {
        return this.buildings[name] || null;
    }

    // Get all buildings in consistent format
    getAllBuildings() {
        return { ...this.buildings };
    }

    // Save buildings to file with proper format
    async saveBuildingsToFile() {
        try {
            // Convert to format expected by backend (lat/lng properties)
            const buildingsForSaving = {};
            Object.entries(this.buildings).forEach(([name, data]) => {
                buildingsForSaving[name] = {
                    lat: data.coordinates[0],
                    lng: data.coordinates[1],
                    type: data.type
                };
            });

            const response = await fetch('/api/save-buildings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ buildings: buildingsForSaving })
            });

            const result = await response.json();
            
            if (result.success) {
                console.log(`💾 Successfully saved ${result.buildings_count} buildings to file`);
            } else {
                console.error('❌ Failed to save buildings:', result.error);
            }
        } catch (error) {
            console.error('❌ Error saving buildings to file:', error);
        }
    }

    // Setup automatic format validation
    setupFormatValidation() {
        // Override CampusData.buildings with a proxy that validates format
        if (typeof CampusData !== 'undefined') {
            const self = this;
            
            // Create a proxy to intercept access to CampusData.buildings
            CampusData.buildings = new Proxy(this.buildings, {
                get(target, prop) {
                    return target[prop];
                },
                set(target, prop, value) {
                    // Validate and normalize any new buildings added
                    if (typeof prop === 'string' && value) {
                        target[prop] = self.normalizeBuilding(prop, value);
                        self.saveBuildingsToFile();
                    }
                    return true;
                }
            });
        }
    }

    // Export data in various formats
    exportData(format = 'json') {
        switch (format) {
            case 'json':
                return JSON.stringify(this.buildings, null, 2);
            case 'csv':
                return this.exportToCSV();
            case 'coordinates':
                return this.exportCoordinatesOnly();
            default:
                return this.buildings;
        }
    }

    // Export to CSV format
    exportToCSV() {
        const headers = ['Name', 'Latitude', 'Longitude', 'Type', 'Description'];
        const rows = Object.entries(this.buildings).map(([name, data]) => [
            name,
            data.coordinates[0],
            data.coordinates[1],
            data.type,
            data.description
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    // Export coordinates only
    exportCoordinatesOnly() {
        const coords = {};
        Object.entries(this.buildings).forEach(([name, data]) => {
            coords[name] = data.coordinates;
        });
        return coords;
    }
}

// Initialize global data manager
const dataManager = new CampusDataManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CampusDataManager;
}