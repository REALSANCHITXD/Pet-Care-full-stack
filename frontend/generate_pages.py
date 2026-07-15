import os

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Dr. Paws — {title}</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🐾</text></svg>" />
    <link rel="stylesheet" href="css/main.css" />
    {extra_head}
</head>
<body>

<div class="dashboard">
    <!-- ═══════════════ SIDEBAR ═══════════════ -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">🐾</div>
            <span class="sidebar-logo-text">Dr. Paws</span>
        </div>

        <div class="sidebar-section-label">Menu</div>
        <nav>
            <button class="nav-item" data-tab="store" id="nav-store" onclick="window.location.href='store.html'">
                <span class="nav-icon">🛒</span> Pet Store
            </button>
            <button class="nav-item" data-tab="vets" id="nav-vets" onclick="window.location.href='vets.html'">
                <span class="nav-icon">🏥</span> Vet Finder
            </button>
            <button class="nav-item" data-tab="chat" id="nav-chat" onclick="window.location.href='chat.html'">
                <span class="nav-icon">🤖</span> AI Chat
            </button>
            <button class="nav-item" data-tab="orders" id="nav-orders" onclick="window.location.href='orders.html'">
                <span class="nav-icon">📦</span> My Orders
            </button>
            <button class="nav-item" data-tab="pets" id="nav-pets" onclick="window.location.href='pets.html'">
                <span class="nav-icon">🐾</span> My Pets
            </button>
        </nav>

        <div class="sidebar-section-label" style="margin-top:16px">Account</div>
        <button class="nav-item" data-tab="settings" id="nav-settings" onclick="window.location.href='settings.html'">
            <span class="nav-icon">⚙️</span> Settings
        </button>

        <div class="sidebar-spacer"></div>

        <div class="sidebar-user">
            <div class="user-info">
                <div class="user-avatar" id="user-avatar">?</div>
                <div>
                    <div class="user-name" id="user-name">Loading...</div>
                    <div class="user-email" id="user-email"></div>
                </div>
            </div>
            <!-- Premium badge -->
            <div id="premium-badge-wrap" class="hidden" style="margin-bottom:8px">
                <span class="premium-badge">✨ Premium</span>
            </div>
            <!-- Upgrade link -->
            <div id="upgrade-link-wrap" style="margin-bottom:8px">
                <button class="upgrade-link" onclick="window.location.href='settings.html'">⬆ Upgrade →</button>
            </div>
            <button class="logout-btn" id="logout-btn">
                <span>🚪</span> Log out
            </button>
        </div>
    </aside>

    <!-- ═══════════════ MAIN CONTENT ═══════════════ -->
    <div class="main-content">
        <!-- Header -->
        <header class="main-header">
            <h1 id="header-title">{title}</h1>
        </header>

        <div class="tab-content" id="page-content">
            {content}
        </div>
    </div>
</div>

{extra_body}

<div class="toast-container" id="toast-container"></div>
<script src="js/api.js"></script>
<script src="js/common.js"></script>
<script src="js/{name}.js"></script>
</body>
</html>
"""

PAGES = [
    {
        "name": "vets",
        "title": "Vet Finder",
        "extra_head": """<!-- Leaflet.js -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>""",
        "content": """
            <section class="tab-section active" id="tab-vets">
                <div class="section-heading"><span>🏥</span> Vet Finder</div>
                <div class="vet-filter-bar">
                    <input type="text" class="vet-filter-input" id="vet-specialty-filter" placeholder="Filter by specialty (e.g. Surgery)" />
                    <button class="btn-filter" onclick="filterVets()">Filter</button>
                    <button class="btn-filter" style="background:var(--bg-card);border:1px solid var(--border-light);color:var(--text-secondary)" onclick="loadVets()">Reset</button>
                </div>
                <div class="vet-layout">
                    <div id="vet-map"></div>
                    <div class="vet-panel-area">
                        <div class="vet-cards-list" id="vet-cards-list">
                            <div class="loading-skeleton" style="height:100px;border-radius:16px"></div>
                            <div class="loading-skeleton" style="height:100px;border-radius:16px"></div>
                        </div>
                        <!-- Slide-over panel -->
                        <div class="vet-slideover" id="vet-slideover">
                            <div class="slideover-header">
                                <button class="close-btn" onclick="closeVetPanel()">✕</button>
                                <div class="vet-detail-avatar" id="so-avatar">🩺</div>
                                <div>
                                    <div class="vet-detail-name" id="so-name"></div>
                                    <div class="vet-detail-clinic" id="so-clinic"></div>
                                </div>
                                <div style="margin-left:auto;text-align:right">
                                    <div class="stars" id="so-stars"></div>
                                    <div style="font-size:0.8rem;font-weight:700;color:var(--accent-amber)" id="so-rating"></div>
                                </div>
                            </div>
                            <div class="slideover-body">
                                <div class="detail-row">
                                    <span class="detail-icon">📍</span>
                                    <div>
                                        <div class="detail-label">Address</div>
                                        <div class="detail-value" id="so-address"></div>
                                    </div>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-icon">🔬</span>
                                    <div>
                                        <div class="detail-label">Specialties</div>
                                        <div class="detail-value" id="so-specialties"></div>
                                    </div>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-icon">📍</span>
                                    <div>
                                        <div class="detail-label">Coordinates</div>
                                        <div class="detail-value" id="so-coords"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="slideover-footer">
                                <button class="btn-book" id="so-book-btn">📅 Book Appointment</button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        """,
        "extra_body": """
