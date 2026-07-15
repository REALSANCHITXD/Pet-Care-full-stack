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