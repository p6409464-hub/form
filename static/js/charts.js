/**
 * Farmer Market Price Assistant - Analytics & Charts Engine
 * Powered by Chart.js
 */

let marketComparisonChartInstance = null;
let priceTrendChartInstance = null;
let commodityBenchmarkChartInstance = null;

async function loadDashboardMetrics(crop = "Tomato") {
  try {
    const res = await fetch(`/api/dashboard-metrics?crop=${encodeURIComponent(crop)}`);
    const data = await res.json();
    if (!data.success) return;

    const m = data.metrics;

    // 1. Update Top KPI Cards
    const kpiSearches = document.getElementById("kpiTotalSearches");
    const kpiPrices = document.getElementById("kpiAvailablePrices");
    const kpiHighest = document.getElementById("kpiHighestPrice");
    const kpiHighestSub = document.getElementById("kpiHighestPriceSub");
    const kpiBest = document.getElementById("kpiBestMarket");
    const kpiBestSub = document.getElementById("kpiBestMarketSub");

    if (kpiSearches) kpiSearches.innerText = m.total_searches.toLocaleString();
    if (kpiPrices) kpiPrices.innerText = m.total_prices_records.toLocaleString();

    if (kpiHighest && m.highest_price) {
      kpiHighest.innerText = `₹${Number(m.highest_price.modal_price).toLocaleString()} / Qtl`;
      if (kpiHighestSub) {
        kpiHighestSub.innerText = `${m.highest_price.crop_name} @ ${m.highest_price.market_name} (${m.highest_price.district_name})`;
      }
    }

    if (kpiBest && m.top_recommended_market) {
      kpiBest.innerText = m.top_recommended_market.market_name;
      if (kpiBestSub) {
        kpiBestSub.innerText = `${m.top_recommended_market.district_name} • ${m.top_recommended_market.rec_count} times optimal`;
      }
    } else if (kpiBest) {
      kpiBest.innerText = "Pollachi / Erode";
      if (kpiBestSub) kpiBestSub.innerText = "Top regional mandis";
    }

    // 2. Render Charts
    renderMarketComparisonChart(data.market_comparison, crop);
    renderPriceTrendChart(data.price_trend, crop);
    renderCommodityBenchmarkChart(data.crop_averages);

    // 3. Render Recent Searches Table
    renderRecentSearchesTable(data.recent_searches);

  } catch (err) {
    console.error("Error loading dashboard metrics:", err);
  }
}

function updateCropCharts(newCrop) {
  const badge = document.getElementById("historyCropBadge");
  if (badge) badge.innerText = newCrop;
  loadDashboardMetrics(newCrop);
}

/**
 * Chart 1: Market-by-Market Modal Price Comparison Bar Chart
 */
function renderMarketComparisonChart(marketData, cropName) {
  const ctx = document.getElementById("marketComparisonChart");
  if (!ctx) return;

  if (marketComparisonChartInstance) {
    marketComparisonChartInstance.destroy();
  }

  const labels = (marketData || []).map(d => d.market_name);
  const values = (marketData || []).map(d => d.modal_price);
  
  // District-based colors
  const backgroundColors = (marketData || []).map(d => {
    const dist = (d.district_name || "").toLowerCase();
    if (dist === "coimbatore") return "rgba(21, 128, 61, 0.85)";
    if (dist === "tiruppur") return "rgba(79, 70, 229, 0.85)";
    return "rgba(168, 85, 247, 0.85)";
  });

  marketComparisonChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: `${cropName} Modal Price (₹/Quintal)`,
        data: values,
        backgroundColor: backgroundColors,
        borderRadius: 6,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const qtl = context.parsed.y;
              const kg = (qtl / 100.0).toFixed(2);
              return `Modal: ₹${qtl.toLocaleString()}/Qtl (₹${kg}/kg)`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: value => `₹${value.toLocaleString()}`
          },
          grid: { color: "rgba(0,0,0,0.05)" }
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } }
        }
      }
    }
  });
}

