/**
 * TruthLens API Communication Module
 * Handles all backend API calls
 */

class TruthLensAPI {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.timeout = CONFIG.REQUEST_TIMEOUT;
    }

    /**
     * Make API request with timeout
     */
    async makeRequest(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timed out. The analysis is taking longer than expected.');
            }
            throw error;
        }
    }

    /**
     * Health check - verify backend is running
     */
    async checkHealth() {
        try {
            const response = await this.makeRequest(CONFIG.API_ENDPOINTS.HEALTH, {
                method: 'GET'
            });
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Detect fake news
     */
    async detectFakeNews(title, text) {
        try {
            console.log('📤 Sending request to backend...');
            console.log('Title:', title);
            console.log('Text length:', text.length);

            const response = await this.makeRequest(CONFIG.API_ENDPOINTS.DETECT, {
                method: 'POST',
                body: JSON.stringify({
                    title: title,
                    text: text
                })
            });

            console.log('📥 Received response from backend');
            console.log('Prediction:', response.prediction);
            console.log('Confidence:', response.confidence);

            return {
                success: true,
                data: response
            };
        } catch (error) {
            console.error('❌ API Error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get root endpoint info
     */
    async getInfo() {
        try {
            const response = await this.makeRequest(CONFIG.API_ENDPOINTS.ROOT, {
                method: 'GET'
            });
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Export API instance
const api = new TruthLensAPI();
