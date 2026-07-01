/* ============================================================
   Dr. Paws — Dashboard Orchestrator
   Handles: Store, Vet Finder, AI Chat, Orders, Pets, Settings
   ============================================================ */

// ── Global State ──────────────────────────────────────────
const state = {
    user: null,
    currentTab: 'store',
    products: [],
    activeCategory: '',
    cartItems: [],
    vets: [],
    selectedVet: null,
    sessions: [],
    currentSessionId: null,
    freeMessageCount: 0,
    FREE_LIMIT: 5,
    isWaitingForBot: false,
    mapInstance: null,
    mapMarkers: [],
    bookingVetId: null,
};

// ── Boot ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    if (!localStorage.getItem('drpaws_token')) {
        window.location.href = 'index.html';
        return;
    }
    await loadUser();
    setupNav();
    setupChatInput();
    setupSearch();
    await loadProducts();
    await loadCart();
});

// ══════════════════════════════════════════════════════════
// USER & AUTH
// ══════════════════════════════════════════════════════════
async function loadUser() {
    try {
        const res = await api.get('/users/me');
        if (!res) return;
        // Try /users/me first; if not found, try /users
        if (res.ok) {
            state.user = await res.json();
        } else {
            // Fallback: get from token payload
            const token = localStorage.getItem('drpaws_token');
            const payload = JSON.parse(atob(token.split('.')[1]));
            state.user = { id: payload.user_id, role: payload.role, subscription_tier: 'free', name: 'User', email: '' };
            // Try fetching by id
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

    document.getElementById('user-avatar').textContent = initials;
    document.getElementById('user-name').textContent = name;
    document.getElementById('user-email').textContent = u.email || '';

    const isPremium = u.subscription_tier === 'premium';
    document.getElementById('premium-badge-wrap').classList.toggle('hidden', !isPremium);
    document.getElementById('upgrade-link-wrap').classList.toggle('hidden', isPremium);

    // Settings tab
    document.getElementById('settings-name').textContent = name;
    document.getElementById('settings-email').textContent = u.email || '—';
    document.getElementById('settings-plan').textContent = isPremium ? '✨ Premium' : 'Free';
    document.getElementById('upgrade-banner').classList.toggle('hidden', isPremium);

    // Free tier query counter
    if (!isPremium) {
        document.getElementById('query-counter').classList.remove('hidden');
    }
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}
document.getElementById('logout-btn').addEventListener('click', logout);

// ══════════════════════════════════════════════════════════
// NAVIGATION
// ══════════════════════════════════════════════════════════
function setupNav() {
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

function switchTab(tab) {
    state.currentTab = tab;
    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
    // Show/hide sections
    document.querySelectorAll('.tab-section').forEach(s => s.classList.toggle('active', s.id === `tab-${tab}`));

    // Update header title
    const titles = { store:'Pet Store', vets:'Vet Finder', chat:'AI Vet Assistant', orders:'My Orders', pets:'My Pets', settings:'Settings' };
    document.getElementById('header-title').textContent = titles[tab] || '';

    // Cart button only on store
    document.getElementById('cart-btn').classList.toggle('hidden', tab !== 'store');
    document.getElementById('search-bar-wrap').classList.toggle('hidden', tab !== 'store');

    // Lazy-load tab data
    if (tab === 'vets' && state.vets.length === 0) initVetFinder();
    if (tab === 'chat' && state.sessions.length === 0) loadSessions();
    if (tab === 'orders') loadOrders();
    if (tab === 'pets') loadPets();
}

// ══════════════════════════════════════════════════════════
// STORE
// ══════════════════════════════════════════════════════════
function setupSearch() {
    const input = document.getElementById('search-input');
    input.addEventListener('input', () => {
        const q = input.value.toLowerCase();
        const filtered = state.products.filter(p =>
            p.name.toLowerCase().includes(q) ||
            (p.description && p.description.toLowerCase().includes(q))
        );
        renderProducts(filtered);
    });
}

async function loadProducts(category = '') {
    state.activeCategory = category;
    let url = '/products';
    if (category) url += `?category=${encodeURIComponent(category)}`;
    try {
        const res = await api.get(url);
        if (!res || !res.ok) { showToast('Could not load products.', 'error'); return; }
        state.products = await res.json();
        renderProducts(state.products);
    } catch { showToast('Server error loading products.', 'error'); }
}

function renderProducts(products) {
    const grid = document.getElementById('product-grid');
    if (!products || products.length === 0) {
        grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🛍️</div><p>No products found.</p></div>`;
        return;
    }
    grid.innerHTML = products.map(p => `
        <div class="product-card">
            <div class="product-img">
                ${getCategoryEmoji(p.category)}
                ${p.stock <= 0 ? '<div class="out-of-stock-overlay">OUT OF STOCK</div>' : ''}
                <span class="instant-badge">⚡ Instant</span>
            </div>
            <div class="product-info">
                <div class="product-name">${escHtml(p.name)}</div>
                <div class="product-price">₹${Number(p.price).toFixed(2)}</div>
                <div class="product-rating">
                    <span class="stars">${renderStars(p.rating)}</span>
                    ${p.rating ? ` ${Number(p.rating).toFixed(1)}` : ''}
                </div>
                <button class="btn-add-cart" onclick="addToCart(${p.id})" ${p.stock <= 0 ? 'disabled' : ''}>
                    🛒 Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

// Category pills
document.getElementById('category-pills').addEventListener('click', e => {
    const pill = e.target.closest('.pill');
    if (!pill) return;
    document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    loadProducts(pill.dataset.category);
});

function getCategoryEmoji(cat) {
    const map = { food:'🍖', medicine:'💊', toys:'🎾', grooming:'🛁', accessories:'🏷️' };
    return `<span style="font-size:3.5rem">${map[(cat||'').toLowerCase()] || '🐾'}</span>`;
}

// ══════════════════════════════════════════════════════════
// CART
// ══════════════════════════════════════════════════════════
async function loadCart() {
    try {
        const res = await api.get('/cart');
        if (!res || !res.ok) return;
        const data = await res.json();
        state.cartItems = data.items || [];
        updateCartCount();
    } catch { /* silent */ }
}

function updateCartCount() {
    document.getElementById('cart-count').textContent = state.cartItems.length;
}

async function addToCart(productId) {
    try {
        const res = await api.post('/cart', { product_id: productId, quantity: 1 });
        if (!res || !res.ok) {
            const err = res ? await res.json() : {};
            showToast(err.detail || 'Failed to add to cart.', 'error'); return;
        }
        await loadCart();
        showToast('Added to cart! 🛒', 'success');
    } catch { showToast('Server error.', 'error'); }
}

function openCartDrawer() {
    renderCartDrawer();
    document.getElementById('cart-overlay').classList.add('open');
    document.getElementById('cart-drawer').classList.add('open');
}

function closeCartDrawer() {
    document.getElementById('cart-overlay').classList.remove('open');
    document.getElementById('cart-drawer').classList.remove('open');
}

function renderCartDrawer() {
    const list = document.getElementById('cart-items-list');
    const footer = document.getElementById('cart-footer');

    if (state.cartItems.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="empty-icon">🛒</div><p>Your cart is empty.</p></div>`;
        footer.style.display = 'none';
        return;
    }

    list.innerHTML = state.cartItems.map(item => `
        <div class="cart-item">
            <span class="cart-item-icon">${getCategoryEmojiRaw(item.product_name || '')}</span>
            <div class="cart-item-info">
                <div class="cart-item-name">${escHtml(item.product_name || `Product #${item.product_id}`)}</div>
                <div class="cart-item-price">₹${Number(item.subtotal || item.price || 0).toFixed(2)}</div>
                <div class="cart-item-qty">Qty: ${item.quantity}</div>
            </div>
            <button class="remove-item-btn" onclick="removeFromCart(${item.id})" title="Remove">✕</button>
        </div>
    `).join('');

    const total = state.cartItems.reduce((sum, i) => sum + (Number(i.subtotal) || 0), 0);
    document.getElementById('cart-total').textContent = `₹${total.toFixed(2)}`;
    footer.style.display = 'block';
}

async function removeFromCart(itemId) {
    try {
        const res = await api.delete(`/cart/items/${itemId}`);
        if (!res || !res.ok) return;
        await loadCart();
        renderCartDrawer();
        showToast('Item removed.', 'info');
    } catch { /* silent */ }
}

async function placeOrder() {
    const address = document.getElementById('shipping-address').value.trim();
    if (!address) { showToast('Please enter a shipping address.', 'error'); return; }

    const btn = document.getElementById('checkout-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Placing order...';

    try {
        const res = await api.post('/orders/checkout', { shipping_address: address });
        if (!res) return;
        const data = await res.json();
        if (!res.ok) { showToast(data.detail || 'Checkout failed.', 'error'); return; }

        state.cartItems = [];
        updateCartCount();
        closeCartDrawer();
        showToast('Order placed successfully! 🎉', 'success');
        document.getElementById('shipping-address').value = '';
    } catch { showToast('Server error during checkout.', 'error'); }
    finally {
        btn.disabled = false;
        btn.innerHTML = '⚡ Place Order';
    }
}

function getCategoryEmojiRaw(name) {
    const n = name.toLowerCase();
    if (n.includes('food') || n.includes('treat') || n.includes('kibble')) return '🍖';
    if (n.includes('medicine') || n.includes('tablet') || n.includes('vaccine')) return '💊';
    if (n.includes('toy') || n.includes('ball') || n.includes('rope')) return '🎾';
    if (n.includes('shampoo') || n.includes('brush') || n.includes('groom')) return '🛁';
    return '🐾';
}

// ══════════════════════════════════════════════════════════
// VET FINDER
// ══════════════════════════════════════════════════════════
async function initVetFinder() {
    initMap();
    await loadVets();
}

function initMap() {
    if (state.mapInstance) return;
    state.mapInstance = L.map('vet-map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(state.mapInstance);
}

async function loadVets() {
    try {
        const res = await api.get('/vets');
        if (!res || !res.ok) { showToast('Could not load vets.', 'error'); return; }
        state.vets = await res.json();
        renderVetCards(state.vets);
        renderVetMarkers(state.vets);
    } catch { showToast('Server error loading vets.', 'error'); }
}

async function filterVets() {
    const specialty = document.getElementById('vet-specialty-filter').value.trim();
    if (!specialty) { loadVets(); return; }
    try {
        const res = await api.get(`/vets/search/specialties?specialties=${encodeURIComponent(specialty)}&clinic_name=`);
        if (!res || !res.ok) { showToast('Filter failed.', 'error'); return; }
        const vets = await res.json();
        state.vets = vets;
        renderVetCards(vets);
        renderVetMarkers(vets);
    } catch { showToast('Server error.', 'error'); }
}

function renderVetCards(vets) {
    const list = document.getElementById('vet-cards-list');
    if (!vets || vets.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="empty-icon">🏥</div><p>No vets found.</p></div>`;
        return;
    }
    list.innerHTML = vets.map(v => `
        <div class="vet-card" onclick="openVetPanel(${v.id})">
            <div class="vet-card-top">
                <div class="vet-avatar">🩺</div>
                <div>
                    <div class="vet-name">${escHtml(v.name)}</div>
                    <div class="vet-clinic">${escHtml(v.clinic_name || '')}</div>
                </div>
                <div class="vet-rating">
                    <div class="stars">${renderStars(v.rating)}</div>
                    <div class="score">${v.rating ? Number(v.rating).toFixed(1) : '—'}</div>
                </div>
            </div>
            <div class="vet-specialties">
                ${(v.specialties || '').split(',').filter(Boolean).map(s =>
                    `<span class="specialty-tag">${escHtml(s.trim())}</span>`
                ).join('')}
            </div>
        </div>
    `).join('');
}

function renderVetMarkers(vets) {
    if (!state.mapInstance) return;
    // Clear old markers
    state.mapMarkers.forEach(m => m.remove());
    state.mapMarkers = [];

    const validVets = vets.filter(v => v.latitude && v.longitude);
    validVets.forEach(v => {
        const marker = L.circleMarker([v.latitude, v.longitude], {
            radius: 10,
            fillColor: '#06b6d4',
            color: '#fff',
            weight: 2,
            fillOpacity: 0.85,
        }).addTo(state.mapInstance);

        marker.bindPopup(`
            <div class="vet-map-popup">
                <h3>🩺 ${escHtml(v.name)}</h3>
                <p>${escHtml(v.clinic_name || '')} • ⭐ ${v.rating || '—'}</p>
                <button class="popup-view-btn" onclick="openVetPanel(${v.id})">View & Book</button>
            </div>
        `);
        state.mapMarkers.push(marker);
    });

    if (validVets.length > 0) {
        const group = L.featureGroup(state.mapMarkers);
        state.mapInstance.fitBounds(group.getBounds().pad(0.2));
    }
}

function openVetPanel(vetId) {
    const vet = state.vets.find(v => v.id === vetId);
    if (!vet) return;
    state.selectedVet = vet;

    document.getElementById('so-name').textContent = vet.name;
    document.getElementById('so-clinic').textContent = vet.clinic_name || '';
    document.getElementById('so-rating').textContent = vet.rating ? `${Number(vet.rating).toFixed(1)} ⭐` : 'No rating';
    document.getElementById('so-stars').innerHTML = renderStars(vet.rating);
    document.getElementById('so-address').textContent = vet.address || 'Address not available';
    document.getElementById('so-specialties').textContent = vet.specialties || 'General Practice';
    document.getElementById('so-coords').textContent = vet.latitude && vet.longitude
        ? `${Number(vet.latitude).toFixed(4)}, ${Number(vet.longitude).toFixed(4)}`
        : 'Not available';

    document.getElementById('so-book-btn').onclick = () => openBookingModal(vet);
    document.getElementById('vet-slideover').classList.add('open');

    // Fly to marker on map
    if (vet.latitude && vet.longitude && state.mapInstance) {
        state.mapInstance.flyTo([vet.latitude, vet.longitude], 14, { duration: 1 });
    }
}

function closeVetPanel() {
    document.getElementById('vet-slideover').classList.remove('open');
    state.selectedVet = null;
}

function openBookingModal(vet) {
    state.bookingVetId = vet.id;
    document.getElementById('booking-vet-name').textContent = `${vet.name} — ${vet.clinic_name || ''}`;
    // Set min datetime to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('booking-datetime').min = now.toISOString().slice(0,16);
    document.getElementById('booking-modal').classList.add('open');
}

function closeBookingModal() {
    document.getElementById('booking-modal').classList.remove('open');
}

async function confirmBooking() {
    const dateTime = document.getElementById('booking-datetime').value;
    const reason = document.getElementById('booking-reason').value.trim();
    if (!dateTime) { showToast('Please select a date and time.', 'error'); return; }
    if (!state.user) return;

    try {
        const res = await api.post('/bookings', {
            user_id: state.user.id,
            vet_id: state.bookingVetId,
            appointment_time: new Date(dateTime).toISOString(),
            reason: reason || 'General consultation',
        });
        if (!res) return;
        const data = await res.json();
        if (!res.ok) { showToast(data.detail || 'Booking failed.', 'error'); return; }
        closeBookingModal();
        closeVetPanel();
        showToast('Appointment booked! 🏥', 'success');
    } catch { showToast('Server error.', 'error'); }
}

// ══════════════════════════════════════════════════════════
// AI CHAT
// ══════════════════════════════════════════════════════════
function setupChatInput() {
    const textarea = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        sendBtn.disabled = !textarea.value.trim() || !state.currentSessionId || state.isWaitingForBot;
    });

    textarea.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) sendMessage();
        }
    });

    document.getElementById('new-session-btn').addEventListener('click', createSession);
    document.getElementById('send-btn').addEventListener('click', sendMessage);
}

