// Chatbot Module for CU PathFinder
// Handles natural language processing and conversational interface

class ChatBot {
    constructor() {
        this.conversationHistory = [];
        this.context = {
            lastStart: null,
            lastEnd: null,
            lastAlgorithm: 'UCS'
        };
        
        // Initialize with welcome message
        this.addMessage('bot', this.getWelcomeMessage());
    }
    
    // Process user message and return response
    async processMessage(userMessage) {
        try {
            // Add user message to history
            this.addMessage('user', userMessage);
            
            // Send message to backend API
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Handle pathfinding responses
                if (data.type === 'pathfinding' && data.path_data) {
                    // Display path on map
                    if (window.mapManager) {
                        window.mapManager.displayPath(data.path_data);
                    }
                    
                    // Update UI with path result
                    if (window.uiController) {
                        window.uiController.displayPathResult(data.path_data);
                        window.uiController.showNavigationPanel(data.path_data);
                    }
                    
                    // Update context
                    this.context.lastStart = data.path_data.path[0];
                    this.context.lastEnd = data.path_data.path[data.path_data.path.length - 1];
                    this.context.lastAlgorithm = 'A*';
                }
                
                // Handle building information
                if (data.type === 'information' && data.building_data) {
                    // Highlight building on map
                    if (window.mapManager) {
                        window.mapManager.highlightBuilding(data.building_data.name);
                    }
                }
                
                // Add bot response to history
                this.addMessage('bot', data.response);
                return data.response;
                
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
            
        } catch (error) {
            console.error('Chatbot API error:', error);
            const errorResponse = "I'm sorry, I encountered an error processing your request. Please check your connection and try again.";
            this.addMessage('bot', errorResponse);
            return errorResponse;
        }
    }
    
