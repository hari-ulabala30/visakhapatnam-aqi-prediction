const AQI_DATA_URL = "/aqi/dashboard";
let dashboard = null;
let currentRange = 30;
const charts = {};

const $ = (id) => document.getElementById(id);
const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};
const fmt = (v, d = 2) => {
  const n = num(v);
  return n === null ? "—" : n.toFixed(d);
};

function category(aqi){
  const n = num(aqi);
  if(n === null) return "Unknown";
  if(n <= 50) return "Good";
  if(n <= 100) return "Satisfactory";
  if(n <= 200) return "Moderate";
  if(n <= 300) return "Poor";
  if(n <= 400) return "Very Poor";
  return "Severe";
}

function categoryColor(name){
  return {
    "Good":"#36d5ac",
    "Satisfactory":"#b8d64b",
    "Moderate":"#f4c95d",
    "Poor":"#ff9a4a",
    "Very Poor":"#ef6570",
    "Severe":"#7b3155"
  }[name] || "#4c8dff";
}

function baseChartOptions(extra = {}){
  return {
    responsive:true,
    maintainAspectRatio:false,
    interaction:{mode:"index",intersect:false},
    plugins:{
      legend:{labels:{font:{family:"DM Sans",size:9},usePointStyle:true,color:"#7f8ba0"}},
      tooltip:{backgroundColor:"#0d1726",titleFont:{family:"DM Sans"},bodyFont:{family:"DM Sans"},padding:10,cornerRadius:10}
    },
    scales:{
      x:{grid:{display:false},ticks:{font:{family:"DM Sans",size:8},color:"#8a96a8",maxTicksLimit:10}},
      y:{grid:{color:"rgba(145,158,177,.13)"},ticks:{font:{family:"DM Sans",size:8},color:"#8a96a8"}}
    },
    ...extra
  };
}

function destroyChart(name){
  if(charts[name]){charts[name].destroy();delete charts[name];}
}

function safeRows(rows){ return Array.isArray(rows) ? rows : []; }

function renderGauge(aqi){
  const value = Math.max(0,Math.min(500,num(aqi) || 0));
  const ratio = value / 500;
  const arcLength = 283;
  $("gaugeArc").style.strokeDashoffset = String(arcLength * (1-ratio));
  const angle = -90 + ratio * 180;
  const rad = angle * Math.PI / 180;
  const x2 = 120 + 92 * Math.cos(rad);
  const y2 = 145 + 92 * Math.sin(rad);
  $("gaugeNeedle").setAttribute("x2",x2);
  $("gaugeNeedle").setAttribute("y2",y2);
  $("gaugeValue").textContent = Math.round(value);
  $("scaleMarker").style.left = `${Math.min(99,Math.max(1,ratio*100))}%`;
}

function renderCurrent(){
  const c = dashboard.current || {};
  const aqi = num(c.AQI);
  const cat = c.AQI_Category || category(aqi);
  $("heroTitle").textContent = `${fmt(aqi,0)} — ${cat}`;
  $("heroText").textContent = "Current measured AQI calculated from the latest pollutant and weather observations.";
  $("currentDate").textContent = c.date ? new Date(c.date).toLocaleDateString("en-IN",{day:"2-digit",month:"short",year:"numeric"}) : "—";
  $("categoryBadge").textContent = cat;
  $("categoryBadge").style.boxShadow = `inset 0 0 0 1px ${categoryColor(cat)}55`;
  renderGauge(aqi);

  $("pm25").textContent = fmt(c["PM2.5"]);
  $("pm10").textContent = fmt(c["PM10"]);
  $("no2").textContent = fmt(c["NO2"]);
  $("so2").textContent = fmt(c["SO2"]);
  $("temp").textContent = fmt(c.Temperature,1);
  $("humidity").textContent = fmt(c.Humidity,0);

  $("pulseWind").textContent = fmt(c["Wind Speed"],1);
  $("pulseRain").textContent = fmt(c.Rainfall,2);
  $("pulseSolar").textContent = fmt(c["Solar Radiation"],0);
  $("pulseOzone").textContent = fmt(c.Ozone,2);
}

