/**
 * TruthLens Main Application Logic
 * Handles user interactions and coordinates API + UI
 */

class TruthLensApp {
    constructor() {
        this.isAnalyzing = false;
        this.init();
    }

    /**
     * Initialize app
     */
    async init() {
        console.log('🚀 TruthLens Frontend Initialized');
        
        // Check backend health
        await this.checkBackendHealth();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ App ready');
    }

    /**
     * Check if backend is running
     */
    async checkBackendHealth() {
        console.log('🔍 Checking backend health...');
        
        const result = await api.checkHealth();
        
        if (result.success) {
            console.log('✅ Backend is healthy');
            console.log('Model loaded:', result.data.is_model_loaded);
        } else {
            console.warn('⚠️ Backend health check failed:', result.error);
            console.warn('Make sure backend is running on:', CONFIG.API_BASE_URL);
        }
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Form submission
        const form = document.getElementById('detectionForm');
        form.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Character count
        const textInput = document.getElementById('newsText');
        textInput.addEventListener('input', () => ui.updateCharCount());

        // Sample buttons
        document.querySelectorAll('.btn-sample').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sampleType = e.target.dataset.sample.toUpperCase();
                ui.fillSample(sampleType);
            });
        });

        // Analyze another button
        const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
        analyzeAnotherBtn.addEventListener('click', () => ui.resetToForm());

        // Retry button
        const retryBtn = document.getElementById('retryBtn');
        retryBtn.addEventListener('click', () => ui.resetToForm());

        // Share button (placeholder)
        const shareBtn = document.getElementById('shareBtn');
        shareBtn.addEventListener('click', () => this.handleShare());

        // Tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                ui.filterHighlights(tab);
            });
        });

        console.log('✅ Event listeners setup complete');
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (this.isAnalyzing) {
            console.log('⏳ Analysis already in progress');
            return;
        }

        // Get form data
        const title = document.getElementById('newsTitle').value.trim();
        const text = document.getElementById('newsText').value.trim();

        // Validate inputs
        if (!this.validateInputs(title, text)) {
            return;
        }

        // Start analysis
        this.isAnalyzing = true;
        ui.showLoading();

        try {
            console.log('🔬 Starting analysis...');
            
            const result = await api.detectFakeNews(title, text);
            
            if (result.success) {
                console.log('✅ Analysis successful');
                ui.showResults(result.data);
            } else {
                console.error('❌ Analysis failed:', result.error);
                ui.showError(result.error);
            }
        } catch (error) {
            console.error('❌ Unexpected error:', error);
            ui.showError('An unexpected error occurred. Please try again.');
        } finally {
            this.isAnalyzing = false;
        }
    }

    /**
     * Validate form inputs
     */
    validateInputs(title, text) {
        if (title.length < 5) {
            ui.showError('Title must be at least 5 characters long');
            return false;
        }

        if (title.length > 500) {
            ui.showError('Title must be less than 500 characters');
            return false;
        }

        if (text.length < 20) {
            ui.showError('Article text must be at least 20 characters long');
            return false;
        }

        if (text.length > 10000) {
            ui.showError('Article text must be less than 10,000 characters');
            return false;
        }

        return true;
    }

    /**
     * Handle share button click
     */
    handleShare() {
        if (!CONFIG.FEATURES.SHARE_RESULTS) {
            ui.showToast('Share feature coming soon!', 'info');
            return;
        }

        // Share functionality can be implemented later
        const shareData = {
            title: 'TruthLens Analysis Result',
            text: 'Check out this fake news analysis from TruthLens!',
            url: window.location.href
        };

        if (navigator.share) {
            navigator.share(shareData).catch(() => {
                console.log('Share cancelled');
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(window.location.href);
            ui.showToast('Link copied to clipboard!', 'success');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new TruthLensApp();
    
    // Expose to window for debugging
    window.TruthLens = {
        app,
        api,
        ui,
        config: CONFIG
    };
});
