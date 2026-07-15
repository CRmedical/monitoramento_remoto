// ─── State ────────────────────────────────────────────────────────────────────
let hospitalsIndex = [];   // [{ key, ...data }, ...]  populado após fetch
let pollingInterval = null;

// ─── Helpers de status ────────────────────────────────────────────────────────
function applyStatusClass(el, value) {
    el.classList.remove('status-ligado', 'status-standby', 'status-desligado', 'status-default');
    if (value === null || value === undefined) {
        el.textContent = '—';
        el.classList.add('status-default');
        return;
    }
    const v = String(value).toLowerCase();
    el.textContent = value;
    if      (v === 'ligado')   el.classList.add('status-ligado');
    else if (v === 'stand-by') el.classList.add('status-standby');
    else if (v === 'desligado')el.classList.add('status-desligado');
    else                       el.classList.add('status-default');
}

function setOptional(cardId, spanId, value) {
    const card = document.getElementById(cardId);
    const span = document.getElementById(spanId);
    const exists = value !== null && value !== undefined;
    card.style.display = exists ? 'flex' : 'none';
    if (exists) span.textContent = value;
}

function setFlag(badgeId, valId, value) {
    const badge = document.getElementById(badgeId);
    const exists = value !== null && value !== undefined;
    badge.style.display = exists ? 'flex' : 'none';
    if (exists) document.getElementById(valId).textContent = value;
}

// ─── Modal ────────────────────────────────────────────────────────────────────
function openModal(index) {
    const d = hospitalsIndex[index];
    if (!d) return;

    document.getElementById('modalHospitalName').textContent = d.hospital ?? d.key ?? '—';

    applyStatusClass(document.getElementById('statusC1'), d.C1);
    applyStatusClass(document.getElementById('statusC2'), d.C2);

    setFlag('flagBE',   'valBE',   d.BE);
    setFlag('flagRST',  'valRST',  d.RST);
    setFlag('flagAuto', 'valAuto', d.auto);
    
    document.getElementById('mPressure').textContent = d.pressure  ?? '—';
    document.getElementById('mDewPoint').textContent = d.dew_point ?? '—';
    
    setOptional('cardVacuo',           'mVacuo',           d.vacuo);
    setOptional('cardProductPressure', 'mProductPressure', d.product_pressure);
    setOptional('cardPurity',          'mPurity',          d.purity);
    setOptional('cardRede', 'mRede', d.rede);
    setOptional('cardAcumulado', 'mAcumulado', d.accumulated);
    // setOptional('cardVazao', 'mVazao', d.flow);


    document.getElementById('hospitalModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('hospitalModal').classList.remove('active');
    document.body.style.overflow = '';
}

function closeModalOnOverlay(e) {
    if (e.target === document.getElementById('hospitalModal')) closeModal();
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// ─── Render dos cards ─────────────────────────────────────────────────────────
function renderCards(locais) {
    const container = document.getElementById('hospitalCards');
    if (!container) return;

    // Normaliza para array preservando a key (nome do local)
    hospitalsIndex = Object.entries(locais).map(([key, val]) => ({ key, ...val }));

    container.innerHTML = '';

    hospitalsIndex.forEach((data, index) => {
        const card = document.createElement('a');
        card.className = 'hospital_card';
        card.setAttribute('data-index', index);
        card.addEventListener('click', () => openModal(index));

        card.innerHTML = `
            <div class="hospital_name">${data.hospital ?? data.key}</div>
            <div class="hospital_pressure">
                ${data.pressure ?? '—'}
                <span>bar</span>
            </div>
        `;
        container.appendChild(card);
    });
}

// ─── Fetch & Polling ──────────────────────────────────────────────────────────
async function fetchData() {
    try {
        const res = await fetch(window.ALL_DATA_URL, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        renderCards(json.locais ?? {});
    } catch (err) {
        console.error('[Dashboard] Erro ao buscar dados:', err);
    }
}

function startPolling(intervalMs = 10000) {
    fetchData();                                   // busca imediata
    pollingInterval = setInterval(fetchData, intervalMs);
}

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // window.ALL_DATA_URL é injetado no template (ver dashboard.html)
    if (!window.ALL_DATA_URL) {
        console.error('[Dashboard] window.ALL_DATA_URL não definida.');
        return;
    }
    startPolling(5_000); 
});