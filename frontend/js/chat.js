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