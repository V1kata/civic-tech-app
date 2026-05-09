"use client";

import React from "react";

interface Disruption {
  street: string;
  disruption_type: string;
  start_date: string;
  end_date: string;
  scraped_at: string;
}

interface DisruptionPopupProps {
  disruption: Disruption;
}

export function DisruptionPopup({ disruption }: DisruptionPopupProps) {
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="w-64 p-3">
      <h3 className="font-bold text-gray-900 mb-2 text-base">
        {disruption.street}
      </h3>
      
      <div className="space-y-2 text-sm">
        <div>
          <span className="font-semibold text-gray-700">Type:</span>
          <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
            {disruption.disruption_type}
          </span>
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          <div>
            <span className="font-semibold text-gray-700">Start:</span>
            <p className="text-gray-600">{formatDate(disruption.start_date)}</p>
          </div>
          <div>
            <span className="font-semibold text-gray-700">End:</span>
            <p className="text-gray-600">{formatDate(disruption.end_date)}</p>
          </div>
        </div>

        <div className="pt-2 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Updated: {new Date(disruption.scraped_at).toLocaleTimeString()}
          </p>
        </div>
      </div>
    </div>
  );
}