<div class="modal-overlay" id="booking-modal">
    <div class="modal">
        <div class="modal-header">
            <h2>📅 Book Appointment</h2>
            <button class="close-btn" onclick="closeBookingModal()">✕</button>
        </div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label">Appointment Date & Time</label>
                <input type="datetime-local" id="booking-datetime" class="form-input" />
            </div>
            <div class="form-group">
                <label class="form-label">Reason for visit</label>
                <input type="text" id="booking-reason" class="form-input" placeholder="e.g. Annual checkup, limping, vaccination..." />
            </div>
            <p class="text-sm text-muted">Vet: <strong id="booking-vet-name">—</strong></p>
        </div>
        <div class="modal-footer">
            <button class="btn-secondary" onclick="closeBookingModal()">Cancel</button>
            <button class="btn-primary" style="flex:1" onclick="confirmBooking()">Confirm Booking</button>
        </div>
    </div>
</div>
        """
    },
    {
        "name": "chat",
        "title": "AI Vet Assistant",
        "extra_head": "",
        "extra_body": "",
        "content": """
            <section class="tab-section active" id="tab-chat">
                <div class="section-heading"><span>🤖</span> AI Vet Assistant</div>
                <div class="chat-layout">
                    <!-- Session sidebar -->
                    <div class="chat-sidebar">
                        <div class="chat-sidebar-header">
                            <h3>Sessions</h3>
                            <button class="btn-new-chat" id="new-session-btn">+ New</button>
                        </div>
                        <div class="session-list" id="session-list">
                            <div style="padding:16px;color:var(--text-muted);font-size:0.8rem">Loading sessions...</div>
                        </div>
                    </div>
                    <!-- Main chat -->
                    <div class="chat-main">
                        <div class="chat-top-bar">
                            <div class="bot-info">
                                <div class="bot-avatar">🐾</div>
                                <div>
                                    <div class="bot-name">Dr. Paws AI</div>
                                    <div class="bot-status">Online</div>
                                </div>
                            </div>
                            <div class="query-counter hidden" id="query-counter">
                                <span class="used" id="queries-used">0</span> / 5 today
                            </div>
                        </div>
                        <!-- Limit banner -->
                        <div class="limit-banner hidden" id="limit-banner">
                            <p>🔒 You've reached your 5 free messages for today.</p>
                            <button class="btn-upgrade" onclick="window.location.href='settings.html'">⬆ Upgrade</button>
                        </div>
                        <div class="messages-area" id="messages-area">
                            <div style="text-align:center;padding:40px;color:var(--text-muted)">
                                <div style="font-size:2.5rem;margin-bottom:12px">🐾</div>
                                <p style="font-size:0.9rem">Select a session or start a new chat!</p>
                            </div>
                        </div>
                        <div class="chat-input-area">
                            <div class="chat-input-wrap">
                                <textarea id="chat-input" placeholder="Ask Dr. Paws anything about your pet..." rows="1"></textarea>
                            </div>
                            <button class="btn-send" id="send-btn" disabled>➤</button>
                        </div>
                    </div>
                </div>
            </section>
        """
    },
    {
        "name": "orders",
        "title": "My Orders",
        "extra_head": "",
        "extra_body": "",
        "content": """
            <section class="tab-section active" id="tab-orders">
                <div class="section-heading"><span>📦</span> My Orders</div>
                <div class="orders-grid" id="orders-grid">
                    <div class="loading-skeleton" style="height:120px;border-radius:16px"></div>
                    <div class="loading-skeleton" style="height:120px;border-radius:16px"></div>
                </div>
            </section>
        """
    },
    {
        "name": "pets",
        "title": "My Pets",
        "extra_head": "",
        "content": """
            <section class="tab-section active" id="tab-pets">
                <div class="section-heading"><span>🐾</span> My Pets</div>
                <div class="pets-grid" id="pets-grid">
                    <div class="loading-skeleton" style="height:200px;border-radius:16px"></div>
                </div>
            </section>
        """,
        "extra_body": """
