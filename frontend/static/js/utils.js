// ExamSphere - Utility Functions

// Standardized Branches
const BRANCHES = ['CSE', 'CSM', 'AIML', 'CAD', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL'];

// Standardized Semesters
const SEMESTERS = ['1', '2', '3', '4', '5', '6', '7', '8'];

// API Base URL - Backend server URL
// Change this if your backend runs on a different port or host
const API_BASE = 'http://localhost:8000/api';

// Utility Functions
const Utils = {
    // Generate branch dropdown options
    generateBranchDropdown: function (selectId, includeAll = false) {
        const select = document.getElementById(selectId);
        if (!select) return;

        select.innerHTML = '';

        if (includeAll) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'All Branches';
            select.appendChild(option);
        }

        BRANCHES.forEach(branch => {
            const option = document.createElement('option');
            option.value = branch;
            option.textContent = branch;
            select.appendChild(option);
        });
    },

    // Generate semester dropdown options
    generateSemesterDropdown: function (selectId, includeAll = false) {
        const select = document.getElementById(selectId);
        if (!select) return;

        select.innerHTML = '';

        if (includeAll) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'All Semesters';
            select.appendChild(option);
        }

        SEMESTERS.forEach(sem => {
            const option = document.createElement('option');
            option.value = sem;
            option.textContent = `Semester ${sem}`;
            select.appendChild(option);
        });
    },

    // Show alert message
    showAlert: function (message, type = 'info', containerId = 'alertContainer') {
        let container = document.getElementById(containerId);
        if (!container) {
            container = document.body;
        }

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.insertBefore(alert, container.firstChild);

        setTimeout(() => {
            alert.remove();
        }, 5000);
    },

    // Format date
    formatDate: function (dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Format time (seconds to MM:SS)
    formatTime: function (seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },

    // API call with authentication token support
    apiCall: async function (endpoint, method = 'GET', data = null, requireAuth = true) {
        try {
            const fullUrl = `${API_BASE}${endpoint}`;
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            // Add authentication token if available and required
            const token = localStorage.getItem('access_token');
            if (token && requireAuth) {
                options.headers['Authorization'] = `Bearer ${token}`;
            }

            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(fullUrl, options);

            // Check if response is ok
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            // Handle empty responses
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return { status: 'success' };
            }
        } catch (error) {
            console.error('API Error:', error);
            Utils.showAlert(error.message || 'An error occurred. Please try again.', 'danger');
            throw error;
        }
    },

    // Store authentication token
    setAuthToken: function (token) {
        localStorage.setItem('access_token', token);
    },

    // Get authentication token
    getAuthToken: function () {
        return localStorage.getItem('access_token');
    },

    // Clear authentication data
    clearAuth: function () {
        localStorage.removeItem('access_token');
        localStorage.removeItem('userRole');
        localStorage.removeItem('username');
        localStorage.removeItem('userId');
    },

    // Check if user is authenticated
    isAuthenticated: function () {
        return !!localStorage.getItem('access_token');
    },

    // Redirect based on role
    redirectByRole: function (role) {
        const routes = {
            'student': '/student/dashboard.html',
            'faculty': '/faculty/dashboard.html',
            'admin': '/admin/dashboard.html'
        };

        if (routes[role]) {
            window.location.href = routes[role];
        }
    },

    // Get user role from localStorage (placeholder)
    getCurrentRole: function () {
        return localStorage.getItem('userRole') || 'student';
    },

    // Set active sidebar menu item
    setActiveMenu: function (menuId) {
        document.querySelectorAll('.sidebar-menu a').forEach(link => {
            link.classList.remove('active');
        });

        const activeLink = document.querySelector(`[data-menu="${menuId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    },

    // Validate form
    validateForm: function (formId) {
        const form = document.getElementById(formId);
        if (!form) return false;

        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        return isValid;
    },

    // Initialize tooltips
    initTooltips: function () {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
}

