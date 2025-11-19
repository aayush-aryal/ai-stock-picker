"use client";
import ChartComponent from "@/app/components/Chart";
import StockRagChatUI from "@/app/components/Chat";
import NewsPage from "@/app/components/News";
import StockBuySell from "@/app/components/StockBuySell";
import { useUser } from "@/app/contexts/userContext";
import { StockDaysData } from "@/app/definitions";
import { useEffect, useState } from "react";

type StockInfoType = {
  symbol: string;
  address: string;
  city: string;
  country: string;
  phone: string;
  zip: string;
  industry: string;
  sector: string;
  long_business_summary: string;
  full_time_employees: number;
  web_site: string;
};

type StockInfoResponse = {
  ticker: string;
  info: StockInfoType[];
};

export default function StockInfoPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const [stockInfo, setStockInfo] = useState<StockInfoType | null>(null);
  const { user } = useUser();
  const [lookback, setLookback] = useState(60);
  const [stockXday, setStockXday] = useState<StockDaysData | null>(null);
  const [ticker, setTicker] = useState("");
  const [buyToggle, setBuyToggle] = useState(false);
  useEffect(() => {
    async function loadData() {
      const { ticker } = await params;
      setTicker(ticker.toUpperCase());
      const stockrequest = await fetch(
        `http://localhost:8000/ticker/get-ticker-info?ticker=${ticker}`
      );
      const stockinfo: StockInfoResponse = await stockrequest.json();
      setStockInfo(stockinfo.info[0]);
      const stock_data_resp = await fetch(
        `http://localhost:8000/stock/get-prev-x-day-data?ticker=${ticker}&days=${lookback}`
      );
      const ticker_data: StockDaysData = await stock_data_resp.json();
      setStockXday(ticker_data);
    }
    loadData();
  }, [params, lookback]);

  if (!stockInfo) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-500 text-lg">Loading stock information...</p>
      </div>
    );
  }

  return (
    <>
      <div className="min-h-screen bg-gray-50 p-6">
        {/* Stock Info Card */}
        <div className="bg-white rounded-2xl border border-blue-100 p-6 max-w-4xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
            <h1 className="text-3xl font-bold text-blue-900 mb-2 sm:mb-0">
              {stockInfo.symbol}
            </h1>
            <span className="text-blue-600 text-sm">
              {stockInfo.industry} / {stockInfo.sector}
            </span>
          </div>

          <div className="text-gray-700 space-y-2 mb-6">
            <p className="text-sm">{stockInfo.address}</p>
            <p className="text-sm">
              {stockInfo.city}, {stockInfo.country} {stockInfo.zip}
            </p>
            <p className="text-sm">Phone: {stockInfo.phone}</p>
            {stockInfo.full_time_employees && (
              <p className="text-sm">
                Employees: {stockInfo.full_time_employees.toLocaleString()}
              </p>
            )}
            {stockInfo.web_site && (
              <p className="text-sm">
                Website:{" "}
                <a
                  href={stockInfo.web_site}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {stockInfo.web_site}
                </a>
              </p>
            )}
            <button
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mt-4"
              onClick={() => setBuyToggle(!buyToggle)}
            >
              {!buyToggle ? "Trade" : "Close"}
            </button>
          </div>

          {user && buyToggle && (
            <StockBuySell user={user.username} ticker={ticker} />
          )}

          <div className="mt-6 text-gray-800">
            <h2 className="text-xl font-semibold text-blue-900 mb-3">
              Business Summary
            </h2>
            <p className="text-gray-700 leading-relaxed">
              {stockInfo.long_business_summary}
            </p>
          </div>

          {/* Stock Chart Section */}
          <div className="flex flex-col items-center w-full mt-8">
            {stockXday && (
              <>
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-bold text-blue-900 mb-2">
                    Stock Performance (
                    {lookback < 360
                      ? `${lookback} days`
                      : `${Math.ceil(lookback / 365)} year`}
                    )
                  </h2>
                  <p
                    className={`text-lg font-semibold ${
                      stockXday.data[0].Close >
                      stockXday.data[stockXday.data.length - 1].Close
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {(
                      ((stockXday.data[0].Close -
                        stockXday.data[stockXday.data.length - 1].Close) /
                        stockXday.data[stockXday.data.length - 1].Close) *
                      100
                    ).toFixed(2)}
                    % change
                  </p>
                </div>

                <div className="w-full">
                  <ChartComponent
                    data={stockXday.data.toReversed()}
                    xKey="Date"
                    yKey="Close"
                    yLabel="Value in dollars"
                    key={lookback}
                  />
                </div>

                <div className="mt-6 flex flex-wrap gap-2 justify-center">
                  {[30, 60, 90, 360].map((days) => (
                    <button
                      key={days}
                      onClick={() => setLookback(days)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      {days === 360 ? "1 Year" : `${days} Days`}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        {/* News and Chat Section */}
        <div className="flex flex-col lg:flex-row gap-6 px-6 mt-8">
          <div className="flex-1">
            <NewsPage ticker={ticker} />
          </div>

          {/* Fixed AI Assistant */}
          <div className="w-full lg:w-[380px] sticky top-6 h-fit">
            {ticker && <StockRagChatUI ticker={ticker} />}
          </div>
        </div>
      </div>
    </>
  );
}
