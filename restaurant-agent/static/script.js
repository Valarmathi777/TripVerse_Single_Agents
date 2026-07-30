// ─────────────────────────────────────────────
//  RestaurantAI · Global v2.0 · script.js
// ─────────────────────────────────────────────

const COUNTRY_FLAGS = {
  "Japan":     "🇯🇵",
  "France":    "🇫🇷",
  "USA":       "🇺🇸",
  "Italy":     "🇮🇹",
  "India":     "🇮🇳",
  "UK":        "🇬🇧",
  "Thailand":  "🇹🇭",
  "Vietnam":   "🇻🇳",
  "Turkey":    "🇹🇷",
  "Australia": "🇦🇺",
  "Spain":     "🇪🇸",
  "Denmark":   "🇩🇰",
  "Taiwan":    "🇹🇼",
  "Germany":   "🇩🇪",
  "Argentina": "🇦🇷",
};

const COUNTRY_COLORS = {
  "Japan":     ["#f43f5e","#fb7185"],
  "France":    ["#3b82f6","#60a5fa"],
  "USA":       ["#ef4444","#f87171"],
  "Italy":     ["#10b981","#34d399"],
  "India":     ["#f59e0b","#fbbf24"],
  "UK":        ["#6366f1","#a5b4fc"],
  "Thailand":  ["#a855f7","#c084fc"],
  "Vietnam":   ["#ef4444","#fca5a5"],
  "Turkey":    ["#f97316","#fb923c"],
  "Australia": ["#06b6d4","#22d3ee"],
  "Spain":     ["#f59e0b","#fcd34d"],
  "Denmark":   ["#ef4444","#fca5a5"],
  "Taiwan":    ["#3b82f6","#93c5fd"],
  "Germany":   ["#f59e0b","#fde68a"],
  "Argentina": ["#06b6d4","#67e8f9"],
};

const MEAL_ICONS = { Morning: "☕", Lunch: "🍽", Dinner: "🌙" };
const DIET_CLASS = {
  "Vegetarian":    "diet-veg",
  "Vegan":         "diet-vegan",
  "Halal":         "diet-halal",
  "Non-Vegetarian": "",
};
const BUDGET_CLASS = { "Low": "budget-low", "High": "budget-high" };

let allTableRows = [];

