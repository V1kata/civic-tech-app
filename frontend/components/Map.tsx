"use client";

import React, { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polygon,
  Polyline,
} from "react-leaflet";
import L from "leaflet";
import { Legend } from "./Legend";
import { DisruptionPopup } from "./DisruptionPopup";

// Fix Leaflet icon issue in Next.js
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41],
});

const roadWorksIcon = L.icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const waterIcon = L.icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const powerIcon = L.icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface Disruption {
  id: string;
  street: string;
  description?: string;
  disruption_type: string;
  start_date: string;
  end_date: string;
  latitude: number;
  longitude: number;
  polygon?: number[][][];
  polyline?: number[][];
  scraped_at: string;
}

interface DisruptionResponse {
  timestamp: string;
  count: number;
  disruptions: Disruption[];
}

// Sofia, Bulgaria coordinates
const SOFIA_CENTER: [number, number] = [42.6977, 23.3219];
const DEFAULT_ZOOM = 11;

export default function Map() {
  const [disruptions, setDisruptions] = useState<Disruption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);

  // Fetch disruptions from API
  useEffect(() => {
    const fetchDisruptions = async () => {
      try {
        setLoading(true);
        const response = await fetch("/api/disruptions");
        
        if (!response.ok) {
          throw new Error(`API error: ${response.statusText}`);
        }
        
        const data: DisruptionResponse = await response.json();
        setDisruptions(data.disruptions);
        setError(null);
      } catch (err) {
        console.error("Error fetching disruptions:", err);
        setError("Failed to load disruption data");
        setDisruptions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDisruptions();
    
    // Optionally, refresh data every 5 minutes
    const interval = setInterval(fetchDisruptions, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Filter disruptions by type if selected
  const filteredDisruptions = selectedType
    ? disruptions.filter((d) => d.disruption_type === selectedType)
    : disruptions;

  // Get unique disruption types for legend
  const uniqueTypes = Array.from(
    new Set(disruptions.map((d) => d.disruption_type))
  );

  // Get icon for disruption type
  const getIconForType = (type: string) => {
    if (type.toLowerCase().includes("water")) return waterIcon;
    if (type.toLowerCase().includes("road")) return roadWorksIcon;
    if (type.toLowerCase().includes("power")) return powerIcon;
    return icon;
  };

  // Get color for disruption type (for polygons)
  const getColorForType = (type: string) => {
    if (type.toLowerCase().includes("water")) return "#3b82f6"; // blue-500
    if (type.toLowerCase().includes("road")) return "#ef4444"; // red-500
    if (type.toLowerCase().includes("power")) return "#facc15"; // yellow-400
    return "#3b82f6";
  };

  return (
    <div className="w-full h-full relative pointer-events-none">
      {/* Loading state */}
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center z-20 pointer-events-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-3"></div>
            <p className="text-gray-700">Loading disruptions...</p>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="absolute top-4 left-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-20 pointer-events-auto">
          {error}
        </div>
      )}

      {/* Map */}
      <MapContainer
        center={SOFIA_CENTER}
        zoom={DEFAULT_ZOOM}
        className="w-full h-full pointer-events-auto"
        attributionControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Render markers and polygons for each disruption */}
        {filteredDisruptions.map((disruption) => (
          <React.Fragment key={disruption.id}>
            {!(disruption.polyline && disruption.polyline.length > 0) && (
              <Marker
                position={[disruption.latitude, disruption.longitude]}
                icon={getIconForType(disruption.disruption_type)}
              >
                <Popup>
                  <DisruptionPopup disruption={disruption} />
                </Popup>
              </Marker>
            )}

            {/* Render polygon if available */}
            {disruption.polygon && disruption.polygon.length > 0 && (
              <Polygon
                positions={disruption.polygon as any}
                pathOptions={{ 
                  color: getColorForType(disruption.disruption_type),
                  fillColor: getColorForType(disruption.disruption_type),
                  fillOpacity: 0.4
                }}
              >
                <Popup>
                  <DisruptionPopup disruption={disruption} />
                </Popup>
              </Polygon>
            )}

            {/* Render polyline if available */}
            {disruption.polyline && disruption.polyline.length > 0 && (
              <Polyline
                positions={disruption.polyline as any}
                pathOptions={{ 
                  color: getColorForType(disruption.disruption_type),
                  weight: 5,
                  opacity: 0.8
                }}
              >
                <Popup>
                  <DisruptionPopup disruption={disruption} />
                </Popup>
              </Polyline>
            )}
          </React.Fragment>
        ))}
      </MapContainer>

      {/* Legend and Controls */}
      <Legend
        types={uniqueTypes}
        selectedType={selectedType}
        onTypeChange={setSelectedType}
        totalCount={disruptions.length}
        visibleCount={filteredDisruptions.length}
      />
    </div>
  );
}