function renderSummary(){
  const s = dashboard.aqi_summary || {};
  const f = dashboard.future_summary || {};
  $("avgAqi").textContent = fmt(s.average_aqi);
  $("maxAqi").textContent = fmt(s.maximum_aqi);
  $("minAqi").textContent = fmt(s.minimum_aqi);
  $("futureAvg").textContent = fmt(f.average);
  $("recordCount").textContent = s.records ?? "—";
}

function renderYears(){
  const select = $("yearSelect");
  const years = dashboard.years || [];
  select.innerHTML = years.map(y=>`<option value="${y}">${y}</option>`).join("");
  if(years.length) select.value = years[years.length-1];
}

function filteredTrend(){
  const rows = safeRows(dashboard.aqi_trend).slice();
  if(currentRange === "all") return rows;
  return rows.slice(-Number(currentRange));
}

function renderAqiTrend(){
  const rows = filteredTrend();
  destroyChart("aqiTrend");
  charts.aqiTrend = new Chart($("aqiTrendChart"),{
    type:"line",
    data:{
      labels:rows.map(r=>new Date(r.date).toLocaleDateString("en-IN",{day:"2-digit",month:"short"})),
      datasets:[{
        label:"AQI",
        data:rows.map(r=>num(r.AQI)),
        borderColor:"#4c8dff",
        backgroundColor:"rgba(76,141,255,.10)",
        fill:true,
        pointRadius:0,
        pointHoverRadius:4,
        tension:.34,
        borderWidth:2.2
      }]
    },
    options:baseChartOptions()
  });
}

function renderCategories(){
  const rows = safeRows(dashboard.category_distribution);
  destroyChart("category");
  charts.category = new Chart($("categoryChart"),{
    type:"doughnut",
    data:{
      labels:rows.map(r=>r.AQI_Category),
      datasets:[{data:rows.map(r=>num(r.Count) || 0),backgroundColor:rows.map(r=>categoryColor(r.AQI_Category)),borderWidth:0,hoverOffset:5}]
    },
    options:{responsive:true,maintainAspectRatio:false,cutout:"70%",plugins:{legend:{position:"bottom",labels:{font:{family:"DM Sans",size:8},usePointStyle:true,color:"#7f8ba0",padding:10}}}}
  });
}

function futureRows(){ return safeRows(dashboard.future); }

function renderFutureMini(){
  const rows = futureRows();
  $("forecastMiniGrid").innerHTML = rows.map((r,i)=>`
    <div class="mini-day ${i===0?'highlight':''}">
      <span class="day">${r.day ?? `Day ${i+1}`}</span>
      <span class="value">${fmt(r.predicted_aqi,0)}</span>
      <span class="cat">${r.category || category(r.predicted_aqi)}</span>
    </div>
  `).join("");
}