async function loadSessions() {
    try {
        const res = await api.get('/chat/sessions');
        if (!res || !res.ok) return;
        state.sessions = await res.json();
        renderSessionList();
    } catch { /* silent */ }
}

function renderSessionList() {
    const list = document.getElementById('session-list');
    if (state.sessions.length === 0) {
        list.innerHTML = `<div style="padding:16px;color:var(--text-muted);font-size:0.8rem">No sessions yet. Start a new chat!</div>`;
        return;
    }
    list.innerHTML = state.sessions.map((s, i) => `
        <div class="session-item ${s.id === state.currentSessionId ? 'active' : ''}"
             onclick="selectSession(${s.id})">
            💬 Chat ${i + 1}
            <div class="session-date">${formatDate(s.started_at)}</div>
        </div>
    `).join('');
}

async function createSession() {
    try {
        const res = await api.post('/chat/session', {});
        if (!res || !res.ok) { showToast('Could not create session.', 'error'); return; }
        const session = await res.json();
        state.sessions.unshift(session);
        renderSessionList();
        selectSession(session.id);
    } catch { showToast('Server error.', 'error'); }
}

async function selectSession(sessionId) {
    state.currentSessionId = sessionId;
    renderSessionList();
    await loadMessages(sessionId);
    document.getElementById('send-btn').disabled = false;
}

