/**
 * TruthLens UI Update Module
 * Handles all DOM updates and animations
 */

class TruthLensUI {
    constructor() {
        this.currentTab = 'all';
        this.currentResults = null;
    }

    /**
     * Show loading state with animated messages
     */
    showLoading() {
        const form = document.getElementById('detectionForm');
        const loading = document.getElementById('loadingState');
        const results = document.getElementById('resultsSection');
        const error = document.getElementById('errorState');

        form.classList.add('hidden');
        results.classList.add('hidden');
        error.classList.add('hidden');
        loading.classList.remove('hidden');

        // Animate loading messages
        let messageIndex = 0;
        const loadingStep = document.getElementById('loadingStep');
        
        const messageInterval = setInterval(() => {
            messageIndex = (messageIndex + 1) % CONFIG.UI.LOADING_MESSAGES.length;
            loadingStep.textContent = CONFIG.UI.LOADING_MESSAGES[messageIndex];
        }, 30000); // Change message every 30 seconds

        // Store interval ID for cleanup
        this.loadingInterval = messageInterval;
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
            this.loadingInterval = null;
        }
    }

    /**
     * Show results section with animation
     */
    showResults(data) {
        this.hideLoading();
        this.currentResults = data;

        const form = document.getElementById('detectionForm');
        const loading = document.getElementById('loadingState');
        const results = document.getElementById('resultsSection');
        const error = document.getElementById('errorState');

        form.classList.add('hidden');
        loading.classList.add('hidden');
        error.classList.add('hidden');
        results.classList.remove('hidden');

        // Update all result elements
        this.updateResultHeader(data);
        this.updateProbabilityBars(data);
        this.updateExplanation(data);
        this.updateWordHighlights(data);
        this.updateMetadata(data);

        // Scroll to results
        results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * Update result header (prediction badge)
     */
    updateResultHeader(data) {
        const badge = document.getElementById('resultBadge');
        const badgeIcon = document.getElementById('badgeIcon');
        const badgeText = document.getElementById('badgeText');
        const confidenceValue = document.getElementById('confidenceValue');

        const isFake = data.prediction === 'Fake';
        
        // Update badge
        badge.className = `result-badge ${isFake ? 'fake' : 'real'}`;
        badgeIcon.textContent = isFake ? '⚠️' : '✅';
        badgeText.textContent = isFake ? 'Fake News Detected' : 'Likely Credible';
        
        // Update confidence
        confidenceValue.textContent = `${(data.confidence * 100).toFixed(1)}%`;
    }

    /**
     * Update probability bars with animation
     */
    updateProbabilityBars(data) {
        const fakeProbValue = document.getElementById('fakeProbValue');
        const realProbValue = document.getElementById('realProbValue');
        const fakeProbBar = document.getElementById('fakeProbBar');
        const realProbBar = document.getElementById('realProbBar');

        const fakePercent = (data.fake_probability * 100).toFixed(1);
        const realPercent = (data.real_probability * 100).toFixed(1);

        // Update values
        fakeProbValue.textContent = `${fakePercent}%`;
        realProbValue.textContent = `${realPercent}%`;

        // Animate bars
        setTimeout(() => {
            fakeProbBar.style.width = `${fakePercent}%`;
            realProbBar.style.width = `${realPercent}%`;
        }, 100);
    }

    /**
     * Update explanation with typing effect
     */
    updateExplanation(data) {
        const explanationText = document.getElementById('explanationText');
        const text = data.explanation;

        explanationText.textContent = ''; // Clear previous

        // Typing effect
        let index = 0;
        const typeInterval = setInterval(() => {
            if (index < text.length) {
                explanationText.textContent += text.charAt(index);
                index++;
            } else {
                clearInterval(typeInterval);
            }
        }, CONFIG.UI.TYPING_DELAY);
    }

    /**
     * Update word highlights
     */
    updateWordHighlights(data) {
        const highlightsGrid = document.getElementById('highlightsGrid');
        const highlights = data.word_highlights || [];

        highlightsGrid.innerHTML = '';

        if (highlights.length === 0) {
            highlightsGrid.innerHTML = '<p class="text-center" style="grid-column: 1/-1; color: var(--text-tertiary);">No word highlights available</p>';
            return;
        }

        highlights.forEach((item, index) => {
            const highlightItem = document.createElement('div');
            highlightItem.className = `highlight-item ${item.direction}`;
            highlightItem.style.animationDelay = `${index * 0.05}s`;
            
            const importance = (item.importance * 100).toFixed(1);
            
            highlightItem.innerHTML = `
                <span class="highlight-word">${this.escapeHtml(item.word)}</span>
                <div class="highlight-score">
                    <span class="score-badge">${importance}%</span>
                    <span>${item.direction === 'fake' ? '❌' : '✅'}</span>
                </div>
            `;

            // Filter based on current tab
            if (this.currentTab === 'all' || this.currentTab === item.direction) {
                highlightItem.style.display = 'flex';
            } else {
                highlightItem.style.display = 'none';
            }

            highlightsGrid.appendChild(highlightItem);
        });
    }

    /**
     * Filter word highlights by tab
     */
    filterHighlights(tab) {
        this.currentTab = tab;
        
        if (!this.currentResults) return;

        const highlightItems = document.querySelectorAll('.highlight-item');
        
        highlightItems.forEach(item => {
            const direction = item.classList.contains('fake') ? 'fake' : 'real';
            
            if (tab === 'all' || tab === direction) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });

        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.dataset.tab === tab) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    /**
     * Update metadata section
     */
    updateMetadata(data) {
        const processingTime = document.getElementById('processingTime');
        const requestId = document.getElementById('requestId');
        const timestamp = document.getElementById('timestamp');

        // Processing time in seconds
        const timeInSeconds = (data.processing_time_ms / 1000).toFixed(1);
        processingTime.textContent = `${timeInSeconds}s`;

        // Request ID
        requestId.textContent = data.request_id.substring(0, 13) + '...';
        requestId.title = data.request_id; // Full ID on hover

        // Timestamp
        const date = new Date(data.timestamp);
        timestamp.textContent = date.toLocaleString();
    }

    /**
     * Show error state
     */
    showError(message) {
        this.hideLoading();

        const form = document.getElementById('detectionForm');
        const loading = document.getElementById('loadingState');
        const results = document.getElementById('resultsSection');
        const error = document.getElementById('errorState');
        const errorMessage = document.getElementById('errorMessage');

        form.classList.add('hidden');
        loading.classList.add('hidden');
        results.classList.add('hidden');
        error.classList.remove('hidden');

        errorMessage.textContent = message;

        // Scroll to error
        error.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * Reset to form view
     */
    resetToForm() {
        this.hideLoading();

        const form = document.getElementById('detectionForm');
        const loading = document.getElementById('loadingState');
        const results = document.getElementById('resultsSection');
        const error = document.getElementById('errorState');

        form.classList.remove('hidden');
        loading.classList.add('hidden');
        results.classList.add('hidden');
        error.classList.add('hidden');

        // Clear form
        document.getElementById('newsTitle').value = '';
        document.getElementById('newsText').value = '';
        document.getElementById('charCount').textContent = '0 / 10,000';

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Fill form with sample data
     */
    fillSample(type) {
        const sample = CONFIG.SAMPLES[type];
        
        if (!sample) return;

        const titleInput = document.getElementById('newsTitle');
        const textInput = document.getElementById('newsText');

        titleInput.value = sample.title;
        textInput.value = sample.text;

        // Update character count
        this.updateCharCount();

        // Smooth scroll to text area
        textInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Update character count
     */
    updateCharCount() {
        const textInput = document.getElementById('newsText');
        const charCount = document.getElementById('charCount');
        const length = textInput.value.length;
        
        charCount.textContent = `${length.toLocaleString()} / 10,000`;
        
        // Change color based on length
        if (length > 10000) {
            charCount.style.color = 'var(--fake-red)';
        } else if (length > 8000) {
            charCount.style.color = 'var(--text-secondary)';
        } else {
            charCount.style.color = 'var(--text-tertiary)';
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show toast notification (for future features)
     */
    showToast(message, type = 'info') {
        console.log(`Toast: ${message} (${type})`);
        // Can implement custom toast notifications later
    }
}

// Export UI instance
const ui = new TruthLensUI();
