// auth.js — Handles login & register on index.html

document.addEventListener('DOMContentLoaded', () => {
    // If already logged in, skip to dashboard
    if (localStorage.getItem('drpaws_token')) {
        window.location.href = 'dashboard.html';
        return;
    }

    // Tab switching
    const tabs = document.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.dataset.tab;
            loginForm.classList.toggle('hidden', target !== 'login');
            registerForm.classList.toggle('hidden', target !== 'register');
            clearErrors();
        });
    });

    // LOGIN
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = loginForm.querySelector('button[type="submit"]');
        setLoading(btn, true);
        clearErrors();

        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;

        try {
            const res = await api.postForm('/login', { username: email, password });
            const data = await res.json();

            if (!res.ok) {
                showError('login-error', parseError(data) || 'Login failed. Check your credentials.');
                return;
            }

            localStorage.setItem('drpaws_token', data.access_token);
            window.location.href = 'dashboard.html';
        } catch {
            showError('login-error', 'Could not reach the server. Is the backend running?');
        } finally {
            setLoading(btn, false);
        }
    });

    // REGISTER
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = registerForm.querySelector('button[type="submit"]');
        setLoading(btn, true);
        clearErrors();

        const full_name = document.getElementById('reg-name').value.trim();
        const email = document.getElementById('reg-email').value.trim();
        const password = document.getElementById('reg-password').value;
        const confirmPassword = document.getElementById('reg-confirm').value;

        if (password !== confirmPassword) {
            showError('reg-error', 'Passwords do not match.');
            setLoading(btn, false);
            return;
        }

        try {
            const res = await api.post('/users', { full_name, email, password });
            const data = await res.json();

            if (!res.ok) {
                showError('reg-error', parseError(data) || 'Registration failed.');
                return;
            }

            // Auto-login after register
            const loginRes = await api.postForm('/login', { username: email, password });
            const loginData = await loginRes.json();

            if (!loginRes.ok) {
                showError('reg-error', 'Registered! But auto-login failed — please log in manually.');
                document.querySelector('[data-tab="login"]').click();
                return;
            }

            localStorage.setItem('drpaws_token', loginData.access_token);
            window.location.href = 'dashboard.html';
        } catch {
            showError('reg-error', 'Could not reach the server. Is the backend running?');
        } finally {
            setLoading(btn, false);
        }
    });
});

function showError(id, msg) {
    const el = document.getElementById(id);
    if (el) { el.textContent = msg; el.classList.remove('hidden'); }
}

// Handles FastAPI errors — detail can be a string OR an array of Pydantic validation objects
function parseError(data) {
    if (!data || !data.detail) return null;
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) {
        return data.detail.map(e => {
            const field = e.loc ? e.loc[e.loc.length - 1] : '';
            return field ? `${field}: ${e.msg}` : e.msg;
        }).join(' | ');
    }
    return String(data.detail);
}

function clearErrors() {
    document.querySelectorAll('.form-error').forEach(el => {
        el.textContent = '';
        el.classList.add('hidden');
    });
}

function setLoading(btn, loading) {
    btn.disabled = loading;
    btn.innerHTML = loading
        ? '<span class="spinner"></span> Please wait...'
        : btn.dataset.label;
}