async function loadMessages(sessionId) {
    try {
        const res = await api.get(`/chat/session/${sessionId}/history`);
        if (!res || !res.ok) return;
        const messages = await res.json();
        renderMessages(messages);
        updateFreeCounter();
    } catch { /* silent */ }
}

function renderMessages(messages) {
    const area = document.getElementById('messages-area');
    if (!messages || messages.length === 0) {
        area.innerHTML = `
            <div style="text-align:center;padding:40px;color:var(--text-muted)">
                <div style="font-size:2.5rem;margin-bottom:12px">🐾</div>
                <p style="font-size:0.9rem">Hi! I'm Dr. Paws. Ask me anything about your pet's health.</p>
            </div>`;
        return;
    }
    area.innerHTML = messages.map(m => buildMessageBubble(m)).join('');
    area.scrollTop = area.scrollHeight;
}

function buildMessageBubble(m) {
    const isUser = m.sender === 'user';
    return `
        <div class="message-row ${isUser ? 'user' : ''}">
            <div class="msg-avatar ${isUser ? 'user' : 'bot'}">${isUser ? '👤' : '🐾'}</div>
            <div>
                <div class="message-bubble ${isUser ? 'user' : 'bot'}">${escHtml(m.message).replace(/\n/g,'<br>')}</div>
                <div class="msg-time ${isUser ? 'text-right' : ''}">${formatDate(m.sent_at)}</div>
            </div>
        </div>`;
}

