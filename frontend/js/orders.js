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