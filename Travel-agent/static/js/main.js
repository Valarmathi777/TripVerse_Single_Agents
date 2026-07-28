// Preference chip toggle
document.querySelectorAll('.pref-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.pref-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
  });
});

// Set today as default date
document.getElementById('date').valueAsDate = new Date();

// Fill route from destination cards
function fillRoute(src, dst) {
  document.getElementById('source').value = src;
  document.getElementById('destination').value = dst;
  document.getElementById('planner').scrollIntoView({ behavior: 'smooth' });
}

// Mode labels
const modeLabels = {
  'Walking': 'Walk', 'Bike': 'Bike', 'Bus': 'Bus', 'Metro': 'Metro',
  'Train': 'Train', 'Taxi': 'Taxi', 'Rental Car': 'Car', 'Flight': 'Flight'
};

function getIcon(mode) {
  return modeLabels[mode] || mode;
}

function scoreClass(score) {
  if (score >= 70) return 'score-high';
  if (score >= 45) return 'score-mid';
  return 'score-low';
}

function weatherIcon(condition) {
  const map = { Clear: 'Clear', Clouds: 'Cloudy', Rain: 'Rain', Snow: 'Snow', Thunderstorm: 'Storm', Drizzle: 'Drizzle', Mist: 'Mist', Fog: 'Fog' };
  return map[condition] || 'Clear';
}

function trafficColor(level) {
  return { light: '#10b981', moderate: '#f59e0b', heavy: '#ef4444' }[level] || '#64748b';
}

document.getElementById('planForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const preference = document.querySelector('input[name="preference"]:checked')?.value || 'fastest';
  const payload = {
    source: document.getElementById('source').value.trim(),
    destination: document.getElementById('destination').value.trim(),
    date: document.getElementById('date').value,
    time: document.getElementById('time').value,
    budget: parseFloat(document.getElementById('budget').value),
    group_size: parseInt(document.getElementById('group_size').value),
    preference
  };

  const btn = document.getElementById('searchBtn');
  document.getElementById('btnText').style.display = 'none';
  document.getElementById('btnLoader').style.display = 'inline';
  btn.disabled = true;

  document.getElementById('results').style.display = 'none';

  try {
    const res = await fetch('/api/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.detail || 'Something went wrong. Please try again.');
      return;
    }

    renderResults(data, payload);
  } catch (err) {
    showError('Network error. Please check your connection.');
  } finally {
    document.getElementById('btnText').style.display = 'inline';
    document.getElementById('btnLoader').style.display = 'none';
    btn.disabled = false;
  }
});

function showError(msg) {
  let box = document.getElementById('errorBox');
  if (!box) {
    box = document.createElement('div');
    box.id = 'errorBox';
    box.className = 'error-box';
    document.getElementById('planner').after(box);
  }
  box.textContent = 'Warning: ' + msg;
  box.style.display = 'block';
}

function renderResults(data, req) {
  const errBox = document.getElementById('errorBox');
  if (errBox) errBox.style.display = 'none';

  // Subtitle
  document.getElementById('routeSubtitle').textContent =
    `${req.source} → ${req.destination} · ${req.date} · ${req.group_size} traveller${req.group_size > 1 ? 's' : ''}`;

  // Conditions bar
  const w = data.weather || {};
  const wIcon = weatherIcon(w.condition);
  const tColor = trafficColor(data.traffic);
  document.getElementById('conditionsBar').innerHTML = `
    <div class="condition-pill">${wIcon} ${w.condition || 'N/A'} · ${w.temp != null ? w.temp + '°C' : '—'}</div>
    <div class="condition-pill">Wind: ${w.description || 'N/A'}</div>
    <div class="condition-pill" style="border-color:${tColor};color:${tColor}">Traffic: ${data.traffic}</div>
    <div class="condition-pill">Budget: $${req.budget}</div>
  `;

  // Best route card
  const best = data;
  document.getElementById('bestRoute').innerHTML = `
    <div class="best-route-header">
      <div>
        <h3>Recommended Route</h3>
        <div class="mode-name">${getIcon(best.recommended_mode)} ${best.recommended_mode}</div>
      </div>
      <div class="score-badge">Score ${best.score}</div>
    </div>
    <div class="best-route-stats">
      <div class="best-stat"><div class="val">${best.travel_time}</div><div class="lbl">Travel Time</div></div>
      <div class="best-stat"><div class="val">$${best.estimated_cost}</div><div class="lbl">Est. Cost</div></div>
      <div class="best-stat"><div class="val">${best.distance}</div><div class="lbl">Distance</div></div>
      <div class="best-stat"><div class="val">${best.arrival}</div><div class="lbl">Arrival</div></div>
    </div>
    <div class="reasons-list">
      ${best.reason.map(r => `<span class="reason-tag">${r}</span>`).join('')}
    </div>
  `;

  // All options
  const grid = document.getElementById('optionsGrid');
  grid.innerHTML = '';
  (data.all_options || []).forEach((opt, i) => {
    const sc = scoreClass(opt.score);
    grid.innerHTML += `
      <div class="option-card ${i === 0 ? 'top-pick' : ''}">
        <div class="option-header">
          <div class="option-mode">${getIcon(opt.mode)} ${opt.mode}</div>
          <span class="option-score ${sc}">${opt.score}</span>
        </div>
        <div class="option-stats">
          <div class="opt-stat"><div class="v">${opt.duration}m</div><div class="l">Duration</div></div>
          <div class="opt-stat"><div class="v">$${opt.cost}</div><div class="l">Cost</div></div>
          <div class="opt-stat"><div class="v">${opt.distance} km</div><div class="l">Distance</div></div>
          <div class="opt-stat"><div class="v">${opt.transfers}</div><div class="l">Transfers</div></div>
        </div>
        ${opt.eco_friendly ? '<span class="eco-tag">Eco-Friendly</span>' : ''}
      </div>
    `;
  });

  document.getElementById('results').style.display = 'block';
  document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}
