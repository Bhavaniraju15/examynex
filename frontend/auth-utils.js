/**
 * Authentication Utilities for Token Management
 * Handles token refresh and expiration logic
 */

const AuthUtils = {
    TOKEN_KEY: 'token',
    REFRESH_TOKEN_KEY: 'refreshToken',
    LOGIN_TIME_KEY: 'loginTime',
    
    // Token expiration check (in minutes)
    ACCESS_TOKEN_EXPIRY_MINUTES: 30,
    REFRESH_CHECK_INTERVAL: 25, // Check every 25 minutes
    
    /**
     * Initialize token refresh interval
     * Call this when user logs in
     */
    initTokenRefresh() {
        // Check if token needs refresh every X minutes
        const refreshIntervalId = setInterval(() => {
            this.refreshTokenIfNeeded();
        }, this.REFRESH_CHECK_INTERVAL * 60 * 1000);
        
        // Store interval ID for cleanup
        window.tokenRefreshIntervalId = refreshIntervalId;
        console.log('Token refresh interval initialized');
    },
    
    /**
     * Cleanup token refresh interval
     * Call this when user logs out
     */
    cleanupTokenRefresh() {
        if (window.tokenRefreshIntervalId) {
            clearInterval(window.tokenRefreshIntervalId);
            console.log('Token refresh interval cleared');
        }
    },
    
    /**
     * Check if token needs refresh and refresh if needed
     */
    async refreshTokenIfNeeded() {
        const loginTime = localStorage.getItem(this.LOGIN_TIME_KEY);
        if (!loginTime) return false;
        
        const now = new Date().getTime();
        const elapsedMinutes = (now - parseInt(loginTime)) / (1000 * 60);
        
        // Refresh if more than 20 minutes have passed (before 30-min expiry)
        if (elapsedMinutes > 20) {
            return this.refreshAccessToken();
        }
        
        return true;
    },
    
    /**
     * Refresh access token using refresh token
     */
    async refreshAccessToken() {
        const refreshToken = localStorage.getItem(this.REFRESH_TOKEN_KEY);
        
        if (!refreshToken) {
            this.logout('Session expired. Please login again.');
            return false;
        }
        
        try {
            const response = await fetch(getApiUrl('/auth/refresh'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: refreshToken
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem(this.TOKEN_KEY, data.access_token);
                localStorage.setItem(this.LOGIN_TIME_KEY, new Date().getTime().toString());
                console.log('Token refreshed successfully');
                return true;
            } else {
                console.warn('Token refresh failed:', response.status);
                // If refresh fails, logout user
                this.logout('Session expired. Please login again.');
                return false;
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            this.logout('Network error. Please login again.');
            return false;
        }
    },
    
    /**
     * Get current access token
     */
    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    },
    
    /**
     * Check if user is logged in
     */
    isLoggedIn() {
        return !!localStorage.getItem(this.TOKEN_KEY);
    },
    
    /**
     * Logout user and redirect to login
     */
    logout(message = null) {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.REFRESH_TOKEN_KEY);
        localStorage.removeItem(this.LOGIN_TIME_KEY);
        localStorage.removeItem('role');
        
        this.cleanupTokenRefresh();
        
        if (message) {
            alert(message);
        }
        
        window.location.href = 'login.html';
    },
    
    /**
     * Wrapper for fetch with automatic token refresh
     */
    async fetchWithTokenRefresh(url, options = {}) {
        // Refresh token if needed before making request
        await this.refreshTokenIfNeeded();
        
        // Add auth header
        const token = this.getToken();
        if (token) {
            if (!options.headers) {
                options.headers = {};
            }
            options.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(url, options);
        
        // If 401 Unauthorized, try refreshing token once
        if (response.status === 401) {
            const refreshed = await this.refreshAccessToken();
            if (refreshed) {
                // Retry request with new token
                const newToken = this.getToken();
                if (!options.headers) {
                    options.headers = {};
                }
                options.headers['Authorization'] = `Bearer ${newToken}`;
                return fetch(url, options);
            }
        }
        
        return response;
    }
};

// Auto-initialize on page load if user is logged in
document.addEventListener('DOMContentLoaded', () => {
    if (AuthUtils.isLoggedIn()) {
        AuthUtils.initTokenRefresh();
    }
});
