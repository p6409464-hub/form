/**
 * Farmer Market Price Assistant - Application Core JavaScript
 * Handles:
 * - Dynamic District-Market cascading dropdowns
 * - Crop quick selection
 * - Profit calculations & Best Market Recommendation rendering
 * - Market comparison table filtering & CSV export
 * - AGMARKNET sync modal & toast alerts
 */

// Target markets map fallback if not passed by template
const DEFAULT_MARKETS = {
  "Coimbatore": ["Pollachi", "Annur", "Sulur", "Kinathukkadavu"],
  "Tiruppur": ["Udumalpet", "Dharapuram", "Palladam", "Kangayam"],
  "Erode": ["Erode", "Gobichettipalayam", "Perundurai", "Bhavani", "Sathyamangalam"]
};

let currentComparisonData = [];

/**
 * Dynamically updates the markets dropdown based on the selected district
 */
function updateMarketsDropdown(districtName, selectedMarket = null) {
  const marketSelect = document.getElementById("marketSelect");
  if (!marketSelect) return;

  const marketsMap = window.MARKETS_BY_DISTRICT || DEFAULT_MARKETS;
  const markets = marketsMap[districtName] || [];

  marketSelect.innerHTML = "";
  markets.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    if (selectedMarket && m.toLowerCase() === selectedMarket.toLowerCase()) {
      opt.selected = true;
    }
    marketSelect.appendChild(opt);
  });

  const hint = document.getElementById("marketCountHint");
  if (hint) {
    hint.textContent = `Showing ${markets.length} regulated mandis in ${districtName}.`;
  }
}

/**
 * Sets quick crop from chips
 */
function setQuickCrop(cropName) {
  const select = document.getElementById("cropSelect");
  if (!select) return;
  select.value = cropName;

  // Update active chip style
  document.querySelectorAll(".crop-chip").forEach(chip => {
    if (chip.textContent.includes(cropName)) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });

  // Automatically recalculate if results already open
  const resultsContainer = document.getElementById("resultsContainer");
  if (resultsContainer && resultsContainer.style.display !== "none") {
    calculateProfit(false);
  }
}

function handleCropChange(cropName) {
  document.querySelectorAll(".crop-chip").forEach(chip => {
    if (chip.textContent.includes(cropName)) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });
}

/**
 * Toggles advanced options accordion
 */
function toggleAdvancedOptions() {
  const body = document.getElementById("advancedOptions");
  const icon = document.getElementById("advancedToggleIcon");
  if (!body) return;

  if (body.style.display === "none") {
    body.style.display = "block";
    if (icon) icon.textContent = "▲";
  } else {
    body.style.display = "none";
    if (icon) icon.textContent = "▼";
  }
}

/**
 * Handles form submit
 */
function handleCalculateSubmit(e) {
  if (e) e.preventDefault();
  calculateProfit(true);
}

/**
 * Executes profit calculation and market comparison via API
 */
async function calculateProfit(showFeedback = true) {
  const cropSelect = document.getElementById("cropSelect");
  const districtSelect = document.getElementById("districtSelect");
  const marketSelect = document.getElementById("marketSelect");
  const dateInput = document.getElementById("marketDate");
  const quantityInput = document.getElementById("cropQuantity");
  const locationInput = document.getElementById("farmerLocation");
  const nameInput = document.getElementById("farmerName");
  const customTransport = document.getElementById("customTransportCost");
  const customOther = document.getElementById("customOtherExpenses");
  const submitBtn = document.getElementById("calcSubmitBtn");

  if (!cropSelect || !districtSelect || !marketSelect) return;

  const crop = cropSelect.value;
  const district = districtSelect.value;
  const market = marketSelect.value;
  const dateVal = dateInput ? dateInput.value : "";
  const quantity = parseFloat(quantityInput ? quantityInput.value : 1000);
  const location = locationInput ? locationInput.value.trim() : market;

  if (!crop) {
    showToast("Please choose a crop.", "danger");
    return;
  }
  if (!district) {
    showToast("Please select a district.", "danger");
    return;
  }
  if (!market) {
    showToast("Please select a target market.", "danger");
    return;
  }
  if (isNaN(quantity) || quantity <= 0) {
    showToast("Crop quantity must be greater than 0 kg.", "danger");
    return;
  }

  // Set loading state
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span> Comparing 13 Mandis...`;
  }

  const payload = {
    crop_name: crop,
    district_name: district,
    market_name: market,
    date: dateVal,
    quantity_kg: quantity,
    farmer_location: location,
    farmer_name: nameInput ? nameInput.value.trim() : "Farmer",
    custom_transport_cost: customTransport && customTransport.value !== "" ? parseFloat(customTransport.value) : null,
    custom_other_expenses: customOther && customOther.value !== "" ? parseFloat(customOther.value) : null
  };

  try {
    const response = await fetch("/api/calculate-profit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const res = await response.json();

    if (!res.success) {
      showToast(res.error || "Failed to calculate profit.", "danger");
      return;
    }

    renderResults(res.data);
    if (showFeedback) {
      showToast(`Market comparison completed for ${quantity} kg of ${crop}!`, "success");
    }

  } catch (err) {
    showToast(`Network or server error: ${err.message}`, "danger");
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>🚀</span> Compare Markets & Calculate Profit`;
    }
  }
}

