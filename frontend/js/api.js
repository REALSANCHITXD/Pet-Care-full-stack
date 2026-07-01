const API_BASE = 'http://localhost:8000';

async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('drpaws_token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
    };

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = 'index.html';
            return null;
        }
        return response;
    } catch (err) {
        console.error(`[API] ${options.method || 'GET'} ${endpoint} failed:`, err);
        throw err;
    }
}

const api = {
    get: (endpoint) =>
        apiFetch(endpoint, { method: 'GET' }),

    post: (endpoint, data) =>
        apiFetch(endpoint, { method: 'POST', body: JSON.stringify(data) }),

    patch: (endpoint, data) =>
        apiFetch(endpoint, { method: 'PATCH', body: JSON.stringify(data) }),

    delete: (endpoint) =>
        apiFetch(endpoint, { method: 'DELETE' }),

    // OAuth2 form-encoded login
    postForm: (endpoint, data) => {
        const token = localStorage.getItem('drpaws_token');
        return fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                ...(token && { 'Authorization': `Bearer ${token}` }),
            },
            body: new URLSearchParams(data),
        });
    },
};
