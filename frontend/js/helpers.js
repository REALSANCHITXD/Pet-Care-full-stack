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

function showToast(message, type = 'info') {
    const icons = { success:'✅', error:'❌', info:'ℹ️' };
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type]}</span><span>${escHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 280);
    }, 3200);
}
