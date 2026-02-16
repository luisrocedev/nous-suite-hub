const state = {
  modules: [],
  suites: [],
  currentSuiteId: null,
  currentDetail: null,
};

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error(data.error || 'Error API');
  }
  return data;
}

function money(value) {
  return `${Number(value).toFixed(2)} €/mes`;
}

function renderKpis(overview) {
  const container = $('kpis');
  container.innerHTML = '';
  const items = [
    `Módulos: ${overview.modules}`,
    `Suites: ${overview.suites}`,
    `Simulaciones: ${overview.runs}`,
  ];
  items.forEach((text) => {
    const el = document.createElement('div');
    el.className = 'kpi';
    el.textContent = text;
    container.appendChild(el);
  });
}

function renderCatalog() {
  const list = $('module-list');
  const familyFilter = $('family-filter').value;
  list.innerHTML = '';

  const filtered = state.modules.filter((module) =>
    familyFilter === 'all' ? true : module.family === familyFilter
  );

  filtered.forEach((module) => {
    const selected = state.currentDetail?.modules?.some((m) => m.id === module.id);
    const row = document.createElement('article');
    row.className = 'module-item';
    row.innerHTML = `
      <input type="checkbox" data-module-id="${module.id}" ${selected ? 'checked' : ''}>
      <div>
        <strong>${module.name}</strong>
        <div class="module-pill">${module.family} · ${module.business_area}</div>
        <div>${module.description}</div>
        <small>Coste: ${money(module.monthly_cost)} · Valor: ${module.value_score} · Complejidad: ${module.complexity_score}</small>
      </div>
    `;
    list.appendChild(row);
  });
}

function renderFamilyFilter(families) {
  const filter = $('family-filter');
  filter.innerHTML = '<option value="all">Todas las familias</option>';
  families.forEach((family) => {
    const opt = document.createElement('option');
    opt.value = family;
    opt.textContent = family;
    filter.appendChild(opt);
  });
}

function renderSuites() {
  const list = $('suite-list');
  list.innerHTML = '';

  state.suites.forEach((suite) => {
    const card = document.createElement('article');
    card.className = 'suite-item' + (suite.id === state.currentSuiteId ? ' active' : '');
    card.innerHTML = `
      <strong>${suite.name}</strong>
      <div>${suite.mission}</div>
      <small>Módulos: ${suite.metrics.moduleCount} · Coste: ${money(suite.metrics.totalCost)}</small>
    `;
    card.addEventListener('click', () => loadSuiteDetail(suite.id));
    list.appendChild(card);
  });
}

function renderSuiteDetail() {
  const empty = $('detail-empty');
  const box = $('suite-detail');

  if (!state.currentDetail) {
    empty.classList.remove('hidden');
    box.classList.add('hidden');
    return;
  }

  empty.classList.add('hidden');
  box.classList.remove('hidden');

  const suite = state.currentDetail.suite;
  const metrics = state.currentDetail.metrics;
  $('suite-title').innerHTML = `<strong>${suite.name}</strong><div>${suite.mission}</div><small>Responsable: ${suite.owner}</small>`;

  $('suite-metrics').innerHTML = `
    <div class="metric"><strong>Módulos</strong><div>${metrics.moduleCount}</div></div>
    <div class="metric"><strong>Coste total</strong><div>${money(metrics.totalCost)}</div></div>
    <div class="metric"><strong>Valor agregado</strong><div>${metrics.totalValue}</div></div>
    <div class="metric"><strong>Complejidad media</strong><div>${metrics.avgComplexity}</div></div>
  `;

  renderRuns(state.currentRuns || []);
  renderCatalog();
}

function renderRuns(runs) {
  const list = $('run-list');
  list.innerHTML = '';

  if (!runs.length) {
    list.innerHTML = '<div class="empty">Todavía no hay simulaciones para esta suite.</div>';
    return;
  }

  runs.forEach((run) => {
    const statusClass = run.status === 'ok' ? 'ok' : 'warning';
    const card = document.createElement('article');
    card.className = 'run-item';
    card.innerHTML = `
      <div><span class="status ${statusClass}">${run.status.toUpperCase()}</span> · ${new Date(run.created_at).toLocaleString()}</div>
      <div>ROI estimado: <strong>${run.summary.estimatedROI.toFixed(2)} €</strong></div>
      <div>Esfuerzo integración: ${run.summary.integrationEffort}</div>
      <small>${run.summary.recommendation}</small>
    `;
    list.appendChild(card);
  });
}

async function loadOverview() {
  const data = await api('/api/overview');
  renderKpis(data.overview);
}

async function loadCatalog() {
  const data = await api('/api/catalog');
  state.modules = data.modules;
  renderFamilyFilter(data.families);
  renderCatalog();
}

async function loadSuites() {
  const data = await api('/api/suites');
  state.suites = data.items;
  renderSuites();

  if (!state.currentSuiteId && state.suites.length) {
    await loadSuiteDetail(state.suites[0].id);
  }
}

async function loadSuiteDetail(suiteId) {
  const data = await api(`/api/suites/${suiteId}`);
  state.currentSuiteId = suiteId;
  state.currentDetail = data.detail;
  state.currentRuns = data.runs;
  renderSuites();
  renderSuiteDetail();
}

function selectedModuleIdsFromUI() {
  const checks = Array.from(document.querySelectorAll('[data-module-id]:checked'));
  return checks.map((el) => Number(el.dataset.moduleId));
}

async function saveSuiteModules() {
  if (!state.currentSuiteId) return;
  const ids = selectedModuleIdsFromUI();
  await api(`/api/suites/${state.currentSuiteId}/modules`, {
    method: 'POST',
    body: JSON.stringify({ moduleIds: ids }),
  });
  await loadSuiteDetail(state.currentSuiteId);
  await loadSuites();
}

async function simulateSuite() {
  if (!state.currentSuiteId) return;
  await api(`/api/suites/${state.currentSuiteId}/simulate`, { method: 'POST' });
  await loadSuiteDetail(state.currentSuiteId);
  await loadOverview();
}

async function createSuite() {
  const name = $('suite-name').value.trim();
  const owner = $('suite-owner').value.trim() || 'Equipo DAM2';
  const mission = $('suite-mission').value.trim();

  if (!name || !mission) {
    alert('Indica nombre y misión de la suite.');
    return;
  }

  const data = await api('/api/suites', {
    method: 'POST',
    body: JSON.stringify({ name, owner, mission }),
  });

  $('suite-name').value = '';
  $('suite-owner').value = '';
  $('suite-mission').value = '';

  await loadSuites();
  await loadSuiteDetail(data.suiteId);
  await loadOverview();
}

async function boot() {
  $('family-filter').addEventListener('change', renderCatalog);
  $('btn-reload').addEventListener('click', async () => {
    await loadOverview();
    await loadCatalog();
    await loadSuites();
  });
  $('btn-create-suite').addEventListener('click', createSuite);
  $('btn-save-links').addEventListener('click', saveSuiteModules);
  $('btn-simulate').addEventListener('click', simulateSuite);

  await loadOverview();
  await loadCatalog();
  await loadSuites();
  renderSuiteDetail();
}

boot().catch((err) => {
  console.error(err);
  $('detail-empty').textContent = `Error al cargar: ${err.message}`;
});
