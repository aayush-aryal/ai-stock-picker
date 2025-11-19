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
  if (!predictions) {
    return <h1>Loading Predictions for the day!</h1>;
  }
  const top5 = predictions?.predictions.slice(0, 5);
  return (
    <div className="mt-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {top5?.map((pred) => (
          <div
            key={pred.Ticker}
            className="bg-white border border-blue-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
          >
            {/* Ticker */}
            <h3 className="text-lg font-bold text-blue-800 mb-2">
              {pred.Ticker}
            </h3>

            {/* Percentile */}
            <p className="text-sm text-blue-600 mb-3">
              Percentile:{" "}
              <span className="font-semibold">
                {Number(pred.percentile).toFixed(1)}%
              </span>
            </p>

            {/* Prediction */}
            <p className="text-sm">
              Prediction:{" "}
              <span
                className={`font-semibold ${
                  pred.target_5d > 0
                    ? "text-green-600"
                    : pred.target_5d < 0
                    ? "text-red-600"
                    : "text-blue-600"
                }`}
              >
                {pred.target_5d > 0
                  ? `+${pred.target_5d.toFixed(2)}%`
                  : `${pred.target_5d.toFixed(2)}%`}
              </span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
