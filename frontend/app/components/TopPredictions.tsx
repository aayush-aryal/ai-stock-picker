"use client";
import { useEffect, useState } from "react";

type Predictions = {
  score: string;
  percentile: string;
  target_5d: number;
  Ticker: string;
};

type Top15PredictionsResponse = {
  date: string;
  predictions: Predictions[];
};

export default function TopPredictions() {
  const [predictions, setPredictions] = useState<Top15PredictionsResponse>();
  useEffect(() => {
    async function load() {
      const res = await fetch("http://localhost:8000/stock/get-top-15", {
        method: "POST",
      });
      const data = await res.json();
      
      setPredictions(data);
    }

    load();
  }, []);
  if (!predictions){
    return(
      <h1>Loading Predictions for the day!</h1>
    )
  }
  const top5=predictions?.predictions.slice(0,5);
  return (
    
    <div className="mt-6">
      <h2 className="text-xl font-bold mb-4">Top 5 Predicted Stocks For Today</h2>

      {/* Grid layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {top5?.map((pred) => (
          <div
            key={pred.Ticker}
            className="
              bg-white 
              border border-gray-200 
              rounded-xl 
              p-4 
              shadow-sm 
              hover:shadow-md 
              transition
            "
          >
            {/* Ticker */}
            <h2 className="text-lg font-semibold text-gray-800">
              {pred.Ticker}
            </h2>

            {/* Percentile */}
            <p className="text-sm text-gray-500 mt-1">
              Percentile:{" "}
              <span className="font-medium text-gray-700">
                {Number(pred.percentile).toFixed(2)}
              </span>
            </p>

            {/* Prediction */}
            <p className="mt-2 text-gray-700">
              Prediction:{" "}
              <span className={`font-semibold ${pred.target_5d>0?"text-green-500":pred.target_5d<0? "text-red-500":"text-gray-500"}`}>
                { pred.target_5d>0? `▲ ${pred.target_5d.toFixed(2)}`:pred.target_5d<0?`▼ ${pred.target_5d.toFixed(2)}`:`-- ${pred.target_5d.toFixed(2)}`}
              %
              </span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
