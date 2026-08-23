import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'

// Delhi-ish default center — reasonable fallback since seed data is Delhi districts.
const DEFAULT_CENTER = [28.6139, 77.209]

function scoreColor(score) {
  if (score >= 80) return '#b4472a' // rust — urgent
  if (score >= 55) return '#e2a32d' // marigold — moderate
  return '#1f6f78' // petrol — lower priority
}

export default function Heatmap({ hotspots }) {
  const center = hotspots.length
    ? [hotspots[0].center_lat, hotspots[0].center_lng]
    : DEFAULT_CENTER

  return (
    <div className="heatmap-wrap">
      <MapContainer center={center} zoom={10} scrollWheelZoom={false} className="heatmap-map">
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {hotspots.map((h) => (
          <CircleMarker
            key={h.cluster_id}
            center={[h.center_lat, h.center_lng]}
            radius={8 + Math.min(h.request_count / 4, 18)}
            pathOptions={{
              color: scoreColor(h.priority_score),
              fillColor: scoreColor(h.priority_score),
              fillOpacity: 0.55,
              weight: 2,
            }}
          >
            <Tooltip direction="top">
              <strong>#{h.rank} · {h.category}</strong>
              <br />
              {h.district} — {h.request_count} reports
              <br />
              Score {h.priority_score}
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
