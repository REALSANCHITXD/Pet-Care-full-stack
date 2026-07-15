/* ============================================================
   Dr. Paws — Common Logic (Auth, Nav, Helpers)
   ============================================================ */

const state = {
    user: null,
    cartItems: [],
};

document.addEventListener('DOMContentLoaded', async () => {
    if (!localStorage.getItem('drpaws_token')) {
        window.location.href = 'index.html';
        return;
    }
    await loadUser();
    setupNav();
});

// ══════════════════════════════════════════════════════════
// USER & AUTH
// ══════════════════════════════════════════════════════════
async function loadUser() {
    try {
        const res = await api.get('/users/me');
        if (!res) return;
        if (res.ok) {
            state.user = await res.json();
        } else {
            const token = localStorage.getItem('drpaws_token');
            const payload = JSON.parse(atob(token.split('.')[1]));
            state.user = { id: payload.user_id, role: payload.role, subscription_tier: 'free', name: 'User', email: '' };
            const res2 = await api.get(`/users/${payload.user_id}`);
            if (res2 && res2.ok) state.user = await res2.json();
        }
    } catch {
        const token = localStorage.getItem('drpaws_token');
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            state.user = { id: payload.user_id, role: payload.role, subscription_tier: 'free', name: 'User', email: '' };
        } catch { logout(); return; }
    }
    renderUserInfo();
}

function renderUserInfo() {
    const u = state.user;
    if (!u) return;
    const name = u.name || u.email || 'User';
    const initials = name.slice(0, 2).toUpperCase();

    const avatarEl = document.getElementById('user-avatar');
    if (avatarEl) avatarEl.textContent = initials;
    const nameEl = document.getElementById('user-name');
    if (nameEl) nameEl.textContent = name;
    const emailEl = document.getElementById('user-email');
    if (emailEl) emailEl.textContent = u.email || '';

    const isPremium = u.subscription_tier === 'premium';
    const premiumBadge = document.getElementById('premium-badge-wrap');
    if (premiumBadge) premiumBadge.classList.toggle('hidden', !isPremium);
    const upgradeLink = document.getElementById('upgrade-link-wrap');
    if (upgradeLink) upgradeLink.classList.toggle('hidden', isPremium);
    
    // Set active nav based on pathname
    const currentPath = window.location.pathname.split('/').pop().replace('.html', '') || 'store';
    document.querySelectorAll('.nav-item').forEach(b => {
        b.classList.toggle('active', b.dataset.tab === currentPath);
    });
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) logoutBtn.addEventListener('click', logout);

// ══════════════════════════════════════════════════════════
// NAVIGATION
// ══════════════════════════════════════════════════════════
function setupNav() {
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            window.location.href = `${tab}.html`;
        });
    });
}

// ══════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ══════════════════════════════════════════════════════════
function showToast(message, type = 'info') {
    const icons = { success:'✅', error:'❌', info:'ℹ️' };
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type]}</span><span>${escHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 280);
    }, 3200);
}

// ══════════════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════════════
function renderStars(rating) {
    if (!rating) return '☆☆☆☆☆';
    const r = Math.round(Number(rating));
    return '⭐'.repeat(Math.min(r, 5)) + '☆'.repeat(Math.max(5 - r, 0));
}

function formatDate(iso) {
    if (!iso) return '';
    try {
        return new Date(iso).toLocaleString('en-IN', {
            day:'numeric', month:'short', year:'numeric',
            hour:'2-digit', minute:'2-digit',
        });
    } catch { return iso; }
}

function escHtml(str) {
    if (str == null) return '';
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
