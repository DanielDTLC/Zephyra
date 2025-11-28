let currentLat, currentLon, currentCiudad;
let searchTimeout;
const map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

// Detectar ubicación inicial
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(pos => {
    currentLat = pos.coords.latitude;
    currentLon = pos.coords.longitude;
    map.setView([currentLat, currentLon], 10);
    L.marker([currentLat, currentLon]).addTo(map).bindPopup("Tu ubicación").openPopup();
    buscarClima(null, currentLat, currentLon);
  });
}

// ============================================
// AUTOCOMPLETADO EN TIEMPO REAL
// ============================================
const searchInput = document.getElementById("search-input");
const suggestionsBox = document.getElementById("suggestions");

searchInput.addEventListener("input", function(e) {
  const query = e.target.value.trim();
  
  clearTimeout(searchTimeout);
  
  if (query.length < 2) {
    suggestionsBox.classList.remove("show");
    suggestionsBox.innerHTML = "";
    return;
  }
  
  // Debounce: esperar 300ms antes de buscar
  searchTimeout = setTimeout(() => {
    buscarSugerencias(query);
  }, 300);
});

// Cerrar sugerencias al hacer clic fuera
document.addEventListener("click", function(e) {
  if (!e.target.closest(".search-container")) {
    suggestionsBox.classList.remove("show");
  }
});

// Permitir buscar con Enter
searchInput.addEventListener("keypress", function(e) {
  if (e.key === "Enter") {
    suggestionsBox.classList.remove("show");
    buscarClima();
  }
});