async function sendMessage() {
    const textarea = document.getElementById('chat-input');
    const text = textarea.value.trim();
    if (!text || !state.currentSessionId || state.isWaitingForBot) return;

    // Check free limit
    const isPremium = state.user?.subscription_tier === 'premium';
    if (!isPremium && state.freeMessageCount >= state.FREE_LIMIT) {
        document.getElementById('limit-banner').classList.remove('hidden');
        return;
    }

    textarea.value = '';
    textarea.style.height = 'auto';
    document.getElementById('send-btn').disabled = true;
    state.isWaitingForBot = true;

    // Optimistically add user bubble
    appendMessageBubble({ sender: 'user', message: text, sent_at: new Date().toISOString() });
    showTypingIndicator();

    try {
        const res = await api.post('/chat/message', { session_id: state.currentSessionId, message: text });

        hideTypingIndicator();
        if (!res) return;

        if (res.status === 429) {
            document.getElementById('limit-banner').classList.remove('hidden');
            state.freeMessageCount = state.FREE_LIMIT;
            updateFreeCounter();
            return;
        }

        const data = await res.json();
        if (!res.ok) { showToast(data.detail || 'Chat error.', 'error'); return; }

        appendMessageBubble(data.bot_reply);
        state.freeMessageCount++;
        updateFreeCounter();
    } catch { hideTypingIndicator(); showToast('Server error.', 'error'); }
    finally {
        state.isWaitingForBot = false;
        document.getElementById('send-btn').disabled = false;
    }
}

