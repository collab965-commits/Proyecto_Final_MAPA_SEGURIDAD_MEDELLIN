// ==============================
// 📍 Mapa de Riesgo Antioquia
// ==============================

// Inicializar mapa
const map = L.map('map').setView([6.25, -75.57], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// ==============================
// 🧾 Cargar datos
// ==============================
fetch("data_final.json")
  .then(response => response.json())
  .then(data => {
    console.log("✅ Datos cargados:", data.length);

    data.forEach(d => {
      if (!d.latitud && !d.longitud) {
        // Si no hay coordenadas, puedes usar un centro predefinido por comuna
        return;
      }

      // Definir color por alerta
      const color = 
        d.alerta === "🚨 Alerta Roja" ? "#d73027" :
        d.alerta === "🟠 Alerta Media" ? "#fc8d59" :
        "#1a9850";

      const circle = L.circleMarker([d.latitud, d.longitud], {
        radius: 10,
        color: color,
        weight: 2,
        fillOpacity: 0.8
      }).addTo(map);

      // ==============================
      // 💬 Popup detallado
      // ==============================
      const popup = `
        <b>${d.sector_norm || "SIN SECTOR"} (${d.municipio_norm || "SIN MUNICIPIO"})</b><br>
        ${d.alerta || ""} — Nivel: ${d.nivel_riesgo || ""}<br><br>

        📊 <b>Promedio de casos mensuales:</b> ${d.promedio_mes ? d.promedio_mes.toFixed(1) : "N/A"}<br>
        🚨 <b>Delito más común:</b> ${d.tipo_delito || "Sin datos"}<br>
        <hr>
        💰 <b>Arriendos promedio:</b><br>
        🏢 Apartamento: $${d.promedio_arriendo_apartamento ? d.promedio_arriendo_apartamento.toLocaleString() : "N/A"}<br>
        🏠 Casa: $${d.promedio_arriendo_casa ? d.promedio_arriendo_casa.toLocaleString() : "N/A"}<br>
        🏪 Local: $${d.promedio_arriendo_local ? d.promedio_arriendo_local.toLocaleString() : "N/A"}<br>
      `;
      circle.bindPopup(popup);
    });
  })
  .catch(error => console.error("❌ Error cargando data_final.json:", error));

// ==============================
// 🧭 Leyenda de interpretación
// ==============================
const legend = L.control({ position: "bottomright" });

legend.onAdd = function(map) {
  const div = L.DomUtil.create("div", "info legend");
  div.innerHTML = `
    <h4>🧭 Niveles de Riesgo</h4>
    <table style="font-size:13px; border-collapse:collapse;">
      <tr><td>💎 Diamante</td><td>0.00–0.20</td><td>🟢 Segura</td></tr>
      <tr><td>🥇 Oro</td><td>0.21–0.40</td><td>🟢 Segura</td></tr>
      <tr><td>🥈 Plata</td><td>0.41–0.60</td><td>🟠 Alerta Media</td></tr>
      <tr><td>🥉 Bronce</td><td>0.61–0.80</td><td>🚨 Alerta Roja</td></tr>
      <tr><td>🧱 Cobre</td><td>0.81–1.00</td><td>🚨 Alerta Roja</td></tr>
    </table>
  `;
  return div;
};

legend.addTo(map);

// ==============================
// 🎨 Estilo CSS adicional sugerido
// ==============================
//
// .info.legend {
//   background: white;
//   padding: 10px;
//   border-radius: 10px;
//   box-shadow: 0 0 10px rgba(0,0,0,0.2);
//   line-height: 1.4em;
// }
// .leaflet-popup-content {
//   font-family: "Inter", sans-serif;
//   font-size: 14px;
//   line-height: 1.5;
// }
// .leaflet-popup-content hr {
//   border: 0;
//   border-top: 1px solid #ccc;
//   margin: 5px 0;
// }