// Buscar sugerencias de ciudades usando Nominatim API
async function buscarSugerencias(query) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=20&addressdetails=1`
    );
    
    const data = await res.json();
    
    if (data.length === 0) {
      suggestionsBox.innerHTML = '<div class="suggestion-item" style="cursor: default; color: #999;">❌ No se encontraron resultados</div>';
      suggestionsBox.classList.add("show");
      return;
    }
    
    // Filtrar y priorizar ciudades, pueblos y países
    const filtered = data.filter(item => 
      item.type === 'city' || 
      item.type === 'town' || 
      item.type === 'village' || 
      item.type === 'administrative' ||
      item.type === 'municipality' ||
      item.type === 'state' ||
      item.class === 'place' ||
      item.class === 'boundary'
    );
    
    // Si hay pocos resultados filtrados, usar todos los resultados
    const results = filtered.length > 0 ? filtered : data;
    
    mostrarSugerencias(results.slice(0, 12));
    
  } catch (error) {
    console.error("Error buscando sugerencias:", error);
    suggestionsBox.innerHTML = '<div class="suggestion-item" style="cursor: default; color: #f56565;">⚠️ Error al buscar sugerencias</div>';
    suggestionsBox.classList.add("show");
  }
}

function mostrarSugerencias(items) {
  if (items.length === 0) {
    suggestionsBox.classList.remove("show");
    return;
  }
  
  suggestionsBox.innerHTML = "";
  
  items.forEach(item => {
    const div = document.createElement("div");
    div.className = "suggestion-item";
    
    // Determinar el icono según el tipo
    const icon = item.type === 'city' ? '🏙️' : 
                 item.type === 'town' ? '🏘️' :
                 item.type === 'village' ? '🏡' :
                 item.type === 'state' ? '🗺️' :
                 item.type === 'administrative' ? '🌍' : 
                 item.type === 'municipality' ? '🏛️' : '📍';
    
    // Obtener nombre de la ubicación
    const ciudad = item.address?.city || 
                   item.address?.town || 
                   item.address?.village || 
                   item.address?.municipality ||
                   item.address?.state ||
                   item.name;
    
    // Obtener país y región
    const pais = item.address?.country || '';
    const estado = item.address?.state || '';
    
    // Construir ubicación completa
    let ubicacion = '';
    if (estado && estado !== ciudad && pais) {
      ubicacion = `${estado}, ${pais}`;
    } else if (pais) {
      ubicacion = pais;
    }
    
    div.innerHTML = `
      <span class="icon">${icon}</span>
      <span class="text">${ciudad}</span>
      ${ubicacion ? `<span class="country">${ubicacion}</span>` : ''}
    `;
    
    div.onclick = () => {
      searchInput.value = `${ciudad}${pais ? ', ' + pais : ''}`;
      suggestionsBox.classList.remove("show");
      // Buscar clima automáticamente con las coordenadas
      buscarClima(null, parseFloat(item.lat), parseFloat(item.lon));
    };
    
    suggestionsBox.appendChild(div);
  });
  
  suggestionsBox.classList.add("show");
}

// ============================================
// EFECTOS CLIMÁTICOS ANIMADOS
// ============================================
const weatherEffects = document.getElementById("weather-effects");
let currentEffect = null;

function crearEfectoClimatico(tipoClima) {
  // Limpiar efectos anteriores
  weatherEffects.innerHTML = "";
  const indicator = document.getElementById("effect-indicator");
  
  const clima = tipoClima.toLowerCase();
  
  // Efecto de LLUVIA
  if (clima.includes("lluv") || clima.includes("rain") || clima.includes("drizzle")) {
    for (let i = 0; i < 100; i++) {
      const gota = document.createElement("div");
      gota.className = "rain";
      gota.style.left = Math.random() * 100 + "%";
      gota.style.animationDuration = (Math.random() * 0.5 + 0.5) + "s";
      gota.style.animationDelay = Math.random() * 2 + "s";
      weatherEffects.appendChild(gota);
    }
    currentEffect = "rain";
    indicator.innerHTML = "☔ Efecto de lluvia activado";
    indicator.style.display = "block";
  }
  
  // Efecto de NIEVE
  else if (clima.includes("niev") || clima.includes("snow")) {
    for (let i = 0; i < 50; i++) {
      const copo = document.createElement("div");
      copo.className = "snow";
      copo.style.left = Math.random() * 100 + "%";
      copo.style.width = (Math.random() * 5 + 5) + "px";
      copo.style.height = copo.style.width;
      copo.style.animationDuration = (Math.random() * 3 + 4) + "s";
      copo.style.animationDelay = Math.random() * 3 + "s";
      weatherEffects.appendChild(copo);
    }
    currentEffect = "snow";
    indicator.innerHTML = "❄️ Efecto de nieve activado";
    indicator.style.display = "block";
  }
  
  // Efecto de TORMENTA (Lluvia + Relámpagos)
  else if (clima.includes("tormenta") || clima.includes("storm") || clima.includes("thunder")) {
    // Agregar lluvia intensa
    for (let i = 0; i < 150; i++) {
      const gota = document.createElement("div");
      gota.className = "rain";
      gota.style.left = Math.random() * 100 + "%";
      gota.style.animationDuration = (Math.random() * 0.3 + 0.3) + "s";
      gota.style.animationDelay = Math.random() + "s";
      weatherEffects.appendChild(gota);
    }
    
    // Agregar relámpagos aleatorios
    setInterval(() => {
      if (Math.random() > 0.7) {
        const relampago = document.createElement("div");
        relampago.className = "lightning";
        weatherEffects.appendChild(relampago);
        setTimeout(() => relampago.remove(), 300);
      }
    }, 3000);
    
    currentEffect = "storm";
    indicator.innerHTML = "⚡ Efecto de tormenta activado - ¡Cuidado con los rayos!";
    indicator.style.display = "block";
  }
  
  // Efecto de NUBES
  else if (clima.includes("nublado") || clima.includes("cloud") || clima.includes("overcast")) {
    for (let i = 0; i < 8; i++) {
      const nube = document.createElement("div");
      nube.className = "cloud";
      nube.style.width = (Math.random() * 100 + 80) + "px";
      nube.style.height = (Math.random() * 40 + 40) + "px";
      nube.style.top = (Math.random() * 40) + "%";
      nube.style.left = -(Math.random() * 20) + "%";
      nube.style.animationDuration = (Math.random() * 20 + 30) + "s";
      nube.style.animationDelay = Math.random() * 5 + "s";
      weatherEffects.appendChild(nube);
    }
    currentEffect = "clouds";
    indicator.innerHTML = "☁️ Efecto de nubes activado";
    indicator.style.display = "block";
  }
  
  // Efecto de SOL (Despejado)
  else if (clima.includes("despejado") || clima.includes("clear") || clima.includes("sunny") || clima.includes("sol")) {
    const rayosContainer = document.createElement("div");
    rayosContainer.className = "sun-rays";
    for (let i = 0; i < 8; i++) {
      const rayo = document.createElement("div");
      rayo.className = "sun-ray";
      rayosContainer.appendChild(rayo);
    }
    weatherEffects.appendChild(rayosContainer);
    currentEffect = "sunny";
    indicator.innerHTML = "☀️ Efecto de sol radiante activado";
    indicator.style.display = "block";
  }
  
  // Efecto de NIEBLA
  else if (clima.includes("niebla") || clima.includes("fog") || clima.includes("mist")) {
    for (let i = 0; i < 3; i++) {
      const niebla = document.createElement("div");
      niebla.className = "fog";
      niebla.style.top = (i * 30) + "%";
      niebla.style.animationDelay = (i * 2) + "s";
      weatherEffects.appendChild(niebla);
    }
    currentEffect = "fog";
    indicator.innerHTML = "🌫️ Efecto de niebla activado";
    indicator.style.display = "block";
  }
  
  // Default: limpiar efectos
  else {
    weatherEffects.innerHTML = "";
    currentEffect = null;
    indicator.style.display = "none";
  }
}

// ============================================
// BUSCAR CLIMA
// ============================================
async function buscarClima(query = null, lat = null, lon = null) {
  let body = {};
  
  if (query) {
    body = { query: query.trim(), dias: 7 };
  } else if (lat !== null && lon !== null) {
    body = { lat, lon, dias: 7 };
  } else {
    const input = document.getElementById("search-input").value.trim();
    if (!input) return alert("Ingresa una ciudad o país.");
    body = { query: input, dias: 7 };
  }

  const res = await fetch('/search', {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.error || "Error en la búsqueda.");
    return;
  }
  
  const data = await res.json();
  currentLat = data.lat;
  currentLon = data.lon;
  currentCiudad = data.ciudad;
  
  // ⭐ ACTIVAR EFECTOS CLIMÁTICOS
  crearEfectoClimatico(data.consenso.estado);
  
  map.setView([data.lat, data.lon], 10);
  L.marker([data.lat, data.lon]).addTo(map)
    .bindPopup(`Clima en ${data.ciudad}: ${data.consenso.estado}, ${data.consenso.temperatura}°C`)
    .openPopup();
  
  document.getElementById("ubicacion").innerText = `📍 ${data.ciudad}`;
  document.getElementById("clima-actual").innerHTML = 
    `<strong>Estado:</strong> ${data.consenso.estado} <br><strong>Temperatura:</strong> ${data.consenso.temperatura}°C | <strong>Humedad:</strong> ${data.consenso.humedad}%`;
  
  // Tabla fuentes
  const tbodyFuentes = document.querySelector("#tabla-fuentes tbody");
  tbodyFuentes.innerHTML = "";
  data.lecturas.forEach(l => {
    const fila = `<tr><td>${l.api}</td><td>${l.estado}</td><td>${l.temperatura}</td><td>${l.humedad}</td></tr>`;
    tbodyFuentes.insertAdjacentHTML("beforeend", fila);
  });
  
  // Consenso
  const tbodyCons = document.querySelector("#tabla-consenso tbody");
  tbodyCons.innerHTML = `<tr><td>${data.consenso.estado}</td><td>${data.consenso.temperatura}</td><td>${data.consenso.humedad}</td></tr>`;
  
  // Proyección
  document.getElementById("proyeccion").innerHTML = 
    `🌡️ Temp Prom: ${data.proyeccion.temperatura}°C | 💧 Hum Prom: ${data.proyeccion.humedad}%`;
}

// ============================================
// FAVORITOS
// ============================================
async function guardarFavorito() {
  if (!currentCiudad || !currentLat || !currentLon) return alert("Busca una ubicación primero.");
  const res = await fetch('/favorites', {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ciudad: currentCiudad, lat: currentLat, lon: currentLon})
  });
  if (res.ok) alert("✅ Favorito guardado exitosamente.");
  else alert("❌ Error guardando favorito.");
}

async function obtenerFavoritos() {
  const res = await fetch('/favorites');
  const favs = await res.json();
  const select = document.getElementById("favoritos-list");
  select.innerHTML = "<option>Selecciona un favorito</option>";
  favs.forEach(f => {
    const opt = document.createElement("option");
    opt.value = JSON.stringify({ lat: f.lat, lon: f.lon });
    opt.text = f.ciudad;
    select.appendChild(opt);
  });
  select.style.display = "inline-block";

  select.onchange = async (e) => {
    const value = e.target.value;
    if (!value || value === "Selecciona un favorito") return;

    const { lat, lon } = JSON.parse(value);
    const body = { lat, lon, dias: 7 };

    const res = await fetch('/search', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    if (!res.ok) {
      const err = await res.json();
      alert(err.error || "Error al cargar favorito");
      return;
    }

    const data = await res.json();
    currentLat = data.lat;
    currentLon = data.lon;
    currentCiudad = data.ciudad;

    map.setView([data.lat, data.lon], 10);
    L.marker([data.lat, data.lon]).addTo(map)
      .bindPopup(`Clima en ${data.ciudad}: ${data.consenso.estado}, ${data.consenso.temperatura}°C`)
      .openPopup();

    document.getElementById("ubicacion").innerText = `📍 ${data.ciudad}`;
    document.getElementById("clima-actual").innerHTML = 
      `<strong>Estado:</strong> ${data.consenso.estado} <br><strong>Temperatura:</strong> ${data.consenso.temperatura}°C | <strong>Humedad:</strong> ${data.consenso.humedad}%`;

    const tbodyFuentes = document.querySelector("#tabla-fuentes tbody");
    tbodyFuentes.innerHTML = "";
    data.lecturas.forEach(l => {
      tbodyFuentes.insertAdjacentHTML("beforeend", 
        `<tr><td>${l.api}</td><td>${l.estado}</td><td>${l.temperatura}</td><td>${l.humedad}</td></tr>`
      );
    });

    document.querySelector("#tabla-consenso tbody").innerHTML = 
      `<tr><td>${data.consenso.estado}</td><td>${data.consenso.temperatura}</td><td>${data.consenso.humedad}</td></tr>`;

    document.getElementById("proyeccion").innerHTML = 
      `🌡️ Temp Prom: ${data.proyeccion.temperatura}°C | 💧 Hum Prom: ${data.proyeccion.humedad}%`;
  };
}

// ============================================
// HISTÓRICO
// ============================================
let historicoVisible = false;
let contenidoOriginal = "";

async function verHistorico() {
  const climaActual = document.getElementById("clima-actual");
  
  // Si el histórico está visible, restaurar el contenido original
  if (historicoVisible) {
    climaActual.innerHTML = contenidoOriginal;
    historicoVisible = false;
    return;
  }
  
  const ciudad = currentCiudad || prompt("Ingresa ciudad para histórico:");
  if (!ciudad) return;
  
  // Guardar el contenido original antes de mostrar el histórico
  contenidoOriginal = climaActual.innerHTML;
  
  const res = await fetch(`/historical?ciudad=${ciudad}`);
  const hist = await res.json();
  
  let html = "<h3 style='color: #667eea;'>📈 Histórico de " + ciudad + "</h3>";
  html += "<button onclick='verHistorico()' style='margin: 10px 0; padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;'>❌ Cerrar Histórico</button>";
  html += "<table style='margin-top: 20px;'><thead><tr><th>Fecha</th><th>Temp</th><th>Hum</th><th>Estado</th></tr></thead><tbody>";
  
  hist.forEach(h => {
    html += `<tr><td>${h.fecha}</td><td>${h.temperatura}°C</td><td>${h.humedad}%</td><td>${h.estado}</td></tr>`;
  });
  
  html += "</tbody></table>";
  climaActual.innerHTML = html;
  historicoVisible = true;
}