function appendMessageBubble(m) {
    const area = document.getElementById('messages-area');
    // Remove placeholder if present
    const placeholder = area.querySelector('[style*="text-align:center"]');
    if (placeholder) placeholder.remove();

    const div = document.createElement('div');
    div.innerHTML = buildMessageBubble(m);
    area.appendChild(div.firstElementChild);
    area.scrollTop = area.scrollHeight;
}

function showTypingIndicator() {
    const area = document.getElementById('messages-area');
    const el = document.createElement('div');
    el.id = 'typing-indicator';
    el.className = 'message-row';
    el.innerHTML = `
        <div class="msg-avatar bot">🐾</div>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>`;
    area.appendChild(el);
    area.scrollTop = area.scrollHeight;
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator')?.remove();
}

function updateFreeCounter() {
    const isPremium = state.user?.subscription_tier === 'premium';
    if (isPremium) return;
    const counter = document.getElementById('query-counter');
    const usedEl = document.getElementById('queries-used');
    counter.classList.remove('hidden');
    usedEl.textContent = state.freeMessageCount;

    if (state.freeMessageCount >= state.FREE_LIMIT) {
        document.getElementById('limit-banner').classList.remove('hidden');
    }
}

// ══════════════════════════════════════════════════════════
// ORDERS
// ══════════════════════════════════════════════════════════
async function loadOrders() {
    const grid = document.getElementById('orders-grid');
    try {
        const res = await api.get('/orders');
        if (!res) return;
        if (res.status === 404) {
            grid.innerHTML = `<div class="empty-state"><div class="empty-icon">📦</div><p>No orders yet. Go shop something!</p></div>`;
            return;
        }
        if (!res.ok) return;
        const orders = await res.json();
        renderOrders(orders);
    } catch { grid.innerHTML = `<div class="empty-state"><div class="empty-icon">📦</div><p>Could not load orders.</p></div>`; }
}

