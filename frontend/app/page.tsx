"use client";

import dynamic from "next/dynamic";

// Dynamically import the map component to avoid SSR issues with Leaflet
const MapComponent = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => <MapLoadingState />,
});

export default function Home() {
  return (
    <main className="w-full h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-md z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-blue-600">
            Sofia Civic Tech
          </h1>
          <p className="text-gray-600 text-sm">
            Real-time tracking of road repairs and water network outages
          </p>
        </div>
      </header>

      {/* Map Container */}
      <div className="flex-1 relative">
        <MapComponent />
      </div>
    </main>
  );
}

function MapLoadingState() {
  return (
    <div className="w-full h-full flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading map...</p>
      </div>
    </div>
  );
}
