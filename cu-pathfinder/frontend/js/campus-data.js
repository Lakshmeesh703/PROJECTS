// Campus Data for CU PathFinder
// Contains all buildings, coordinates, connections, and metadata

const CampusData = {
    // Campus bounds and center - Chanakya University, Karnataka, India
    bounds: {
        center: [13.2220167, 77.755403], // Chanakya University coordinates from Google Maps
        zoom: 17,
        minZoom: 15,
        maxZoom: 20
    },
    
    // Campus buildings - Interactive placement with satellite precision
    // Use the "Add Building" button to place additional buildings on the satellite map
    buildings: {
        "Entry Gate": {
            "lat": 13.220186973909623,
            "lng": 77.75417625904085,
            "type": "entrance"
        },
        "Exit Gate": {
            "lat": 13.220155195558384,
            "lng": 77.75507211685182,
            "type": "entrance"
        },
        "Flag Post": {
            "lat": 13.221682489363936,
            "lng": 77.75497090146462,
            "type": "landmark"
        },
        "Block B": {
            "lat": 13.223450311578047,
            "lng": 77.7560088759252,
            "type": "academic"
        },
        "Faculty Apartment": {
            "lat": 13.223703528320414,
            "lng": 77.75727521268479,
            "type": "residential"
        },
        "DG Yard": {
            "lat": 13.22314203987797,
            "lng": 77.75727497774372,
            "type": "utility"
        },
        "Boys Hostel": {
            "lat": 13.224688833473646,
            "lng": 77.75892545613766,
            "type": "residential"
        },
        "Girls Hostel": {
            "lat": 13.224536376798993,
            "lng": 77.7592865193227,
            "type": "residential"
        },
        "Mart": {
            "lat": 13.224638216895125,
            "lng": 77.75923017691468,
            "type": "commercial"
        },
        "Food Court": {
            "lat": 13.224876918137536,
            "lng": 77.75727277753974,
            "type": "dining"
        },
        "Gym": {
            "lat": 13.224610624822716,
            "lng": 77.75725187670851,
            "type": "fitness"
        },
        "Badminton Court": {
            "lat": 13.225038875066291,
            "lng": 77.75745578256611,
            "type": "sports"
        },
        "Cricket Ground": {
            "lat": 13.228981817960303,
            "lng": 77.75717619055452,
            "type": "sports"
        },
        "Block A": {
            "lat": 13.222296958450547,
            "lng": 77.75535713566691,
            "type": "academic"
        },
        "Basketball Court": {
            "lat": 13.228826563896906,
            "lng": 77.75815457143432,
            "type": "sports"
        },
        "Tennis Court": {
            "lat": 13.228462383528285,
            "lng": 77.75843024253847,
            "type": "sports"
        },
        "Security Office": {
            "lat": 13.2213873729162,
            "lng": 77.75509438910794,
            "type": "security"
        },
        "Main Gate": {
            "lat": 13.221363871251494,
            "lng": 77.75516929644742,
            "type": "entrance"
        },
        "Library": {
            "lat": 13.222161205274716,
            "lng": 77.75549696294732,
            "type": "academic"
        },
        "Cafe": {
            "lat": 13.222527462879173,
            "lng": 77.75516599416734,
            "type": "dining"
        },
        "Playing Ground": {
            "lat": 13.22104356182045,
            "lng": 77.75355985730003,
            "type": "sports"
        },
        "Pottery Making Area": {
            "lat": 13.222558124147385,
            "lng": 77.7534954659766,
            "type": "workshop"
        },
        "Auditorium": {
            "lat": 13.222196800668,
            "lng": 77.7552790595366,
            "type": "academic"
        },
        "Water Treatment Area": {
            "lat": 13.22415785298079,
            "lng": 77.75849842509406,
            "type": "utility"
        },
        "Laundry Area": {
            "lat": 13.224332809288764,
            "lng": 77.75869159906445,
            "type": "utility"
        },
        "Temple": {
            "lat": 13.22327269648816,
            "lng": 77.75752204761696,
            "type": "religious"
        },
        "Volleyball Court": {
            "lat": 13.22870669105609,
            "lng": 77.75857776403429,
            "type": "sports"
        },
        "Football Ground": {
            "lat": 13.22804334467194,
            "lng": 77.75639712810518,
            "type": "sports"
        },
        "Guest House": {
            "lat": 13.223395976770766,
            "lng": 77.75413870811464,
            "type": "hostel"
        },
    },
    
    // Campus connections (edges) with distances in meters
    // Realistic pathways following cement roads and walkways
    connections: [
        // Main entrance connections with road waypoints
        { 
            from: "Entry Gate", 
            to: "Main Gate", 
            distance: 50,
            waypoints: [
                [13.221200000000000, 77.75500000000000], // Road curve point
            ]
        },
        { 
            from: "Main Gate", 
            to: "Security Office", 
            distance: 30,
            waypoints: [
                [13.221350000000000, 77.75510000000000], // Path junction
            ]
        },
        { 
            from: "Main Gate", 
            to: "Library", 
            distance: 80,
            waypoints: [
                [13.221500000000000, 77.75530000000000], // Main road
                [13.221800000000000, 77.75545000000000], // Turn to library
            ]
        },
        
        // Academic area connections with cement pathways
        { 
            from: "Library", 
            to: "Block A", 
            distance: 60,
            waypoints: [
                [13.222000000000000, 77.75540000000000], // Walkway junction
            ]
        },
        { 
            from: "Block A", 
            to: "Cafe", 
            distance: 40,
            waypoints: [
                [13.222200000000000, 77.75525000000000], // Campus courtyard
            ]
        },
        { 
            from: "Library", 
            to: "Block B", 
            distance: 120,
            waypoints: [
                [13.222300000000000, 77.75600000000000], // Main campus road
                [13.223000000000000, 77.75650000000000], // Road turn
            ]
        },
        { 
            from: "Block A", 
            to: "Block B", 
            distance: 150,
            waypoints: [
                [13.222500000000000, 77.75580000000000], // Connect via main road
                [13.223200000000000, 77.75620000000000], // Road intersection
            ]
        },
        
        // Central area connections
        { from: "Library", to: "Flag Post", distance: 90 },
        { from: "Flag Post", to: "Block B", distance: 180 },
        { from: "Cafe", to: "Pottery Making Area", distance: 70 },
        
        // Residential area connections
        { from: "Block B", to: "Faculty Apartment", distance: 200 },
        { from: "Faculty Apartment", to: "DG Yard", distance: 60 },
        { from: "DG Yard", to: "Food Court", distance: 80 },
        { from: "Food Court", to: "Boys Hostel", distance: 100 },
        { from: "Boys Hostel", to: "Girls Hostel", distance: 50 },
        { from: "Girls Hostel", to: "Mart", distance: 40 },
        { from: "Boys Hostel", to: "Water Tank", distance: 90 },
        
        // Sports area connections
        { from: "Food Court", to: "Cricket Ground", distance: 300 },
        { from: "Cricket Ground", to: "Basketball Court", distance: 150 },
        { from: "Basketball Court", to: "Volleyball Court", distance: 80 },
        { from: "Volleyball Court", to: "Tennis Court", distance: 60 },
        { from: "Basketball Court", to: "Tennis Court", distance: 100 },
        
        // Alternative pathways and shortcuts
        { from: "Guest House", to: "Block A", distance: 140 },
        { from: "Guest House", to: "Main Gate", distance: 120 },
        { from: "Playing Ground", to: "Pottery Making Area", distance: 80 },
        { from: "Playing Ground", to: "Entry Gate", distance: 200 },
        { from: "Exit Gate", to: "Flag Post", distance: 110 },
        { from: "Security Office", to: "Exit Gate", distance: 70 },
        
        // Cross-campus connections for better accessibility
        { from: "Block B", to: "Cricket Ground", distance: 450 },
        { from: "Water Tank", to: "Tennis Court", distance: 200 },
        { from: "DG Yard", to: "Water Tank", distance: 120 },
        
        // Additional facility connections
        { from: "Food Court", to: "Gym", distance: 30 },
        { from: "Gym", to: "Badminton Court", distance: 20 },
        { from: "Cricket Ground", to: "Football Ground", distance: 100 },
        { from: "Football Ground", to: "Playing Ground", distance: 150 },
        { from: "Temple", to: "Food Court", distance: 40 },
        { from: "Water Treatment Area", to: "Laundry Area", distance: 60 },
        { from: "Auditorium", to: "Library", distance: 50 },
        { from: "Auditorium", to: "Block A", distance: 80 }
    ],
    
    // Building categories for filtering and display
    categories: {
        "Academic": [],
        "Residential": [],
        "Sports & Recreation": [],
        "Food & Dining": [],
        "Administrative": [],
        "Student Services": [],
        "Utilities": [],
        "Special Areas": []
    },
    
    // Location aliases for natural language processing
    aliases: {
        // Academic buildings
        "cs building": "Block A",
        "computer science": "Block A",
        "academic block 1": "Block A",
        "main academic building": "Block A",
        "academic block 2": "Block B",
        "second block": "Block B",
        "central library": "Library",
        "lib": "Library",
        "books": "Library",
        "main auditorium": "Auditorium",
        "assembly hall": "Auditorium",
        
        // Residential
        "boys dorm": "Boys Hostel",
        "male hostel": "Boys Hostel",
        "girls dorm": "Girls Hostel",
        "female hostel": "Girls Hostel",
        "faculty housing": "Faculty Apartment",
        "teacher quarters": "Faculty Apartment",
        "visitor accommodation": "Guest House",
        
        // Sports facilities
        "fitness center": "Gym",
        "workout": "Gym",
        "exercise": "Gym",
        "cricket field": "Cricket Ground",
        "football field": "Football Ground",
        "soccer field": "Football Ground",
        "basketball": "Basketball Court",
        "volleyball": "Volleyball Court",
        "tennis": "Tennis Court",
        "badminton": "Badminton Court",
        
        // Food and dining
        "dining hall": "Canteen",
        "mess": "Canteen",
        "cafeteria": "Canteen",
        "food court": "Food Court",
        "restaurants": "Food Court",
        "shop": "Mart",
        "store": "Mart",
        "grocery": "Mart",
        
        // Administrative and services
        "administration": "Admin Office",
        "admin": "Admin Office",
        "security": "Security Office",
        "main entrance": "Main Gate",
        "front gate": "Main Gate",
        "entrance": "Entry Gate",
        "exit": "Exit Gate",
        "back gate": "Exit Gate",
        "student services": "Student Center",
        "student hub": "Student Center",
        "clinic": "Medical Center",
        "health center": "Medical Center",
        "hospital": "Medical Center",
        "first aid": "Medical Center",
        
        // Utilities and special areas
        "generator": "DG Yard",
        "power": "DG Yard",
        "water plant": "Water Treatment Area",
        "water": "Water Treatment Area",
        "water tank": "Water Tank",
        "tank": "Water Tank",
        "flag": "Flag Post",
        "assembly": "Flag Post",
        "pottery": "Pottery Making Area",
        "arts": "Pottery Making Area",
        "crafts": "Pottery Making Area"
    },
    
    // Map styling and markers
    mapStyles: {
        academic: {
            color: '#3498db',
            icon: 'graduation-cap'
        },
        residential: {
            color: '#e74c3c',
            icon: 'home'
        },
        sports: {
            color: '#27ae60',
            icon: 'dumbbell'
        },
        food: {
            color: '#f39c12',
            icon: 'utensils'
        },
        administrative: {
            color: '#9b59b6',
            icon: 'building'
        },
        'student services': {
            color: '#1abc9c',
            icon: 'users'
        },
        healthcare: {
            color: '#e67e22',
            icon: 'heartbeat'
        },
        utility: {
            color: '#95a5a6',
            icon: 'cog'
        },
        creative: {
            color: '#f1c40f',
            icon: 'palette'
        },
        security: {
            color: '#34495e',
            icon: 'shield-alt'
        },
        entrance: {
            color: '#8e44ad',
            icon: 'door-open'
        },
        landmark: {
            color: '#e74c3c',
            icon: 'flag'
        },
        commercial: {
            color: '#16a085',
            icon: 'shopping-bag'
        }
    },
    
    // Default map settings
    defaultSettings: {
        showAllMarkers: true,
        showConnections: false,
        pathColor: '#667eea',
        pathWeight: 4,
        pathOpacity: 0.8,
        markerSize: 25,
        animateMarkers: true,
        clustersEnabled: false
    },
    
    // Helper functions
    utils: {
        // Get building by name (case insensitive)
        getBuildingByName: function(name) {
            const normalizedName = name.toLowerCase().trim();
            
            // Check exact match first
            for (const building in CampusData.buildings) {
                if (building.toLowerCase() === normalizedName) {
                    return {
                        name: building,
                        data: CampusData.buildings[building]
                    };
                }
            }
            
            // Check aliases
            for (const alias in CampusData.aliases) {
                if (alias.toLowerCase() === normalizedName) {
                    const buildingName = CampusData.aliases[alias];
                    return {
                        name: buildingName,
                        data: CampusData.buildings[buildingName]
                    };
                }
            }
            
            return null;
        },
        
        // Get all building names
        getAllBuildingNames: function() {
            return Object.keys(CampusData.buildings).sort();
        },
        
        // Get buildings by category
        getBuildingsByCategory: function(category) {
            return CampusData.categories[category] || [];
        },
        
        // Get connection between two buildings
        getConnection: function(building1, building2) {
            return CampusData.connections.find(conn => 
                (conn.from === building1 && conn.to === building2) ||
                (conn.from === building2 && conn.to === building1)
            );
        },
        
        // Get all connections for a building
        getBuildingConnections: function(buildingName) {
            return CampusData.connections.filter(conn => 
                conn.from === buildingName || conn.to === buildingName
            );
        },
        
        // Calculate distance between two coordinates
        calculateDistance: function(coord1, coord2) {
            const R = 6371000; // Earth's radius in meters
            const dLat = (coord2[0] - coord1[0]) * Math.PI / 180;
            const dLon = (coord2[1] - coord1[1]) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                    Math.cos(coord1[0] * Math.PI / 180) * Math.cos(coord2[0] * Math.PI / 180) *
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            return R * c;
        },
        
        // Format distance for display
        formatDistance: function(meters) {
            if (meters < 1000) {
                return Math.round(meters) + " m";
            } else {
                return (meters / 1000).toFixed(1) + " km";
            }
        },
        
        // Calculate walking time
        calculateWalkingTime: function(distanceMeters, walkingSpeedMPS = 1.4) {
            const timeSeconds = distanceMeters / walkingSpeedMPS;
            const minutes = Math.floor(timeSeconds / 60);
            const seconds = Math.round(timeSeconds % 60);
            
            if (minutes === 0) {
                return `${seconds}s`;
            } else if (seconds === 0) {
                return `${minutes}m`;
            } else {
                return `${minutes}m ${seconds}s`;
            }
        },
        
        // Get building style by type
        getBuildingStyle: function(building) {
            const buildingData = CampusData.buildings[building];
            if (!buildingData) return CampusData.mapStyles.academic;
            
            const type = buildingData.type;
            return CampusData.mapStyles[type] || CampusData.mapStyles.academic;
        },
        
        // Search buildings by partial name
        searchBuildings: function(query) {
            const normalizedQuery = query.toLowerCase().trim();
            const results = [];
            
            // Direct name matches
            for (const building in CampusData.buildings) {
                if (building.toLowerCase().includes(normalizedQuery)) {
                    results.push({
                        name: building,
                        type: 'direct',
                        score: 1
                    });
                }
            }
            
            // Alias matches
            for (const alias in CampusData.aliases) {
                if (alias.toLowerCase().includes(normalizedQuery)) {
                    const buildingName = CampusData.aliases[alias];
                    if (!results.find(r => r.name === buildingName)) {
                        results.push({
                            name: buildingName,
                            type: 'alias',
                            score: 0.8
                        });
                    }
                }
            }
            
            // Sort by score and name
            return results.sort((a, b) => {
                if (a.score !== b.score) return b.score - a.score;
                return a.name.localeCompare(b.name);
            });
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CampusData;
}