/**
 * Renders Best Market Recommendation & Comparison Table
 */
function renderResults(data) {
  const placeholder = document.getElementById("resultsPlaceholder");
  const container = document.getElementById("resultsContainer");
  if (placeholder) placeholder.style.display = "none";
  if (container) container.style.display = "block";

  currentComparisonData = data.markets || [];

  // 1. Best Market Recommendation Card
  const best = data.best_market;
  if (best) {
    document.getElementById("recMarketName").innerHTML = `
      ${best.market_name} Market 
      <span style="font-size: 1rem; font-weight: 600; color: var(--primary-green);">(${best.district_name})</span>
    `;
    document.getElementById("recExplanation").innerText = data.recommendation_summary || "";

    // Stats
    document.getElementById("statSellingValue").innerText = `₹${Number(best.selling_value).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById("statModalPrice").innerText = `@ ₹${best.price_per_kg.toFixed(2)} / kg (₹${Number(best.modal_price_qtl).toLocaleString()}/Qtl)`;
    
    document.getElementById("statTransportCost").innerText = `- ₹${Number(best.transport_cost).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById("statDistance").innerText = `${best.distance_km} km road distance`;

    document.getElementById("statOtherExpenses").innerText = `- ₹${Number(best.other_expenses).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    
    document.getElementById("statNetProfit").innerText = `₹${Number(best.net_profit).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  } else {
    document.getElementById("recMarketName").innerText = "No Active Price Data Reported";
    document.getElementById("recExplanation").innerText = `AGMARKNET has not yet reported daily prices for ${data.crop_name} on this date. Try clicking 'Sync Agmarknet API' or choose another crop.`;
  }

  // 2. Comparison Table
  document.getElementById("comparisonTableTitle").innerText = `Market Comparison: ${data.crop_name} (${data.quantity_kg.toLocaleString()} kg)`;
  document.getElementById("comparisonSubtext").innerText = `Farmer Location: ${data.farmer_location} • Selected Base: ${data.selected_market} (${data.selected_district})`;
  document.getElementById("tablePricedSummary").innerText = `${data.priced_markets_count} of ${data.total_markets_compared} mandis reporting prices for this arrival date.`;

  renderComparisonTable(currentComparisonData);
}

/**
 * Generates table rows for comparison
 */
function renderComparisonTable(markets) {
  const tbody = document.getElementById("comparisonTableBody");
  if (!tbody) return;

  if (!markets || markets.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; padding: 2rem;">No matching markets found.</td></tr>`;
    return;
  }

  let html = "";
  markets.forEach(m => {
    const isRec = m.is_recommended;
    const isSel = m.is_selected;
    const rowClass = isRec ? "recommended-row" : (isSel ? "selected-row" : "");

    const distBadgeClass = m.district_name.toLowerCase() === "coimbatore" ? "badge-coimbatore" :
                           m.district_name.toLowerCase() === "tiruppur" ? "badge-tiruppur" : "badge-erode";

    let statusBadges = "";
    if (isRec) {
      statusBadges += `<span class="badge badge-recommended">★ Best Net Profit</span> `;
    }
    if (isSel) {
      statusBadges += `<span class="badge badge-selected">Your Base</span> `;
    }

    if (!m.has_price) {
      html += `
        <tr class="${rowClass}">
          <td><strong>${m.market_name}</strong></td>
          <td><span class="badge ${distBadgeClass}">${m.district_name}</span></td>
          <td colspan="6" style="color: var(--text-muted); font-style: italic;">No price reported by Agmarknet for selected date</td>
          <td>-</td>
          <td>${statusBadges || '<span class="badge badge-source">No Data</span>'}</td>
        </tr>
      `;
      return;
    }

    html += `
      <tr class="${rowClass}">
        <td><strong>${m.market_name}</strong></td>
        <td><span class="badge ${distBadgeClass}">${m.district_name}</span></td>
        <td><code>${m.arrival_date || '-'}</code></td>
        <td><strong>₹${Number(m.modal_price_qtl).toLocaleString()}</strong></td>
        <td><span style="font-weight: 700; color: var(--primary-green);">₹${m.price_per_kg.toFixed(2)}</span></td>
        <td style="font-size: 0.82rem; color: var(--text-muted);">₹${Number(m.min_price_qtl).toLocaleString()} - ₹${Number(m.max_price_qtl).toLocaleString()}</td>
        <td style="color: #b91c1c;">₹${Number(m.transport_cost).toLocaleString()} <span style="font-size: 0.72rem; color: var(--text-muted);">(${m.distance_km}km)</span></td>
        <td style="color: #b91c1c;">₹${Number(m.other_expenses).toLocaleString()}</td>
        <td>
          <strong style="font-size: 1rem; color: ${m.net_profit > 0 ? 'var(--primary-dark)' : '#b91c1c'};">
            ₹${Number(m.net_profit).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
          </strong>
        </td>
        <td>${statusBadges || '<span class="badge badge-source">Standard</span>'}</td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

/**
 * Filter comparison table by market or district
 */
function filterComparisonTable(query) {
  if (!currentComparisonData) return;
  const q = query.toLowerCase().trim();
  const filtered = currentComparisonData.filter(m => 
    m.market_name.toLowerCase().includes(q) || 
    m.district_name.toLowerCase().includes(q)
  );
  renderComparisonTable(filtered);
}

/**
 * Export current comparison to CSV
 */
function exportComparisonCSV() {
  if (!currentComparisonData || currentComparisonData.length === 0) {
    showToast("No comparison data available to export.", "warning");
    return;
  }

  let csv = "Market Name,District,Distance (km),Modal Price (Rs/Qtl),Price per kg (Rs),Min Price,Max Price,Selling Value (Rs),Transport Cost (Rs),Other Expenses (Rs),Net Profit (Rs),Is Best Recommended\n";
  currentComparisonData.forEach(m => {
    csv += `"${m.market_name}","${m.district_name}",${m.distance_km},${m.modal_price_qtl},${m.price_per_kg},${m.min_price_qtl},${m.max_price_qtl},${m.selling_value},${m.transport_cost},${m.other_expenses},${m.net_profit},${m.is_recommended ? 'YES' : 'NO'}\n`;
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `Market_Comparison_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast("Comparison exported to CSV!", "success");
}

/**
 * Modal Handling for AGMARKNET Live Sync
 */
function openSyncModal() {
  const modal = document.getElementById("syncModal");
  if (modal) modal.classList.add("active");
}

function closeSyncModal() {
  const modal = document.getElementById("syncModal");
  if (modal) modal.classList.remove("active");
  const statusDiv = document.getElementById("syncResultStatus");
  if (statusDiv) statusDiv.style.display = "none";
}

async function runAgmarknetSync() {
  const apiKey = document.getElementById("modalApiKeyInput").value.trim();
  const district = document.getElementById("modalDistrictFilter").value;
  const statusDiv = document.getElementById("syncResultStatus");
  const btn = document.getElementById("executeSyncBtn");

  if (statusDiv) {
    statusDiv.style.display = "block";
    statusDiv.className = "alert-banner alert-info";
    statusDiv.innerHTML = `<span class="spinner"></span> Connecting to Government of India data.gov.in servers...`;
  }
  if (btn) btn.disabled = true;

  try {
    const res = await fetch("/api/sync-agmarknet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey, district: district })
    });
    const result = await res.json();

    if (result.success) {
      statusDiv.className = "alert-banner alert-success";
      statusDiv.innerHTML = `✅ <strong>Sync Successful!</strong> ${result.message}`;
      showToast("Agmarknet data synchronized successfully!", "success");
      setTimeout(() => {
        closeSyncModal();
        // Refresh calculations
        calculateProfit(false);
      }, 1500);
    } else {
      statusDiv.className = "alert-banner alert-danger";
      statusDiv.innerHTML = `⚠️ <strong>Sync Warning:</strong> ${result.message}`;
      showToast(result.message, "danger");
    }
  } catch (e) {
    if (statusDiv) {
      statusDiv.className = "alert-banner alert-danger";
      statusDiv.innerHTML = `❌ Connection Error: ${e.message}`;
    }
  } finally {
    if (btn) btn.disabled = false;
  }
}

/**
 * Global Toast Alert Display
 */
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast`;
  if (type === "danger") toast.style.borderLeftColor = "#dc2626";
  if (type === "warning") toast.style.borderLeftColor = "#f59e0b";
  if (type === "info") toast.style.borderLeftColor = "#2563eb";

  const icon = type === "danger" ? "❌" : (type === "warning" ? "⚠️" : (type === "info" ? "ℹ️" : "✅"));

  toast.innerHTML = `
    <span>${icon}</span>
    <span style="font-size: 0.88rem; font-weight: 500;">${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