document.addEventListener("DOMContentLoaded", () => {

  // ── Topbar scroll ──
  window.addEventListener("scroll", () => {
    document.getElementById("topbar").classList.toggle("scrolled", window.scrollY > 10);
  });

  // ── Load hero stats ──
  Promise.all([
    fetch("/api/restaurants").then(r => r.json()).catch(() => []),
    fetch("/api/countries").then(r => r.json()).catch(() => []),
  ]).then(([rests, countries]) => {
    const statCount = document.getElementById("stat-count");
    const statCountries = document.getElementById("stat-countries");
    const statCities = document.getElementById("stat-cities");
    if (statCount) animateCount(statCount, rests.length || 0);
    if (statCountries) animateCount(statCountries, countries.length || 0);
    if (statCities) {
      const cities = new Set(rests.map(r => r.location).filter(Boolean));
      animateCount(statCities, cities.size);
    }
  });

  function animateCount(el, target) {
    let n = 0;
    const step = Math.ceil(target / 25);
    const t = setInterval(() => {
      n = Math.min(n + step, target);
      el.textContent = n;
      if (n >= target) clearInterval(t);
    }, 35);
  }

  // ── Toast ──
  function toast(msg, type = "info") {
    const icons = { success: "✅", error: "❌", info: "✨" };
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${icons[type]}</span><span>${msg}</span>`;
    document.getElementById("toast-container").appendChild(el);
    setTimeout(() => { el.classList.add("fade-out"); setTimeout(() => el.remove(), 320); }, 3200);
  }
  window._toast = toast;

  // ── Tab Navigation ──
  const hero = document.getElementById("hero-banner");

  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
      hero.style.display = btn.dataset.tab === "recommend" ? "" : "none";
      if (btn.dataset.tab === "manage") loadTable();
      if (btn.dataset.tab === "browse") browseRestaurants();
      if (btn.dataset.tab === "explore") loadCountryExplorer();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });

  // ── Quick Chips ──
  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.getElementById("query-input").value = chip.dataset.query;
      executeRecommendation();
    });
  });

  document.getElementById("search-btn").addEventListener("click", executeRecommendation);
  document.getElementById("query-input").addEventListener("keypress", e => {
    if (e.key === "Enter") executeRecommendation();
  });

  // ── Recommend ──
  async function executeRecommendation() {
    const query = document.getElementById("query-input").value.trim();
    const btnText = document.getElementById("btn-text");
    const spinner = document.getElementById("btn-spinner");
    const btn = document.getElementById("search-btn");

    btnText.classList.add("hidden");
    spinner.classList.remove("hidden");
    btn.disabled = true;

    document.getElementById("trace-container").innerHTML =
      `<div class="trace-item"><div class="trace-agent">🚀 Pipeline Active</div><div class="trace-action">Processing your request…</div></div>`;

    const payload = query
      ? { query }
      : {
          preferences: {
            location: document.getElementById("f-location").value || "Tokyo",
            country:  document.getElementById("f-country").value || null,
            cuisine:  document.getElementById("f-cuisine").value,
            budget:   document.getElementById("f-budget").value,
            food_preference: document.getElementById("f-diet").value,
            min_rating: parseFloat(document.getElementById("f-rating").value) || 4.0,
            meal_time: document.getElementById("f-meal").value || null,
          }
        };

    try {
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      renderTrace(data.agent_trace, data.metadata);
      renderPrefTags(data.preferences);
      renderResults(data.recommendations);
      toast(`Found ${data.recommendations?.length || 0} restaurants!`, "success");
    } catch (err) {
      document.getElementById("trace-container").innerHTML =
        `<div class="trace-item" style="border-color:#ef4444"><div class="trace-agent" style="color:#f87171">❌ Error</div><div class="trace-action">${err.message}</div></div>`;
      document.getElementById("results-container").innerHTML =
        `<div class="empty-state"><div class="empty-icon">⚠️</div><div class="empty-title">Request Failed</div><div class="empty-sub">${err.message}</div></div>`;
      toast(err.message, "error");
    } finally {
      btnText.classList.remove("hidden");
      spinner.classList.add("hidden");
      btn.disabled = false;
    }
  }

  function renderTrace(steps, meta) {
    if (!steps || !steps.length) return;
    document.getElementById("exec-badge").textContent = `${meta?.execution_time_ms ?? 0} ms`;
    document.getElementById("trace-container").innerHTML = steps.map(s => `
      <div class="trace-item">
        <div class="trace-agent">🧠 ${s.agent_name} <span style="font-weight:400;color:var(--muted)">(${s.duration_ms}ms)</span></div>
        <div class="trace-action">${s.action}</div>
        <div class="trace-output">➔ ${s.output_summary}</div>
      </div>`).join("");
  }

  function renderPrefTags(pref) {
    if (!pref) return;
    const tags = [];
    if (pref.location) tags.push(`📍 ${pref.location}`);
    if (pref.country)  tags.push(`${COUNTRY_FLAGS[pref.country] || "🌍"} ${pref.country}`);
    if (pref.cuisine)  tags.push(`🍳 ${pref.cuisine}`);
    if (pref.food_preference) tags.push(`🥗 ${pref.food_preference}`);
    if (pref.budget)   tags.push(`💰 ${pref.budget}`);
    if (pref.min_rating) tags.push(`⭐ ${pref.min_rating}+`);
    document.getElementById("pref-tags").innerHTML = tags.map(t => `<span class="tag">${t}</span>`).join("");
  }

  function renderResults(recs) {
    if (!recs || !recs.length) {
      document.getElementById("results-container").innerHTML =
        `<div class="empty-state"><div class="empty-icon">🔍</div><div class="empty-title">No Matches Found</div><div class="empty-sub">Try relaxing your filters, changing the location, or using a different country.</div></div>`;
      return;
    }

    const groups = { Morning: [], Lunch: [], Dinner: [] };
    const unassigned = [];
    recs.forEach(r => {
      const mt = (r.meal_time || "").toLowerCase();
      if (mt === "morning") groups.Morning.push(r);
      else if (mt === "lunch") groups.Lunch.push(r);
      else if (mt === "dinner") groups.Dinner.push(r);
      else unassigned.push(r);
    });
    unassigned.forEach((r, i) => groups[["Morning","Lunch","Dinner"][i % 3]].push(r));

    let html = "";
    for (const [meal, list] of Object.entries(groups)) {
      if (!list.length) continue;
      html += `<div class="meal-section">
        <div class="meal-title">
          ${MEAL_ICONS[meal]} ${meal}
          <span class="meal-title-badge">${list.length} restaurant${list.length > 1 ? "s" : ""}</span>
        </div>
        <div class="cards-grid">${list.map(cardHTML).join("")}</div>
      </div>`;
    }
    document.getElementById("results-container").innerHTML = html;
  }

  function cardHTML(r) {
    const flag = COUNTRY_FLAGS[r.country] || "🌍";
    const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent((r.name || "") + " " + (r.address || r.location || ""))}`;
    const dietCls = DIET_CLASS[r.type] || "";
    const budgetCls = BUDGET_CLASS[r.budget] || "";
    return `
      <div class="resto-card">
        <div class="resto-top">
          <div class="resto-name">${r.name}</div>
          <div class="resto-rating">⭐ ${r.rating}</div>
        </div>
        <div class="resto-location">${flag} ${r.location}${r.country ? `, ${r.country}` : ""}</div>
        <div class="resto-meta">
          <span class="meta-tag">${r.cuisine}</span>
          <span class="meta-tag ${dietCls}">${r.type}</span>
          <span class="meta-tag ${budgetCls}">${r.budget === "Low" ? "$" : r.budget === "Medium" ? "$$" : "$$$"}</span>
          ${r.match_score ? `<span class="match-tag">✦ ${r.match_score}% match</span>` : ""}
        </div>
        <ul class="resto-reasons">
          ${(r.reasons || []).map(reason => `<li>${reason}</li>`).join("")}
        </ul>
        <div class="card-actions">
          <a href="${mapUrl}" target="_blank" class="btn-map">📍 View on Map</a>
        </div>
      </div>`;
  }

  // ─────────────────────────────────────────────
  //  WORLD EXPLORER
  // ─────────────────────────────────────────────

  window.loadCountryExplorer = async function () {
    const grid = document.getElementById("country-grid");
    const detail = document.getElementById("country-detail");
    detail.classList.add("hidden");
    grid.style.display = "";
    grid.innerHTML = `<div class="loading-spinner-wrap"><div class="spinner-lg"></div></div>`;

    try {
      const countries = await fetch("/api/countries").then(r => r.json());
      if (!countries.length) {
        grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🌍</div><div class="empty-title">No Countries Found</div><div class="empty-sub">Add restaurants to populate the world map.</div></div>`;
        return;
      }
      grid.innerHTML = countries.map(c => {
        const flag = COUNTRY_FLAGS[c.country] || "🌍";
        const colors = COUNTRY_COLORS[c.country] || ["#6366f1","#a855f7"];
        const cityList = (c.cities || []).slice(0, 3).join(", ");
        const moreCities = c.cities.length > 3 ? ` +${c.cities.length - 3} more` : "";
        return `
          <div class="country-card" onclick="showCountryDetail('${c.country.replace(/'/g, "\\'")}', '${flag}')"
               style="--cg1:${colors[0]};--cg2:${colors[1]}">
            <div class="country-flag">${flag}</div>
            <div class="country-name">${c.country}</div>
            <div class="country-count">${c.count} restaurant${c.count > 1 ? "s" : ""}</div>
            <div class="country-cities">${cityList}${moreCities}</div>
            <div class="country-cuisines">
              ${(c.cuisines || []).slice(0, 3).map(cu => `<span class="country-cuisine-tag">${cu}</span>`).join("")}
            </div>
          </div>`;
      }).join("");
    } catch (e) {
      grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">⚠️</div><div class="empty-title">Failed to load countries</div><div class="empty-sub">${e.message}</div></div>`;
    }
  };

  window.showCountryDetail = async function (countryName, flag) {
    const grid = document.getElementById("country-grid");
    const detail = document.getElementById("country-detail");
    grid.style.display = "none";
    detail.classList.remove("hidden");

    document.getElementById("detail-flag").textContent = flag;
    document.getElementById("detail-country-name").textContent = countryName;
    document.getElementById("country-detail-stats").innerHTML = `<div class="loading-spinner-wrap"><div class="spinner-lg"></div></div>`;
    document.getElementById("country-restaurant-grid").innerHTML = "";

    try {
      const rows = await fetch(`/api/restaurants?country=${encodeURIComponent(countryName)}`).then(r => r.json());
      const cities = [...new Set(rows.map(r => r.location).filter(Boolean))];
      const cuisines = [...new Set(rows.map(r => r.cuisine).filter(Boolean))];
      const avgRating = rows.length ? (rows.reduce((s, r) => s + (r.rating || 0), 0) / rows.length).toFixed(1) : "-";

      document.getElementById("country-detail-stats").innerHTML = `
        <div class="detail-stat"><div class="detail-stat-num">${rows.length}</div><div class="detail-stat-label">Restaurants</div></div>
        <div class="detail-stat"><div class="detail-stat-num">${cities.length}</div><div class="detail-stat-label">Cities</div></div>
        <div class="detail-stat"><div class="detail-stat-num">${cuisines.length}</div><div class="detail-stat-label">Cuisines</div></div>
        <div class="detail-stat"><div class="detail-stat-num">${avgRating}</div><div class="detail-stat-label">Avg Rating</div></div>
      `;

      if (!rows.length) {
        document.getElementById("country-restaurant-grid").innerHTML =
          `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🍽</div><div class="empty-title">No restaurants for ${countryName}</div></div>`;
        return;
      }

      document.getElementById("country-restaurant-grid").innerHTML = rows.map(r => {
        const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent((r.name || "") + " " + (r.address || r.location || ""))}`;
        const dietCls = DIET_CLASS[r.type] || "";
        const budgetCls = BUDGET_CLASS[r.budget] || "";
        return `
          <div class="browse-card">
            <div class="browse-card-name">${r.name}</div>
            <div class="browse-card-loc">📍 ${r.location} &nbsp;•&nbsp; ⭐ ${r.rating} &nbsp;•&nbsp; ${MEAL_ICONS[r.meal_time] || ""} ${r.meal_time || ""}</div>
            <div class="resto-meta">
              <span class="meta-tag">${r.cuisine}</span>
              <span class="meta-tag ${dietCls}">${r.type}</span>
              <span class="meta-tag ${budgetCls}">${r.budget === "Low" ? "$" : r.budget === "Medium" ? "$$" : "$$$"}</span>
            </div>
            <div class="browse-card-desc">${r.description || r.address || ""}</div>
            <div class="card-actions">
              <a href="${mapUrl}" target="_blank" class="btn-map">📍 View on Map</a>
            </div>
          </div>`;
      }).join("");
    } catch (e) {
      toast("Failed to load restaurants: " + e.message, "error");
    }
  };

  document.getElementById("btn-back-countries").addEventListener("click", () => {
    document.getElementById("country-detail").classList.add("hidden");
    document.getElementById("country-grid").style.display = "";
  });

  // ─────────────────────────────────────────────
  //  DB TABLE
  // ─────────────────────────────────────────────

  window.loadTable = async function () {
    try {
      const rows = await fetch("/api/restaurants").then(r => r.json());
      allTableRows = rows;
      renderTable(rows);
    } catch (e) { console.error("loadTable error:", e); }
  };

  function renderTable(rows) {
    const tbody = document.getElementById("db-tbody");
    if (!rows.length) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;color:var(--muted);padding:24px">No restaurants in database.</td></tr>`;
      return;
    }
    tbody.innerHTML = rows.map(r => {
      const flag = COUNTRY_FLAGS[r.country] || "";
      return `
        <tr>
          <td>${r.id}</td>
          <td style="color:var(--text);font-weight:600">${r.name}</td>
          <td>${r.location || "—"}</td>
          <td>${flag} ${r.country || "—"}</td>
          <td>${r.cuisine}</td>
          <td>${r.type}</td>
          <td>${r.budget}</td>
          <td style="color:var(--yellow)">⭐ ${r.rating}</td>
          <td>${r.meal_time}</td>
          <td class="actions-cell">
            <button class="btn-edit" onclick='editRestaurant(${JSON.stringify(r).replace(/"/g, "&quot;")})'>Edit</button>
            <button class="btn-danger" onclick="deleteRestaurant(${r.id}, '${r.name.replace(/'/g, "\\'")}')">Del</button>
          </td>
        </tr>`;
    }).join("");
  }

  window.filterTable = function () {
    const q = (document.getElementById("tbl-search")?.value || "").toLowerCase();
    if (!q) { renderTable(allTableRows); return; }
    renderTable(allTableRows.filter(r => (r.name || "").toLowerCase().includes(q)));
  };

  window.saveRestaurant = async function () {
    const id = document.getElementById("edit-id").value;
    const payload = {
      name:        document.getElementById("db-name").value.trim(),
      location:    document.getElementById("db-location").value.trim(),
      country:     document.getElementById("db-country").value || null,
      cuisine:     document.getElementById("db-cuisine").value,
      type:        document.getElementById("db-type").value,
      budget:      document.getElementById("db-budget").value,
      meal_time:   document.getElementById("db-meal").value,
      rating:      parseFloat(document.getElementById("db-rating").value) || 4.5,
      address:     document.getElementById("db-address").value.trim() || null,
      description: document.getElementById("db-desc").value.trim() || null,
    };
    if (!payload.name || !payload.location) { showFormMsg("Name and City are required.", "error"); return; }
    try {
      const res = await fetch(id ? `/api/restaurants/${id}` : "/api/restaurants", {
        method: id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(await res.text());
      const msg = id ? "Restaurant updated!" : "Restaurant added!";
      showFormMsg(msg, "success");
      toast(msg, "success");
      resetForm();
      loadTable();
    } catch (e) { showFormMsg("Error: " + e.message, "error"); toast(e.message, "error"); }
  };

  window.editRestaurant = function (r) {
    document.getElementById("edit-id").value = r.id;
    document.getElementById("form-title").textContent = "Edit Restaurant";
    document.getElementById("db-name").value = r.name;
    document.getElementById("db-location").value = r.location;
    document.getElementById("db-country").value = r.country || "";
    document.getElementById("db-cuisine").value = r.cuisine;
    document.getElementById("db-type").value = r.type;
    document.getElementById("db-budget").value = r.budget;
    document.getElementById("db-meal").value = r.meal_time;
    document.getElementById("db-rating").value = r.rating;
    document.getElementById("db-address").value = r.address || "";
    document.getElementById("db-desc").value = r.description || "";
    document.getElementById("cancel-edit-btn").classList.remove("hidden");
    document.getElementById("save-btn").textContent = "💾 Update Restaurant";
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  window.cancelEdit = function () { resetForm(); };

  window.deleteRestaurant = async function (id, name) {
    if (!confirm(`Delete "${name}"?`)) return;
    try {
      const res = await fetch(`/api/restaurants/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error(await res.text());
      toast(`"${name}" deleted.`, "info");
      loadTable();
    } catch (e) { toast("Delete failed: " + e.message, "error"); }
  };

  function resetForm() {
    document.getElementById("edit-id").value = "";
    document.getElementById("form-title").textContent = "Add New Restaurant";
    document.getElementById("save-btn").textContent = "💾 Save Restaurant";
    document.getElementById("cancel-edit-btn").classList.add("hidden");
    ["db-name","db-location","db-address","db-desc"].forEach(id => document.getElementById(id).value = "");
    document.getElementById("db-country").value = "";
    document.getElementById("db-cuisine").value = "Any";
    document.getElementById("db-type").value = "Any";
    document.getElementById("db-budget").value = "Any";
    document.getElementById("db-meal").value = "Lunch";
    document.getElementById("db-rating").value = "4.5";
    showFormMsg("", "");
  }

  function showFormMsg(msg, type) {
    const el = document.getElementById("form-msg");
    el.textContent = msg;
    el.className = `form-msg ${type}`;
  }

  // ─────────────────────────────────────────────
  //  BROWSE
  // ─────────────────────────────────────────────

  window.browseRestaurants = async function () {
    const params = new URLSearchParams();
    const loc = document.getElementById("br-location")?.value || "";
    const country = document.getElementById("br-country")?.value || "";
    const cui = document.getElementById("br-cuisine")?.value || "";
    const typ = document.getElementById("br-type")?.value || "";
    const bud = document.getElementById("br-budget")?.value || "";
    if (loc)     params.append("location", loc);
    if (country) params.append("country", country);
    if (cui)     params.append("cuisine", cui);
    if (typ)     params.append("type", typ);

    try {
      let rows = await fetch(`/api/restaurants?${params}`).then(r => r.json());
      // Client-side budget filter (API doesn't filter budget)
      if (bud) rows = rows.filter(r => r.budget === bud);

      const container = document.getElementById("browse-results");
      const countEl = document.getElementById("browse-count");
      countEl.textContent = rows.length
        ? `Showing ${rows.length} restaurant${rows.length > 1 ? "s" : ""}`
        : "";

      if (!rows.length) {
        container.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🔍</div><div class="empty-title">No Results</div><div class="empty-sub">Try different filters or clear all.</div></div>`;
        return;
      }
      container.innerHTML = rows.map(r => {
        const flag = COUNTRY_FLAGS[r.country] || "🌍";
        const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent((r.name || "") + " " + (r.address || r.location || ""))}`;
        const dietCls = DIET_CLASS[r.type] || "";
        const budgetCls = BUDGET_CLASS[r.budget] || "";
        return `
          <div class="browse-card">
            <div class="browse-card-name">${r.name}</div>
            <div class="browse-card-loc">${flag} ${r.location}${r.country ? `, ${r.country}` : ""} &nbsp;•&nbsp; ⭐ ${r.rating} &nbsp;•&nbsp; ${MEAL_ICONS[r.meal_time] || ""} ${r.meal_time || ""}</div>
            <div class="resto-meta">
              <span class="meta-tag">${r.cuisine}</span>
              <span class="meta-tag ${dietCls}">${r.type}</span>
              <span class="meta-tag ${budgetCls}">${r.budget === "Low" ? "$" : r.budget === "Medium" ? "$$" : "$$$"}</span>
            </div>
            <div class="browse-card-desc">${r.description || r.address || ""}</div>
            <div class="card-actions">
              <a href="${mapUrl}" target="_blank" class="btn-map">📍 View on Map</a>
            </div>
          </div>`;
      }).join("");
    } catch (e) { console.error("browse error:", e); }
  };

  window.clearBrowseFilters = function () {
    document.getElementById("br-location").value = "";
    document.getElementById("br-country").value = "";
    document.getElementById("br-cuisine").value = "";
    document.getElementById("br-type").value = "";
    document.getElementById("br-budget").value = "";
    browseRestaurants();
  };

  // Initial load
  browseRestaurants();
});
