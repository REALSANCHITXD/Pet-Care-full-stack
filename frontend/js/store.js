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
    const hasFilters = !!category;
    let url = hasFilters ? `/products/search?category=${encodeURIComponent(category)}` : '/products';
    try {
        const res = await api.get(url);
        if (!res || !res.ok) { showToast('Could not load products.', 'error'); return; }
        state.products = await res.json();
        initPriceSlider(state.products);
        renderProducts(state.products);
    } catch { showToast('Server error loading products.', 'error'); }
}

function togglePricePopup() {
    const popup = document.getElementById('price-popup');
    popup.classList.toggle('open');
}

function closePricePopup() {
    document.getElementById('price-popup').classList.remove('open');
}

// Close popup when clicking anywhere outside
document.addEventListener('click', e => {
    const wrap = document.getElementById('price-filter-wrap');
    if (wrap && !wrap.contains(e.target)) closePricePopup();
});

function initPriceSlider(products) {
    if (!products || products.length === 0) return;
    const prices = products.map(p => Number(p.price));
    const minPrice = Math.floor(Math.min(...prices));
    const maxPrice = Math.ceil(Math.max(...prices));

    const sliderMin = document.getElementById('price-slider-min');
    const sliderMax = document.getElementById('price-slider-max');
    if (!sliderMin || !sliderMax) return;

    sliderMin.min = minPrice;  sliderMin.max = maxPrice;  sliderMin.value = minPrice;
    sliderMax.min = minPrice;  sliderMax.max = maxPrice;  sliderMax.value = maxPrice;
    updateSliderUI(minPrice, maxPrice, minPrice, maxPrice);
    // Reset pill label
    document.getElementById('price-pill-label').textContent = 'Price';
    document.getElementById('price-pill-btn').classList.remove('active');
}

function resetPriceFilter() {
    const sliderMin = document.getElementById('price-slider-min');
    const sliderMax = document.getElementById('price-slider-max');
    if (sliderMin && sliderMax) {
        sliderMin.value = sliderMin.min;
        sliderMax.value = sliderMax.max;
        updateSliderUI(Number(sliderMin.min), Number(sliderMax.max), Number(sliderMin.min), Number(sliderMax.max));
    }
    document.getElementById('price-pill-label').textContent = 'Price';
    document.getElementById('price-pill-btn').classList.remove('active');
    closePricePopup();
    renderProducts(state.products);
}

function onPriceSlide() {
    const sliderMin = document.getElementById('price-slider-min');
    const sliderMax = document.getElementById('price-slider-max');
    let minVal = Number(sliderMin.value);
    let maxVal = Number(sliderMax.value);

    // Prevent thumbs from crossing
    if (minVal > maxVal) {
        if (event.target === sliderMin) { sliderMin.value = maxVal; minVal = maxVal; }
        else { sliderMax.value = minVal; maxVal = minVal; }
    }

    updateSliderUI(Number(sliderMin.min), Number(sliderMin.max), minVal, maxVal);

    // Filter client-side instantly
    const filtered = state.products.filter(p => p.price >= minVal && p.price <= maxVal);
    renderProducts(filtered);

    // Update pill label to show active range
    const isFullRange = minVal == Number(sliderMin.min) && maxVal == Number(sliderMax.max);
    const pillLabel = document.getElementById('price-pill-label');
    const pillBtn = document.getElementById('price-pill-btn');
    if (!isFullRange) {
        pillLabel.textContent = `₹${minVal}–₹${maxVal}`;
        pillBtn.classList.add('active');
    } else {
        pillLabel.textContent = 'Price';
        pillBtn.classList.remove('active');
    }
}

function updateSliderUI(absMin, absMax, minVal, maxVal) {
    document.getElementById('price-popup-range').textContent = `₹${minVal} – ₹${maxVal}`;
    const range = absMax - absMin || 1;
    const leftPct  = ((minVal - absMin) / range) * 100;
    const rightPct = ((absMax - maxVal) / range) * 100;
    const fill = document.getElementById('price-track-fill');
    if (fill) { fill.style.left = leftPct + '%'; fill.style.right = rightPct + '%'; }
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