function renderAirQuality(){
  const current = dashboard.current || {};
  const summaryRows = safeRows(dashboard.pollutant_summary);
  const currentKeys = ["PM2.5","PM10","NO2","SO2","CO","Ozone"];
  const unit = (name) => name === "CO" ? "mg/m³" : "µg/m³";
  const histMax = Object.fromEntries(summaryRows.map(r=>[r.Pollutant,num(r.Maximum) || 1]));
  $("pollutantCards").innerHTML = currentKeys.map(name=>{
    const value = num(current[name]);
    const max = histMax[name] || Math.max(value || 0,1);
    const width = value === null ? 0 : Math.min(100,(value/max)*100);
    return `<article class="pollutant-card"><div class="pc-top"><span>${name}</span><span>${unit(name)}</span></div><strong>${fmt(value)}</strong><small>Latest observation</small><div class="pc-bar"><span style="width:${width}%"></span></div></article>`;
  }).join("");

  destroyChart("pollutant");
  charts.pollutant = new Chart($("pollutantChart"),{
    type:"bar",
    data:{labels:currentKeys,datasets:[{label:"Current",data:currentKeys.map(k=>num(current[k]) || 0),backgroundColor:["#36d5ac","#4c8dff","#9b7cff","#f4c95d","#ff9a4a","#44c9ea"],borderRadius:8,borderSkipped:false}]},
    options:baseChartOptions({scales:{x:{grid:{display:false},ticks:{color:"#8a96a8"}},y:{beginAtZero:true,grid:{color:"rgba(145,158,177,.13)"},ticks:{color:"#8a96a8"}}}})
  });

  destroyChart("pollutantHistory");
  charts.pollutantHistory = new Chart($("pollutantHistoryChart"),{
    type:"bar",
    data:{labels:summaryRows.map(r=>r.Pollutant),datasets:[{label:"Average",data:summaryRows.map(r=>num(r.Average) || 0),backgroundColor:"rgba(76,141,255,.78)",borderRadius:7}]},
    options:baseChartOptions()
  });

  $("pollutantTable").innerHTML = summaryRows.map(r=>`<tr><td><b>${r.Pollutant}</b></td><td>${fmt(r.Average)}</td><td>${fmt(r.Minimum)}</td><td>${fmt(r.Maximum)}</td></tr>`).join("");
  $("pollutantCount").textContent = `${summaryRows.length} pollutants tracked`;
}

function renderForecast(){
  const rows = futureRows();
  const s = dashboard.future_summary || {};
  const today = num(dashboard.current?.AQI);
  const day1 = num(rows[0]?.predicted_aqi);
  const delta = today !== null && day1 !== null ? day1 - today : null;
  $("forecastHeadline").textContent = `${fmt(s.average)} average AQI`;
  $("forecastSummary").textContent = `Model output for the next ${rows.length || 7} days using the current project forecasting pipeline.`;
  $("futureMax").textContent = fmt(s.maximum);
  $("futureMin").textContent = fmt(s.minimum);
  $("futureMaxDay").textContent = s.highest_day || "—";
  $("futureMinDay").textContent = s.lowest_day || "—";
  $("forecastDelta").textContent = delta === null ? "—" : `${delta >= 0 ? "+" : ""}${delta.toFixed(1)} AQI`;

  destroyChart("future");
  charts.future = new Chart($("futureChart"),{
    type:"line",
    data:{labels:rows.map(r=>r.day),datasets:[{label:"Predicted AQI",data:rows.map(r=>num(r.predicted_aqi)),borderColor:"#36d5ac",backgroundColor:"rgba(54,213,172,.12)",fill:true,tension:.35,pointRadius:5,pointBackgroundColor:"#36d5ac",borderWidth:2.4}]},
    options:baseChartOptions()
  });

  $("predictionGrid").innerHTML = rows.map((r,i)=>`<div class="prediction-card ${i===0?'current-day':''}"><div class="pred-top"><span>${r.day}</span><span>●</span></div><strong>${fmt(r.predicted_aqi,0)}</strong><small>${r.category || category(r.predicted_aqi)}</small></div>`).join("");

  const comp = safeRows(dashboard.historical_future);
  destroyChart("comparison");
  const hist = comp.filter(r=>r.type === "Historical");
  const pred = comp.filter(r=>r.type === "Predicted");
  const labels = comp.map(r=>new Date(r.date).toLocaleDateString("en-IN",{day:"2-digit",month:"short"}));
  charts.comparison = new Chart($("comparisonChart"),{
    type:"line",
    data:{labels,datasets:[
      {label:"Historical",data:hist.map(r=>num(r.AQI)),borderColor:"#4c8dff",pointRadius:0,tension:.3,borderWidth:2.2},
      {label:"Predicted",data:Array(hist.length).fill(null).concat(pred.map(r=>num(r.AQI))),borderColor:"#36d5ac",borderDash:[6,4],pointRadius:3,tension:.3,borderWidth:2.2}
    ]},
    options:baseChartOptions()
  });
}