/**
 * Chart 2: Daily Price History & Trend Line Chart
 */
function renderPriceTrendChart(trendData, cropName) {
  const ctx = document.getElementById("priceTrendChart");
  if (!ctx) return;

  if (priceTrendChartInstance) {
    priceTrendChartInstance.destroy();
  }

  const labels = (trendData || []).map(d => d.arrival_date);
  const modalValues = (trendData || []).map(d => d.avg_modal);
  const minValues = (trendData || []).map(d => d.min_modal);
  const maxValues = (trendData || []).map(d => d.max_modal);

  priceTrendChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Avg Modal Price (₹/Qtl)",
          data: modalValues,
          borderColor: "#15803d",
          backgroundColor: "rgba(21, 128, 61, 0.1)",
          borderWidth: 3,
          fill: true,
          tension: 0.3,
          pointRadius: 4,
          pointBackgroundColor: "#15803d"
        },
        {
          label: "Max Price (₹/Qtl)",
          data: maxValues,
          borderColor: "#d97706",
          borderDash: [5, 5],
          borderWidth: 2,
          fill: false,
          tension: 0.3,
          pointRadius: 3
        },
        {
          label: "Min Price (₹/Qtl)",
          data: minValues,
          borderColor: "#94a3b8",
          borderDash: [3, 3],
          borderWidth: 1.5,
          fill: false,
          tension: 0.3,
          pointRadius: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top", labels: { boxWidth: 12 } },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ₹${Number(context.parsed.y).toLocaleString()}`;
            }
          }
        }
      },
      scales: {
        y: {
          ticks: { callback: v => `₹${v.toLocaleString()}` },
          grid: { color: "rgba(0,0,0,0.05)" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

/**
 * Chart 3: Benchmark Rates for Regional Crops (Horizontal Bar)
 */
function renderCommodityBenchmarkChart(cropAverages) {
  const ctx = document.getElementById("commodityBenchmarkChart");
  if (!ctx) return;

  if (commodityBenchmarkChartInstance) {
    commodityBenchmarkChartInstance.destroy();
  }

  const labels = (cropAverages || []).map(c => c.crop_name);
  const perKgValues = (cropAverages || []).map(c => c.avg_per_kg);

  commodityBenchmarkChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Benchmark Price (₹ per kg)",
        data: perKgValues,
        backgroundColor: "#16a34a",
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: c => `Avg Price: ₹${c.parsed.x} / kg`
          }
        }
      },
      scales: {
        x: {
          ticks: { callback: v => `₹${v}` },
          grid: { color: "rgba(0,0,0,0.05)" }
        },
        y: { grid: { display: false } }
      }
    }
  });
}

/**
 * Renders Recent Searches & Profit History Table
 */
function renderRecentSearchesTable(searches) {
  const tbody = document.getElementById("recentSearchesBody");
  if (!tbody) return;

  if (!searches || searches.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-muted);">No searches recorded yet. Run a market comparison from the home page.</td></tr>`;
    return;
  }

  let html = "";
  searches.forEach(s => {
    const profitText = s.net_profit ? `₹${Number(s.net_profit).toLocaleString('en-IN', {maximumFractionDigits: 2})}` : "Evaluated";
    const statusBadge = s.is_recommended ? `<span class="badge badge-recommended">Optimal</span>` : `<span class="badge badge-source">Standard</span>`;

    html += `
      <tr>
        <td><code>#${s.id}</code></td>
        <td><strong>${s.farmer_name || 'Farmer'}</strong> <span style="font-size: 0.78rem; color: var(--text-muted);">(${s.farmer_location})</span></td>
        <td><strong>${s.crop_name}</strong></td>
        <td>${Number(s.quantity_kg).toLocaleString()} kg</td>
        <td>${s.market_name} (${s.district_name})</td>
        <td><code>${s.search_date}</code></td>
        <td><strong style="color: var(--primary-green); font-size: 0.95rem;">${profitText}</strong></td>
        <td>${statusBadge}</td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}
