/**
 * TruthLens Frontend Configuration
 * API endpoints and app settings
 */

const CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://localhost:8000',  // Backend URL
    API_ENDPOINTS: {
        DETECT: '/api/detect',
        HEALTH: '/api/health',
        ROOT: '/'
    },
    
    // Request Configuration
    REQUEST_TIMEOUT: 600000,  // 10 minutes (for SHAP analysis)
    
    // Sample Articles
    SAMPLES: {
        FAKE: {
            title: "BREAKING: Scientists Discover Miracle Cure That Doctors Don't Want You to Know",
            text: "Amazing breakthrough that medical establishment is trying to hide from the public. Anonymous sources reveal shocking truth about secret treatment. Government officials refuse to comment. Share this before they delete it! Mainstream media won't report this incredible discovery."
        },
        REAL: {
            title: "London's Canary Wharf Docklands Light Railway station reopens after fire alert",
            text: "Transport for London confirmed that Canary Wharf DLR station has reopened following a brief closure due to a fire alert earlier today. The station was evacuated as a precautionary measure while fire services investigated. No injuries were reported and normal service has now resumed."
        }
    },
    
    // UI Configuration
    UI: {
        LOADING_MESSAGES: [
            'Running AI model prediction...',
            'Analyzing text patterns...',
            'Generating word importance scores...',
            'Creating human-readable explanation...'
        ],
        TYPING_DELAY: 50,  // Typing animation speed (ms)
        ANIMATION_DURATION: 500  // General animation duration (ms)
    },
    
    // Feature Flags (for future features)
    FEATURES: {
        SHARE_RESULTS: true,
        DOWNLOAD_REPORT: false,
        HISTORY: false
    }
};

// Freeze config to prevent modifications
Object.freeze(CONFIG);