function getWeatherRows(){
  return safeRows(dashboard.historical);
}

function weatherLabels(rows){
  return rows.map(r=>new Date(r.date).toLocaleDateString("en-IN",{day:"2-digit",month:"short"}));
}

function renderWeather(){
  const c = dashboard.current || {};
  const cards = [
    ["Temperature",fmt(c.Temperature,1)+" °C","Thermal"],
    ["Humidity",fmt(c.Humidity,0)+" %","Moisture"],
    ["Wind Speed",fmt(c["Wind Speed"],1),"Wind"],
    ["Wind Direction",fmt(c["Wind Direction"],0)+"°","Direction"],
    ["Rainfall",fmt(c.Rainfall,2),"Latest"],
    ["Total Rainfall",fmt(c["Total Rainfall"],2),"Accumulated"],
    ["Solar Radiation",fmt(c["Solar Radiation"],0),"Energy"],
    ["Vertical Wind",fmt(c["Vertical Wind Speed"],2),"Wind" ]
  ];
  $("weatherCards").innerHTML = cards.map(x=>`<article class="weather-card"><div class="weather-card-top"><span>${x[0]}</span><span>${x[2]}</span></div><strong>${x[1]}</strong><small>Latest observation</small></article>`).join("");

  const rows = getWeatherRows();
  const labels = weatherLabels(rows);

  destroyChart("temp");
  charts.temp = new Chart($("tempChart"),{type:"line",data:{labels,datasets:[{label:"Temperature °C",data:rows.map(r=>num(r.temp)),borderColor:"#ff9a4a",backgroundColor:"rgba(255,154,74,.10)",fill:true,pointRadius:0,tension:.32,borderWidth:2}]},options:baseChartOptions()});

  destroyChart("humidity");
  charts.humidity = new Chart($("humidityChart"),{type:"line",data:{labels,datasets:[{label:"Humidity %",data:rows.map(r=>num(r.humidity)),borderColor:"#4c8dff",backgroundColor:"rgba(76,141,255,.08)",fill:true,pointRadius:0,tension:.32,borderWidth:2}]},options:baseChartOptions()});

  destroyChart("rain");
  charts.rain = new Chart($("rainChart"),{type:"bar",data:{labels,datasets:[{label:"Rainfall",data:rows.map(r=>num(r.rainfall) || 0),backgroundColor:"rgba(68,201,234,.55)",borderRadius:5}]},options:baseChartOptions()});

  destroyChart("solar");
  charts.solar = new Chart($("solarChart"),{type:"line",data:{labels,datasets:[{label:"Solar Radiation",data:rows.map(r=>num(r.solar_radiation)),borderColor:"#f4c95d",backgroundColor:"rgba(244,201,93,.10)",fill:true,pointRadius:0,tension:.3,borderWidth:2}]},options:baseChartOptions()});
}