<div class="modal-overlay" id="add-pet-modal">
    <div class="modal">
        <div class="modal-header">
            <h2>🐾 Add a Pet</h2>
            <button class="close-btn" onclick="closeAddPetModal()">✕</button>
        </div>
        <div class="modal-body">
            <div class="form-group">
                <label class="form-label">Pet Name</label>
                <input type="text" id="pet-name" class="form-input" placeholder="e.g. Buddy" />
            </div>
            <div class="form-group">
                <label class="form-label">Species</label>
                <input type="text" id="pet-species" class="form-input" placeholder="e.g. Dog, Cat, Rabbit..." />
            </div>
            <div class="form-group">
                <label class="form-label">Breed</label>
                <input type="text" id="pet-breed" class="form-input" placeholder="e.g. Golden Retriever" />
            </div>
            <div class="form-group">
                <label class="form-label">Age (years)</label>
                <input type="number" id="pet-age" class="form-input" placeholder="e.g. 3" min="0" step="0.5" />
            </div>
            <div class="form-group">
                <label class="form-label">Medical History (optional)</label>
                <input type="text" id="pet-history" class="form-input" placeholder="e.g. Allergic to pollen..." />
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn-secondary" onclick="closeAddPetModal()">Cancel</button>
            <button class="btn-primary" style="flex:1" onclick="submitAddPet()">Add Pet 🐾</button>
        </div>
    </div>
</div>
        """
    },
    {
        "name": "settings",
        "title": "Settings & Account",
        "extra_head": "",
        "extra_body": "",
        "content": """
            <section class="tab-section active" id="tab-settings">
                <div class="section-heading"><span>⚙️</span> Settings & Account</div>
                <div class="settings-card">
                    <h2>Account Info</h2>
                    <div class="setting-row">
                        <span class="setting-label">Name</span>
                        <span class="setting-value" id="settings-name">—</span>
                    </div>
                    <div class="setting-row">
                        <span class="setting-label">Email</span>
                        <span class="setting-value" id="settings-email">—</span>
                    </div>
                    <div class="setting-row">
                        <span class="setting-label">Plan</span>
                        <span class="setting-value" id="settings-plan">Free</span>
                    </div>
                </div>

                <!-- Edit Profile Card -->
                <div class="settings-card" style="margin-top:16px">
                    <h2>Edit Profile</h2>
                    <div class="form-group" style="margin-top:12px">
                        <label class="form-label" for="edit-name">Full Name</label>
                        <input type="text" id="edit-name" class="form-input" placeholder="Enter new name" />
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="edit-password">New Password</label>
                        <input type="password" id="edit-password" class="form-input" placeholder="Leave blank to keep current" />
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="edit-confirm-password">Confirm New Password</label>
                        <input type="password" id="edit-confirm-password" class="form-input" placeholder="Repeat new password" />
                    </div>
                    <button class="btn-primary" id="save-profile-btn" onclick="saveProfile()" style="margin-top:8px;width:100%">
                        Save Changes
                    </button>
                </div>

                <div class="upgrade-banner" id="upgrade-banner">
                    <h2>✨ Upgrade to Premium</h2>
                    <p>Unlock the full Dr. Paws experience.</p>
                    <ul class="upgrade-features">
                        <li>Unlimited AI Vet Chatbot queries</li>
                        <li>Priority veterinary appointments</li>
                        <li>Free instant delivery on the Pet Store</li>
                        <li>Exclusive Premium badge</li>
                    </ul>
                    <button class="btn-go-premium">🌟 Go Premium — ₹299/month</button>
                </div>
            </section>
        """
    }
]

for page in PAGES:
    filename = f"{page['name']}.html"
    content = TEMPLATE.format(**page)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

print("Generated all pages!")