    // Parse user intent from message
    parseIntent(message) {
        const normalizedMessage = message.toLowerCase().trim();
        
        // Pathfinding patterns
        const pathfindingPatterns = [
            /(?:how do i get|route|path|directions?|navigate|go|walk) (?:from )?(.+?) (?:to|→) (.+?)(?:\s+using\s+(.+?))?$/,
            /(?:find|show|get) (?:the )?(?:route|path|directions?) (?:from )?(.+?) (?:to|→) (.+?)(?:\s+using\s+(.+?))?$/,
            /(?:what's|whats) (?:the )?(?:best|shortest|fastest) (?:route|path|way) (?:from )?(.+?) (?:to|→) (.+?)$/,
            /(.+?) (?:to|→) (.+?)(?:\s+using\s+(.+?))?$/
        ];
        
        // Check pathfinding patterns
        for (const pattern of pathfindingPatterns) {
            const match = normalizedMessage.match(pattern);
            if (match) {
                return {
                    type: 'pathfinding',
                    start: this.normalizeLocation(match[1]),
                    end: this.normalizeLocation(match[2]),
                    algorithm: this.normalizeAlgorithm(match[3]) || 'UCS'
                };
            }
        }
        
        // Algorithm comparison patterns
        const comparisonPatterns = [
            /compare (?:algorithms?|all) (?:from )?(.+?) (?:to|→) (.+?)$/,
            /(?:show|analyze) (?:all )?algorithms? (?:for )?(?:from )?(.+?) (?:to|→) (.+?)$/,
            /compare (.+?) (?:to|→) (.+?)$/
        ];
        
        for (const pattern of comparisonPatterns) {
            const match = normalizedMessage.match(pattern);
            if (match) {
                return {
                    type: 'comparison',
                    start: this.normalizeLocation(match[1]),
                    end: this.normalizeLocation(match[2])
                };
            }
        }
        
        // Information patterns
        const infoPatterns = [
            /(?:what is|tell me about|info about|describe) (.+?)$/,
            /(?:where is|location of) (.+?)$/,
            /(?:list|show) (?:all )?(?:locations?|buildings?|places?)$/,
            /(?:what|which) (?:locations?|buildings?|places?) (?:are )?(?:available|exist)$/
        ];
        
        for (const pattern of infoPatterns) {
            const match = normalizedMessage.match(pattern);
            if (match) {
                const location = match[1];
                if (location && !location.includes('locations') && !location.includes('buildings')) {
                    return {
                        type: 'information',
                        subject: this.normalizeLocation(location)
                    };
                } else {
                    return {
                        type: 'information',
                        subject: 'list_all'
                    };
                }
            }
        }
        
        // Help patterns
        const helpPatterns = [
            /help|assist|support|how to|what can you do|commands?/,
            /(?:how do i|can you help me) .*/
        ];
        
        for (const pattern of helpPatterns) {
            if (normalizedMessage.match(pattern)) {
                return { type: 'help' };
            }
        }
        
        // Greeting patterns
        const greetingPatterns = [
            /^(?:hi|hello|hey|good (?:morning|afternoon|evening)|greetings?)$/
        ];
        
        for (const pattern of greetingPatterns) {
            if (normalizedMessage.match(pattern)) {
                return { type: 'greeting' };
            }
        }
        
        return { type: 'unknown', message: message };
    }
    
    // Handle pathfinding requests
    async handlePathfindingIntent(intent) {
        const { start, end, algorithm } = intent;
        
        if (!start || !end) {
            return "I need both a starting location and destination. Please specify both locations, for example: 'How do I get from Block A to Library?'";
        }
        
        // Validate locations
        const startBuilding = CampusData.utils.getBuildingByName(start);
        const endBuilding = CampusData.utils.getBuildingByName(end);
        
        if (!startBuilding) {
            const suggestions = this.suggestLocations(start);
            return `I couldn't find "${start}" on campus. ${suggestions}`;
        }
        
        if (!endBuilding) {
            const suggestions = this.suggestLocations(end);
            return `I couldn't find "${end}" on campus. ${suggestions}`;
        }
        
        try {
            // Update context
            this.context.lastStart = startBuilding.name;
            this.context.lastEnd = endBuilding.name;
            this.context.lastAlgorithm = algorithm;
            
            // Find path using pathfinding engine
            const result = await pathfindingEngine.findPath(startBuilding.name, endBuilding.name, algorithm);
            
            if (result.success) {
                // Display path on map
                if (window.mapManager) {
                    window.mapManager.displayPath(result);
                }
                
                // Update UI
                if (window.uiController) {
                    window.uiController.displayPathResult(result);
                    window.uiController.showNavigationPanel(result);
                }
                
                // Generate response
                const stepsList = result.steps.map((step, index) => 
                    `${index + 1}. ${step.instruction} (${step.formattedDistance})`
                ).join('\\n');
                
                return `🛣️ **Route found from ${startBuilding.name} to ${endBuilding.name}!**\\n\\n` +
                       `📏 **Distance:** ${CampusData.utils.formatDistance(result.distance)}\\n` +
                       `🚶 **Walking time:** ${result.walkingTime}\\n` +
                       `🧠 **Algorithm:** ${result.algorithm}\\n` +
                       `📊 **Nodes explored:** ${result.nodesExplored}\\n\\n` +
                       `**Step-by-step directions:**\\n${stepsList}\\n\\n` +
                       `The route has been highlighted on the map. Would you like me to compare this with other algorithms?`;
            } else {
                return `I couldn't find a path from ${startBuilding.name} to ${endBuilding.name}. This might be because these locations are not connected on campus.`;
            }
            
        } catch (error) {
            console.error('Pathfinding error:', error);
            return `I encountered an error while finding the path. Please try again or check if the locations are correct.`;
        }
    }
    
    // Handle information requests
    handleInformationIntent(intent) {
        const { subject } = intent;
        
        if (subject === 'list_all') {
            const buildings = CampusData.utils.getAllBuildingNames();
            const categorized = {};
            
            // Group by category
            for (const [category, buildingList] of Object.entries(CampusData.categories)) {
                categorized[category] = buildingList.filter(building => buildings.includes(building));
            }
            
            let response = "📍 **Available campus locations:**\\n\\n";
            
            for (const [category, buildingList] of Object.entries(categorized)) {
                if (buildingList.length > 0) {
                    response += `**${category}:**\\n`;
                    response += buildingList.map(building => `• ${building}`).join('\\n');
                    response += '\\n\\n';
                }
            }
            
            response += `Total: ${buildings.length} locations available.\\n\\n`;
            response += "You can ask me for directions between any of these locations!";
            
            return response;
            
        } else if (subject) {
            const building = CampusData.utils.getBuildingByName(subject);
            
            if (!building) {
                const suggestions = this.suggestLocations(subject);
                return `I couldn't find "${subject}" on campus. ${suggestions}`;
            }
            
            const details = pathfindingEngine.getLocationDetails(building.name);
            
            let response = `📍 **${building.name}**\\n\\n`;
            response += `${details.description}\\n\\n`;
            
            if (details.type) {
                response += `**Type:** ${details.type}\\n`;
            }
            
            if (details.capacity) {
                response += `**Capacity:** ${details.capacity}\\n`;
            }
            
            if (details.floors) {
                response += `**Floors:** ${details.floors}\\n`;
            }
            
            if (details.facilities && details.facilities.length > 0) {
                response += `**Facilities:**\\n`;
                response += details.facilities.map(facility => `• ${facility}`).join('\\n');
                response += '\\n';
            }
            
            response += `\\n**Coordinates:** ${details.coordinates[0].toFixed(4)}, ${details.coordinates[1].toFixed(4)}\\n\\n`;
            response += `Would you like directions to ${building.name}?`;
            
            // Highlight building on map
            if (window.mapManager) {
                window.mapManager.highlightBuilding(building.name);
            }
            
            return response;
        }
        
        return "What would you like to know? You can ask about specific buildings or request a list of all locations.";
    }
    
    // Handle algorithm comparison
    async handleComparisonIntent(intent) {
        const { start, end } = intent;
        
        if (!start || !end) {
            return "Please specify both locations for algorithm comparison, for example: 'Compare algorithms from Block A to Library'";
        }
        
        const startBuilding = CampusData.utils.getBuildingByName(start);
        const endBuilding = CampusData.utils.getBuildingByName(end);
        
        if (!startBuilding || !endBuilding) {
            return "I couldn't find one or both of those locations. Please check the spelling and try again.";
        }
        
        try {
            const results = await pathfindingEngine.compareAlgorithms(startBuilding.name, endBuilding.name);
            
            let response = `📊 **Algorithm Comparison: ${startBuilding.name} → ${endBuilding.name}**\\n\\n`;
            
            results.forEach(result => {
                if (result.error) {
                    response += `**${result.algorithm}:** Error - ${result.error}\\n`;
                } else {
                    response += `**${result.algorithm}:**\\n`;
                    response += `• Distance: ${CampusData.utils.formatDistance(result.distance)}\\n`;
                    response += `• Nodes explored: ${result.nodesExplored}\\n`;
                    response += `• Execution time: ${result.executionTime}ms\\n`;
                    response += `• Optimal: ${result.isOptimal ? '✅' : '❌'}\\n\\n`;
                }
            });
            
            // Find the best algorithm
            const validResults = results.filter(r => !r.error);
            if (validResults.length > 0) {
                const fastest = validResults.reduce((min, current) => 
                    current.nodesExplored < min.nodesExplored ? current : min
                );
                
                response += `🏆 **Most efficient:** ${fastest.algorithm} (${fastest.nodesExplored} nodes explored)\\n\\n`;
            }
            
            // Show comparison in UI
            if (window.uiController) {
                window.uiController.showAlgorithmComparison(results);
            }
            
            response += "The detailed comparison is shown in the Algorithm Comparison modal.";
            
            return response;
            
        } catch (error) {
            console.error('Comparison error:', error);
            return "I encountered an error while comparing algorithms. Please try again.";
        }
    }
    
    // Handle help requests
    handleHelpIntent(intent) {
        return `🤖 **I'm your AI campus navigation assistant!** Here's what I can help you with:\\n\\n` +
               `**🛣️ Find Routes:**\\n` +
               `• "How do I get from Block A to Library?"\\n` +
               `• "Find path from Canteen to Gym using A*"\\n` +
               `• "Route Block A to Library"\\n\\n` +
               `**📊 Compare Algorithms:**\\n` +
               `• "Compare algorithms from Block A to Library"\\n` +
               `• "Show all algorithms for Canteen to Gym"\\n\\n` +
               `**📍 Get Information:**\\n` +
               `• "Tell me about the Library"\\n` +
               `• "Where is the Gym?"\\n` +
               `• "List all locations"\\n\\n` +
               `**🧠 Available Algorithms:**\\n` +
               `• **UCS** (Uniform Cost Search) - Default, finds optimal paths\\n` +
               `• **A*** (A-Star) - Fastest, optimal paths with heuristics\\n` +
               `• **BFS** (Breadth-First Search) - Explores level by level\\n` +
               `• **DFS** (Depth-First Search) - Quick but not always optimal\\n\\n` +
               `Just ask me in natural language and I'll help you navigate the campus! 🗺️`;
    }
    
    // Handle greetings
    handleGreetingIntent(intent) {
        const greetings = [
            "Hello! I'm your AI campus navigation assistant. How can I help you find your way around campus?",
            "Hi there! Ready to explore Chanakya University? Ask me for directions anywhere on campus!",
            "Hey! I'm here to help you navigate the campus. Where would you like to go?",
            "Greetings! I can help you find the best routes around campus. What's your destination?"
        ];
        
        return greetings[Math.floor(Math.random() * greetings.length)];
    }
    
    // Handle unknown intents
    handleUnknownIntent(message) {
        const suggestions = [
            "I'm not sure I understand. Try asking for directions like: 'How do I get from Block A to Library?'",
            "I didn't catch that. You can ask me for routes, building information, or say 'help' for more options.",
            "Sorry, I'm not sure what you mean. Try asking about campus locations or directions between buildings.",
            "I don't understand that request. Ask me something like 'Find path from Canteen to Gym' or 'Tell me about the Library'."
        ];
        
        let response = suggestions[Math.floor(Math.random() * suggestions.length)];
        
        // Try to extract potential location names
        const words = message.toLowerCase().split(/\\s+/);
        const potentialLocations = words.filter(word => 
            word.length > 3 && 
            (CampusData.utils.getBuildingByName(word) || Object.keys(CampusData.aliases).includes(word))
        );
        
        if (potentialLocations.length > 0) {
            response += `\\n\\nI noticed you mentioned "${potentialLocations[0]}" - did you want directions involving this location?`;
        }
        
        return response;
    }
    
    // Normalize location names
    normalizeLocation(locationText) {
        if (!locationText) return null;
        
        const cleaned = locationText.trim().toLowerCase()
            .replace(/^(the|a|an)\\s+/, '') // Remove articles
            .replace(/\\s+(building|block|area|center|office)$/, '') // Remove common suffixes
            .trim();
        
        return cleaned;
    }
    
    // Normalize algorithm names
    normalizeAlgorithm(algorithmText) {
        if (!algorithmText) return null;
        
        const normalized = algorithmText.toLowerCase().trim();
        
        const algorithmMap = {
            'ucs': 'UCS',
            'uniform cost': 'UCS',
            'uniform cost search': 'UCS',
            'dijkstra': 'UCS',
            'a*': 'A*',
            'a star': 'A*',
            'astar': 'A*',
            'a-star': 'A*',
            'bfs': 'BFS',
            'breadth first': 'BFS',
            'breadth first search': 'BFS',
            'breadth-first': 'BFS',
            'dfs': 'DFS',
            'depth first': 'DFS',
            'depth first search': 'DFS',
            'depth-first': 'DFS'
        };
        
        return algorithmMap[normalized] || null;
    }
    
    // Suggest similar locations
    suggestLocations(query) {
        const suggestions = CampusData.utils.searchBuildings(query);
        
        if (suggestions.length === 0) {
            return "Try asking for a list of all locations by saying 'list all locations'.";
        }
        
        const suggestionText = suggestions.slice(0, 3).map(s => s.name).join(', ');
        return `Did you mean: ${suggestionText}?`;
    }
    
    // Add message to conversation history
    addMessage(sender, content) {
        const message = {
            id: Date.now() + Math.random(),
            sender: sender,
            content: content,
            timestamp: new Date()
        };
        
        this.conversationHistory.push(message);
        
        // Limit history size
        if (this.conversationHistory.length > 50) {
            this.conversationHistory = this.conversationHistory.slice(-40);
        }
        
        return message;
    }
    
    // Get conversation history
    getHistory() {
        return this.conversationHistory;
    }
    
    // Clear conversation history
    clearHistory() {
        this.conversationHistory = [];
        this.addMessage('bot', this.getWelcomeMessage());
    }
    
    // Get welcome message
    getWelcomeMessage() {
        return "🤖 Hello! I'm your AI navigation assistant for Chanakya University campus. I can help you find the best routes between any locations on campus.\n\nTry asking me something like:\n• \"How do I get from Engineering Center to Library?\"\n• \"Find route to Rec Center\"\n• \"Where is the Student Center?\"\n• \"Tell me about the Sports Complex\"\n\nWhat can I help you with today? 🗺️";
    }
    
    // Get current context
    getContext() {
        return this.context;
    }
    
    // Set context
    setContext(newContext) {
        this.context = { ...this.context, ...newContext };
    }
    
    // Process quick actions
    async processQuickAction(action, data = {}) {
        switch (action) {
            case 'find_route':
                if (data.start && data.end) {
                    const message = `Find route from ${data.start} to ${data.end}`;
                    return await this.processMessage(message);
                }
                break;
                
            case 'compare_algorithms':
                if (data.start && data.end) {
                    const message = `Compare algorithms from ${data.start} to ${data.end}`;
                    return await this.processMessage(message);
                }
                break;
                
            case 'get_info':
                if (data.location) {
                    const message = `Tell me about ${data.location}`;
                    return await this.processMessage(message);
                }
                break;
                
            case 'list_locations':
                return await this.processMessage('List all locations');
                
            default:
                return "I don't understand that action.";
        }
    }
}

// Initialize chatbot
const chatBot = new ChatBot();