function renderOrders(orders) {
    const grid = document.getElementById('orders-grid');
    if (!orders || orders.length === 0) {
        grid.innerHTML = `<div class="empty-state"><div class="empty-icon">📦</div><p>No orders yet!</p></div>`;
        return;
    }
    grid.innerHTML = orders.map(o => {
        const statusKey = (o.status || 'pending').replace(/\s+/g, '_').toLowerCase();
        const statusLabel = { pending:'Pending', out_for_delivery:'Out for Delivery', delivered:'Delivered', cancelled:'Cancelled' };
        const statusIcons = { pending:'🟡', out_for_delivery:'🔵', delivered:'✅', cancelled:'🔴' };
        const steps = ['pending','out_for_delivery','delivered'];
        const currentStep = steps.indexOf(statusKey);

        return `
        <div class="order-card">
            <div class="order-header">
                <div>
                    <div class="order-id">Order #${o.id}</div>
                    <div class="order-date">${formatDate(o.created_at)}</div>
                </div>
                <div style="text-align:right">
                    <span class="status-chip ${statusKey}">${statusIcons[statusKey] || ''} ${statusLabel[statusKey] || o.status}</span>
                    <div class="order-total" style="margin-top:4px">₹${Number(o.total_amount || 0).toFixed(2)}</div>
                </div>
            </div>
            <div class="order-body">
                ${(o.items || []).map(item => `
                    <div class="order-item">
                        <span class="order-item-icon">${getCategoryEmojiRaw(item.product_id?.toString() || '')}</span>
                        <span class="order-item-name">Product #${item.product_id} × ${item.quantity}</span>
                        <span class="order-item-price">₹${Number(item.price_at_purchase * item.quantity).toFixed(2)}</span>
                    </div>
                `).join('')}
                <div style="font-size:0.78rem;color:var(--text-muted);margin-top:8px">📍 ${escHtml(o.shipping_address || 'N/A')}</div>
                ${statusKey !== 'cancelled' ? `
                <div class="delivery-timeline">
                    ${steps.map((step, i) => `
                        <div class="timeline-step">
                            ${i > 0 ? `<div class="timeline-line ${i <= currentStep ? 'done' : ''}"></div>` : ''}
                            <div class="timeline-dot ${i < currentStep ? 'done' : i === currentStep ? 'current' : ''}">
                                ${i < currentStep ? '✓' : i + 1}
                            </div>
                            <div class="timeline-label">${statusLabel[step]}</div>
                        </div>
                    `).join('')}
                </div>` : ''}
            </div>
        </div>`;
    }).join('');
}

// ══════════════════════════════════════════════════════════
// MY PETS
// ══════════════════════════════════════════════════════════
async function loadPets() {
    const grid = document.getElementById('pets-grid');
    try {
        const res = await api.get('/pets');
        if (!res || !res.ok) {
            grid.innerHTML = '';
            renderAddPetCard();
            return;
        }
        const pets = await res.json();
        renderPets(pets);
    } catch {
        grid.innerHTML = '';
        renderAddPetCard();
    }
}

