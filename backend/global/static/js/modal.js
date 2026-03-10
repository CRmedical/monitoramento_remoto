const hospitalsData = JSON.parse(document.getElementById('hospitalsData').textContent);

    function applyStatusClass(el, value) {
        el.classList.remove('status-ligado','status-standby','status-desligado','status-default');
        if (value === null || value === undefined) {
            el.textContent = '—';
            el.classList.add('status-default');
            return;
        }
        const v = String(value).toLowerCase();
        el.textContent = value;
        if (v === 'ligado')        el.classList.add('status-ligado');
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

    function openModal(index) {
        const d = hospitalsData[index];
        if (!d) return;

        document.getElementById('modalHospitalName').textContent = d.hospital ?? '—';

        // Compressores
        applyStatusClass(document.getElementById('statusC1'), d.C1);
        applyStatusClass(document.getElementById('statusC2'), d.C2);

        // Flags opcionais
        setFlag('flagBE',   'valBE',   d.BE);
        setFlag('flagRST',  'valRST',  d.RST);
        setFlag('flagAuto', 'valAuto', d.auto);
        setFlag('flagRede', 'valRede', d.rede);

        // Sempre presentes
        document.getElementById('mPressure').textContent = d.pressure  ?? '—';
        document.getElementById('mDewPoint').textContent = d.dew_point ?? '—';

        // Opcionais — aparecem somente se o dado existir
        setOptional('cardVacuo',           'mVacuo',           d.vacuo);
        setOptional('cardProductPressure', 'mProductPressure', d.product_pressure);
        setOptional('cardPurity',          'mPurity',          d.purity);

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