function renderInsights(){
  const c = dashboard.current || {};
  const s = dashboard.aqi_summary || {};
  const f = dashboard.future_summary || {};
  const rows = safeRows(dashboard.future);
  const first = num(rows[0]?.predicted_aqi);
  const current = num(c.AQI);
  const change = current !== null && first !== null ? first-current : null;
  const insights = [
    ["✦","Current status","Live observation",`Current AQI is ${fmt(current,0)} and the dashboard classifies it as ${c.AQI_Category || category(current)}.`],
    ["⌁","Forecast outlook","Machine learning",`The seven-day forecast has an average AQI of ${fmt(f.average)} with a range of ${fmt(f.minimum)}–${fmt(f.maximum)}.`],
    ["↗","Near-term movement","Current → Day 1",change === null ? "The first forecast value is not available." : `Day 1 is ${Math.abs(change).toFixed(1)} AQI ${change >= 0 ? "above" : "below"} the current observation.`],
    ["◎","Historical range","Dataset",`Historical AQI spans ${fmt(s.minimum_aqi)} to ${fmt(s.maximum_aqi)} across ${s.records || 0} observations.`],
    ["☁","Weather context","Latest conditions",`The latest observation records ${fmt(c.Temperature,1)} °C, ${fmt(c.Humidity,0)}% humidity and ${fmt(c["Wind Speed"],1)} wind speed.`],
    ["◌","Data story","Project view","Use the current observation for present conditions and the ML series for forward-looking analysis."]
  ];
  $("insightGrid").innerHTML = insights.map(i=>`<article class="insight"><div class="insight-top"><div class="icon">${i[0]}</div><span class="insight-tag">${i[2]}</span></div><h4>${i[1]}</h4><p>${i[3]}</p></article>`).join("");
}

function renderAll(){
  renderCurrent();
  renderSummary();
  renderAqiTrend();
  renderCategories();
  renderFutureMini();
  renderAirQuality();
  renderForecast();
  renderWeather();
  renderInsights();
  $("lastUpdated").textContent = `Updated ${new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}`;
}

async function loadDashboard(url = `${AQI_DATA_URL}?t=${Date.now()}`){
  try{
    $("lastUpdated").textContent = "Refreshing…";
    const response = await fetch(url,{cache:"no-store"});
    if(!response.ok) throw new Error(`AQI backend returned ${response.status}`);
    const data = await response.json();
    if(data.error) throw new Error(data.error);
    dashboard = data;
    renderYears();
    renderAll();
  }catch(err){
    showError(`AQI data connection failed. Start the AQI backend and check /aqi/dashboard. Details: ${err.message}`);
    $("lastUpdated").textContent = "Connection unavailable";
  }
}

function showError(message){
  const box = $("errorBox");
  box.textContent = message;
  box.classList.remove("hidden");
  setTimeout(()=>box.classList.add("hidden"),8000);
}

function switchSection(section){
  document.querySelectorAll(".nav-item").forEach(x=>x.classList.toggle("active",x.dataset.section===section));
  document.querySelectorAll(".page-section").forEach(x=>x.classList.toggle("active-section",x.id===section));
  $("sidebar").classList.remove("open");
  $("mobileBackdrop").classList.remove("show");
  window.scrollTo({top:0,behavior:"smooth"});
}

document.querySelectorAll(".nav-item").forEach(btn=>btn.addEventListener("click",()=>switchSection(btn.dataset.section)));
document.querySelectorAll("[data-jump]").forEach(btn=>btn.addEventListener("click",()=>switchSection(btn.dataset.jump)));

$("refreshBtn").addEventListener("click",()=>loadDashboard());
$("themeBtn").addEventListener("click",()=>document.body.classList.toggle("dark"));
$("menuBtn").addEventListener("click",()=>{$("sidebar").classList.add("open");$("mobileBackdrop").classList.add("show")});
$("closeSidebar").addEventListener("click",()=>{$("sidebar").classList.remove("open");$("mobileBackdrop").classList.remove("show")});
$("mobileBackdrop").addEventListener("click",()=>{$("sidebar").classList.remove("open");$("mobileBackdrop").classList.remove("show")});

$("rangeSwitch").addEventListener("click",(e)=>{
  const btn = e.target.closest("button[data-range]");
  if(!btn) return;
  currentRange = btn.dataset.range === "all" ? "all" : Number(btn.dataset.range);
  document.querySelectorAll("#rangeSwitch button").forEach(x=>x.classList.toggle("active",x===btn));
  renderAqiTrend();
});

$("yearSelect").addEventListener("change",async()=>{
  const year = $("yearSelect").value;
  await loadDashboard(`${AQI_DATA_URL}?year=${encodeURIComponent(year)}&t=${Date.now()}`);
});

loadDashboard();