function renderPets(pets) {
    const grid = document.getElementById('pets-grid');
    const speciesEmoji = { dog:'🐶', cat:'🐱', rabbit:'🐰', bird:'🐦', fish:'🐟', hamster:'🐹' };

    grid.innerHTML = pets.map(p => `
        <div class="pet-card">
            <div class="pet-emoji">${speciesEmoji[(p.species||'').toLowerCase()] || '🐾'}</div>
            <div class="pet-card-name">${escHtml(p.name)}</div>
            <div class="pet-card-species">${escHtml(p.species || '—')}</div>
            <div class="pet-card-breed">${escHtml(p.breed || '')}</div>
            <div class="pet-card-age">${p.age ? `${p.age} yrs old` : ''}</div>
            ${p.medical_history ? `<div class="pet-history">📋 ${escHtml(p.medical_history)}</div>` : ''}
        </div>
    `).join('');

    renderAddPetCard();
}

function renderAddPetCard() {
    const grid = document.getElementById('pets-grid');
    const card = document.createElement('div');
    card.className = 'add-pet-card';
    card.onclick = openAddPetModal;
    card.innerHTML = `<div class="add-icon">➕</div><span>Add a Pet</span>`;
    grid.appendChild(card);
}

function openAddPetModal() {
    document.getElementById('add-pet-modal').classList.add('open');
}
function closeAddPetModal() {
    document.getElementById('add-pet-modal').classList.remove('open');
}

async function submitAddPet() {
    const name = document.getElementById('pet-name').value.trim();
    const species = document.getElementById('pet-species').value.trim();
    const breed = document.getElementById('pet-breed').value.trim();
    const age = parseFloat(document.getElementById('pet-age').value) || null;
    const history = document.getElementById('pet-history').value.trim();

    if (!name || !species) { showToast('Name and species are required.', 'error'); return; }
    if (!state.user) return;

    try {
        const res = await api.post('/pets', {
            owner_id: state.user.id,
            name, species,
            breed: breed || null,
            age: age,
            medical_history: history || null,
        });
        if (!res) return;
        const data = await res.json();
        if (!res.ok) { showToast(data.detail || 'Could not add pet.', 'error'); return; }
        closeAddPetModal();
        showToast(`${name} added! 🐾`, 'success');
        ['pet-name','pet-species','pet-breed','pet-age','pet-history'].forEach(id => {
            document.getElementById(id).value = '';
        });
        await loadPets();
    } catch { showToast('Server error.', 'error'); }
}

// ══════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ══════════════════════════════════════════════════════════
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

// ══════════════════════════════════════════════════════════
// SETTINGS — EDIT PROFILE
// ══════════════════════════════════════════════════════════
async function saveProfile() {
    const name     = document.getElementById('edit-name').value.trim();
    const password = document.getElementById('edit-password').value;
    const confirm  = document.getElementById('edit-confirm-password').value;

    if (!name && !password) {
        showToast('Fill in at least one field to update.', 'error');
        return;
    }
    if (password && password !== confirm) {
        showToast('Passwords do not match.', 'error');
        return;
    }
    if (password && password.length < 6) {
        showToast('Password must be at least 6 characters.', 'error');
        return;
    }

    const payload = {};
    if (name)     payload.full_name = name;
    if (password) payload.password  = password;

    const btn = document.getElementById('save-profile-btn');
    btn.disabled = true;
    btn.textContent = 'Saving...';

    try {
        const res = await api.patch(`/users/${state.user.id}`, payload);
        if (!res) return;
        const data = await res.json();
        if (!res.ok) { showToast(data.detail || 'Update failed.', 'error'); return; }

        // Refresh user in state and re-render
        state.user = data;
        renderUserInfo();
        document.getElementById('edit-name').value = '';
        document.getElementById('edit-password').value = '';
        document.getElementById('edit-confirm-password').value = '';
        showToast('Profile updated successfully!', 'success');
    } catch { showToast('Server error.', 'error'); }
    finally {
        btn.disabled = false;
        btn.textContent = 'Save Changes';
    }
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
