"use client";


interface LegendProps {
  types: string[];
  selectedType: string | null;
  onTypeChange: (type: string | null) => void;
  totalCount: number;
  visibleCount: number;
}

const disruptionColors: Record<string, string> = {
  "Road works": "bg-red-500",
  "Water repair": "bg-blue-500",
  "Sewer repair": "bg-yellow-600",
  "Power outage": "bg-yellow-400",
  "Other": "bg-gray-500",
};

export function Legend({
  types,
  selectedType,
  onTypeChange,
  totalCount,
  visibleCount,
}: LegendProps) {
  const getColorClass = (type: string) => {
    const match = Object.entries(disruptionColors).find(
      ([key]) => type.toLowerCase().includes(key.toLowerCase())
    );
    return match ? match[1] : "bg-gray-500";
  };

  return (
    <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 z-[1000] max-w-xs pointer-events-auto">
      <h2 className="font-bold text-gray-900 mb-3">Disruptions</h2>

      {/* Filter buttons */}
      <div className="space-y-2 mb-4">
        <button
          onClick={() => onTypeChange(null)}
          className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
            selectedType === null
              ? "bg-blue-500 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          All ({totalCount})
        </button>

        {types.map((type) => {
          return (
            <button
              key={type}
              onClick={() => onTypeChange(selectedType === type ? null : type)}
              className={`w-full text-left px-3 py-2 rounded text-sm transition-colors flex items-center gap-2 ${
                selectedType === type
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <span
                className={`w-3 h-3 rounded-full ${getColorClass(type)}`}
              ></span>
              <span className="flex-1">{type}</span>
            </button>
          );
        })}
      </div>

      {/* Stats */}
      <div className="border-t border-gray-200 pt-3 text-xs text-gray-600">
        <p>Showing {visibleCount} of {totalCount} items</p>
      </div>
    </div>
  );
}
