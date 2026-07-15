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