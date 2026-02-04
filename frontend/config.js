// API Configuration
// Update this URL based on your backend deployment
const API_CONFIG = {
    BASE_URL: (function() {
        const stored = (typeof window !== 'undefined') ? window.localStorage.getItem('api_base') : null;
        return stored || 'https://examynex-backend.up.railway.app';
    })(),
    
    // Endpoints
    ENDPOINTS: {
        // Auth
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        
        // Users
        USER_ME: '/users/me',
        
        // Exams
        EXAMS: '/exams/',
        EXAM_BY_ID: (id) => `/exams/${id}`,
        EXAM_QUESTIONS: (id) => `/exams/${id}/questions`,
        START_EXAM: (id) => `/exams/${id}/start`,
        
        // Questions
        QUESTIONS: '/questions/',
        QUESTIONS_BY_EXAM: (id) => `/questions/${id}`,
        
        // Submissions
        SAVE_ANSWER: '/submissions/answer',
        SUBMIT_EXAM: '/submissions/submit',
        GET_RESULT: (examId) => `/submissions/${examId}/result`,
        
        // Proctoring
        PROCTOR_START: '/proctor/start',
        PROCTOR_FRAME: '/proctor/frame',
        PROCTOR_ADMIN_REPORT: (examId) => `/proctor/admin/report/${examId}`,
        
        // WebSocket
        WS_ADMIN: '/ws/admin'
    }
};

// Helper function to get full API URL
function getApiUrl(endpoint) {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
}

function setApiBase(url) {
    if (typeof window !== 'undefined') {
        window.localStorage.setItem('api_base', url);
        API_CONFIG.BASE_URL = url;
    }
}

// Helper function to get WebSocket URL
function getWsUrl(endpoint) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const baseUrl = API_CONFIG.BASE_URL.replace(/^https?:/, '');
    return `${wsProtocol}${baseUrl}${endpoint}`;
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, getApiUrl, getWsUrl, setApiBase };
}

